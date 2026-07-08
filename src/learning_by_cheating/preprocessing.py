#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
데이터 전처리 스크립트
CSV (제어 데이터) + NPZ (BEV 맵)를 결합하여 오프라인 학습 데이터셋 생성
"""

import os
import csv
import json
import numpy as np
from pathlib import Path
from collections import defaultdict
import pickle
from tqdm import tqdm

_LBC_ROOT = Path(__file__).resolve().parent


class DataPreprocessor:
    """데이터 전처리 클래스"""
    
    def __init__(
        self,
        data_root=None,
        dataset_name=None,  # LBC_20260331_144448 같은 폴더명
        output_root=None,
        max_timestamp_diff=0.5,  # NPZ와 CSV 매칭 시 최대 시간 차이 (초)
        velocity_scale=30.0,      # 최대 속도 (km/h)
        normalize=True,
    ):
        """
        초기화
        
        Args:
            data_root: 원본 데이터 루트 (raw/, bev_map/ 포함)
            dataset_name: 데이터셋 폴더명 (예: LBC_20260331_144448)
                         None이면 COMMON_TIMESTAMP 환경변수 또는 최신 폴더 자동 선택
            output_root: 전처리 데이터 저장 경로
            max_timestamp_diff: 타임스탐프 매칭 허용 범위 (초)
            velocity_scale: 속도 정규화 기준값
            normalize: 데이터 정규화 여부
        """
        if data_root is None:
            data_root = _LBC_ROOT / "data"
        self.data_root = Path(data_root)
        
        # 데이터셋 폴더명 결정
        if dataset_name is None:
            # 환경변수에서 읽기
            dataset_name = os.getenv('COMMON_TIMESTAMP')
        
        if dataset_name is None:
            # 가장 최근 폴더 찾기
            dataset_name = self._find_latest_dataset()
            if dataset_name is None:
                raise ValueError(f"데이터셋을 찾을 수 없습니다. --dataset_name을 지정해주세요.\n"
                               f"사용 가능한 경로: {self.data_root}/raw/LBC_*")
            print(f"ℹ️  가장 최근 데이터셋 사용: {dataset_name}")
        
        print(f"📂 데이터셋: {dataset_name}")
        self.dataset_name = dataset_name
        self.raw_dir = self.data_root / "raw" / dataset_name
        self.bev_dir = self.data_root / "bev_map" / dataset_name
        
        # 디렉토리 존재 확인
        if not self.raw_dir.exists():
            raise FileNotFoundError(f"CSV 폴더를 찾을 수 없습니다: {self.raw_dir}")
        
        # BEV 폴더가 없으면 "default" 제거해서 찾기
        if not self.bev_dir.exists():
            if "default" in dataset_name:
                alternate_name = dataset_name.replace("LBC_default_", "LBC_")
                alternate_bev_dir = self.data_root / "bev_map" / alternate_name
                if alternate_bev_dir.exists():
                    print(f"ℹ️  BEV 폴더명 변환: {dataset_name} → {alternate_name}")
                    self.bev_dir = alternate_bev_dir
                else:
                    raise FileNotFoundError(f"BEV 폴더를 찾을 수 없습니다: {self.bev_dir} 또는 {alternate_bev_dir}")
            else:
                raise FileNotFoundError(f"BEV 폴더를 찾을 수 없습니다: {self.bev_dir}")
        
        self.output_root = Path(output_root or self.data_root / "Preprocessing")
        
        self.max_timestamp_diff = max_timestamp_diff
        self.velocity_scale = velocity_scale
        self.normalize = normalize
        
        # 통계 정보
        self.stats = {
            'total_matched': 0,
            'total_csv_rows': 0,
            'total_npz_files': 0,
            'unmatched_csv': 0,
            'unmatched_npz': 0,
            'scenarios': defaultdict(int),
        }
        
        # 디렉토리 생성
        self.output_root.mkdir(parents=True, exist_ok=True)
        
        print(f"[Preprocessor] 초기화 완료")
        print(f"  - CSV 경로: {self.raw_dir}")
        print(f"  - BEV 경로: {self.bev_dir}")
        print(f"  - 출력 경로: {self.output_root}")
    
    def _find_latest_dataset(self):
        """가장 최근 데이터셋 폴더 찾기"""
        raw_path = self.data_root / "raw"
        if not raw_path.exists():
            return None
        
        # LBC_로 시작하는 폴더 찾기
        datasets = sorted([d.name for d in raw_path.iterdir() if d.is_dir() and d.name.startswith('LBC_')])
        return datasets[-1] if datasets else None
    
    def preprocess(self):
        """전체 전처리 실행"""
        print("\n" + "="*70)
        print("데이터 전처리 시작")
        print("="*70)
        
        # Step 1: 데이터 로드 및 매칭
        print("\n[Step 1/4] 데이터 로드 및 매칭 중...")
        matched_samples = self._load_and_match_data()
        
        if len(matched_samples) == 0:
            print("[ERROR] 매칭된 데이터가 없습니다!")
            return False
        
        print(f"✅ {len(matched_samples)}개 샘플 매칭 완료")
        
        # Step 2: 데이터 정규화
        print("\n[Step 2/4] 데이터 정규화 중...")
        processed_samples = self._normalize_data(matched_samples)
        
        # Step 3: 데이터 검증
        print("\n[Step 3/4] 데이터 검증 중...")
        valid_samples = self._validate_data(processed_samples)
        print(f"✅ {len(valid_samples)}개 샘플 검증 완료")
        
        if len(valid_samples) == 0:
            print("[ERROR] 검증된 데이터가 없습니다!")
            return False
        
        # Step 4: 데이터 저장
        print("\n[Step 4/4] 전처리 데이터 저장 중...")
        self._save_data(valid_samples)
        
        # 통계 출력
        self._print_statistics(len(matched_samples), len(valid_samples))
        
        return True
    
    def _load_and_match_data(self):
        """CSV와 NPZ 데이터 로드 및 타임스탐프 매칭"""
        matched_samples = []
        
        # CSV 파일 찾기 (raw_dir 바로 안에 있음)
        csv_files = sorted(self.raw_dir.glob("run_*.csv"))
        
        if not csv_files:
            print(f"⚠️  CSV 파일 없음: {self.raw_dir}")
            return matched_samples
        
        # NPZ 파일 로드 (타임스탐프 → 파일 경로 매핑)
        npz_files = sorted(self.bev_dir.glob("*.npz"))
        npz_dict = {}
        npz_timestamps = []
        
        for npz_file in npz_files:
            try:
                timestamp = float(npz_file.stem)
                npz_dict[timestamp] = npz_file
                npz_timestamps.append(timestamp)
            except ValueError:
                continue
        
        if not npz_dict:
            print(f"⚠️  NPZ 파일 없음: {self.bev_dir}")
            return matched_samples
        
        print(f"\n📊 데이터 정보:")
        print(f"    NPZ 파일: {len(npz_dict)}개 ({min(npz_timestamps):.1f} ~ {max(npz_timestamps):.1f})")
        
        # CSV 파일 처리
        for csv_file in csv_files:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            # 유효한 행만 필터링
            valid_rows = [(idx, row) for idx, row in enumerate(rows) if row.get('timestamp', '').strip()]
            
            self.stats['total_csv_rows'] += len(valid_rows)
            
            csv_timestamps = []
            matched_count = 0
            unmatched_count = 0
            
            # 각 CSV 행과 NPZ 매칭
            for row_idx, row in valid_rows:
                try:
                    csv_timestamp = float(row['timestamp'])
                    csv_timestamps.append(csv_timestamp)
                    
                    # 가장 가까운 NPZ 타임스탐프 찾기
                    closest_ts = self._find_closest_timestamp(
                        csv_timestamp, 
                        npz_timestamps
                    )
                    
                    if closest_ts is None:
                        unmatched_count += 1
                        continue
                    
                    # 샘플 생성
                    sample = {
                        'scenario': self.bev_dir.name,  # NPZ 폴더명 사용
                        'csv_timestamp': csv_timestamp,
                        'npz_timestamp': closest_ts,
                        'csv_path': str(csv_file),
                        'npz_path': str(npz_dict[closest_ts]),
                        'time_diff': abs(csv_timestamp - closest_ts),
                        'row_idx': row_idx,
                        'csv_data': row,
                    }
                    
                    matched_samples.append(sample)
                    matched_count += 1
                    self.stats['total_matched'] += 1
                    self.stats['scenarios'][self.bev_dir.name] += 1
                
                except (ValueError, KeyError) as e:
                    unmatched_count += 1
                    continue
            
            if valid_rows:
                print(f"    CSV {csv_file.name}: {matched_count}/{len(valid_rows)} 매칭 "
                      f"({csv_timestamps[0]:.1f} ~ {csv_timestamps[-1]:.1f})")
        
        self.stats['total_npz_files'] += len(npz_files)
        
        return matched_samples
    
    def _find_closest_timestamp(self, target_ts, available_ts, max_diff=None):
        """가장 가까운 타임스탐프 찾기"""
        if max_diff is None:
            max_diff = self.max_timestamp_diff
        
        available_ts = list(available_ts)
        if not available_ts:
            return None
        
        closest = min(available_ts, key=lambda ts: abs(ts - target_ts))
        
        if abs(closest - target_ts) <= max_diff:
            return closest
        
        return None
    
    def _normalize_data(self, matched_samples):
        """데이터 정규화"""
        processed_samples = []
        
        for sample in tqdm(matched_samples, desc="정규화 중"):
            try:
                # NPZ 로드
                npz_data = np.load(sample['npz_path'])
                # LBC 7-channel (LearningByCheating) or legacy 3-channel BEV
                bev_map = npz_data['bev_map'].astype(np.float32)
                
                # CSV 데이터 추출
                csv_data = sample['csv_data']
                ego_vel = float(csv_data.get('ego_vel', 0.0))
                target_x = float(csv_data.get('target_local_path_x', 0.0))
                target_y = float(csv_data.get('target_local_path_y', 0.0))
                ego_x = float(csv_data.get('ego_x', 0.0))
                ego_y = float(csv_data.get('ego_y', 0.0))
                ego_yaw = float(csv_data.get('ego_yaw', 0.0))
                
                # 정규화
                if self.normalize:
                    n_ch = bev_map.shape[-1] if bev_map.ndim == 3 else bev_map.shape[0]
                    max_val = float(np.max(bev_map)) if bev_map.size else 0.0
                    if n_ch == 7 or max_val > 1.5:
                        bev_map = np.clip(bev_map / 255.0, 0.0, 1.0)
                    else:
                        bev_map = np.clip(bev_map / 100.0, 0.0, 1.0)
                    
                    # 속도: km/h → 0-1 정규화
                    velocity_norm = ego_vel / self.velocity_scale
                    velocity_norm = np.clip(velocity_norm, 0.0, 1.0)
                    
                    # 좌표: ±16m → -1~1 정규화
                    target_x_norm = np.clip(target_x / 16.0, -1.0, 1.0)
                    target_y_norm = np.clip(target_y / 16.0, -1.0, 1.0)
                else:
                    velocity_norm = ego_vel
                    target_x_norm = target_x
                    target_y_norm = target_y
                
                if bev_map.ndim == 3:
                    bev_map_chw = np.transpose(bev_map, (2, 0, 1))
                else:
                    bev_map_chw = bev_map
                
                # 처리된 샘플
                processed_sample = {
                    'scenario': sample['scenario'],
                    'timestamp': sample['csv_timestamp'],
                    'bev_map': bev_map_chw,              # (3, H, W)
                    'velocity': float(velocity_norm),     # scalar
                    'target_x': float(target_x_norm),     # scalar
                    'target_y': float(target_y_norm),     # scalar
                    'ego_x': float(ego_x),
                    'ego_y': float(ego_y),
                    'ego_yaw': float(ego_yaw),
                    'raw_velocity': float(ego_vel),
                    'raw_target_x': float(target_x),
                    'raw_target_y': float(target_y),
                }
                
                processed_samples.append(processed_sample)
            
            except Exception as e:
                print(f"⚠️  샘플 처리 실패: {e}")
                continue
        
        return processed_samples
    
    def _validate_data(self, processed_samples):
        """데이터 검증"""
        valid_samples = []
        
        for sample in processed_samples:
            try:
                # BEV 맵 검증 (LBC 7ch teacher or legacy 3ch)
                shape = sample['bev_map'].shape
                valid_shapes = ((3, 256, 256), (3, 320, 320), (7, 256, 256), (7, 320, 320), (7, 192, 192))
                assert shape in valid_shapes, f"BEV 맵 크기 오류: {shape}"
                
                # 값 범위 검증
                assert np.isfinite(sample['bev_map']).all(), "BEV 맵에 NaN/Inf 존재"
                assert 0.0 <= sample['velocity'] <= 1.0, f"속도 범위 오류: {sample['velocity']}"
                assert -1.0 <= sample['target_x'] <= 1.0, f"target_x 범위 오류: {sample['target_x']}"
                assert -1.0 <= sample['target_y'] <= 1.0, f"target_y 범위 오류: {sample['target_y']}"
                
                valid_samples.append(sample)
            
            except AssertionError as e:
                print(f"⚠️  검증 실패: {e}")
                continue
        
        return valid_samples
    
    def _save_data(self, samples):
        """전처리 데이터 저장"""
        # 시나리오별로 분리
        samples_by_scenario = defaultdict(list)
        for sample in samples:
            samples_by_scenario[sample['scenario']].append(sample)
        
        # 각 시나리오별 저장
        for scenario, scenario_samples in samples_by_scenario.items():
            # Pickle로 저장
            output_file = self.output_root / f"{scenario}_processed.pkl"
            with open(output_file, 'wb') as f:
                pickle.dump(scenario_samples, f)
            
            print(f"✅ 저장됨: {output_file} ({len(scenario_samples)}개 샘플)")
        
        # 전체 메타데이터 저장 (샘플 개수만 저장, 배열은 제외)
        metadata = {
            'total_samples': len(samples),
            'scenarios_count': {name: len(data) for name, data in samples_by_scenario.items()},
            'parameters': {
                'max_timestamp_diff': self.max_timestamp_diff,
                'velocity_scale': self.velocity_scale,
                'normalize': self.normalize,
            },
            'stats': {
                'total_csv_rows': self.stats['total_csv_rows'],
                'total_npz_files': self.stats['total_npz_files'],
                'total_matched': self.stats['total_matched'],
                'unmatched_csv': self.stats['unmatched_csv'],
                'unmatched_npz': self.stats['unmatched_npz'],
                'scenarios': {name: count for name, count in self.stats['scenarios'].items()},
            },
        }
        
        metadata_file = self.output_root / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ 메타데이터 저장됨: {metadata_file}")
    
    def _print_statistics(self, total_matched, total_valid):
        """통계 출력"""
        print("\n" + "="*70)
        print("전처리 완료 - 통계")
        print("="*70)
        print(f"총 CSV 행: {self.stats['total_csv_rows']}")
        print(f"총 NPZ 파일: {self.stats['total_npz_files']}")
        print(f"매칭된 샘플: {total_matched}")
        print(f"검증된 샘플: {total_valid}")
        print(f"불일치 CSV: {self.stats['unmatched_csv']}")
        print(f"불일치 NPZ: {self.stats['unmatched_npz']}")
        print(f"\n시나리오별:")
        for scenario, count in self.stats['scenarios'].items():
            print(f"  - {scenario}: {count}개")
        print("="*70 + "\n")


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="데이터 전처리: CSV + NPZ 병합")
    parser.add_argument(
        '--data_root',
        type=str,
        default=str(_LBC_ROOT / 'data'),
        help='원본 데이터 루트 경로'
    )
    parser.add_argument(
        '--dataset_name',
        type=str,
        default=None,
        help='데이터셋 폴더명 (예: LBC_20260331_144448)\n'
             'None이면 COMMON_TIMESTAMP 환경변수 또는 최신 폴더 자동 선택'
    )
    parser.add_argument(
        '--output_root',
        type=str,
        default=None,
        help='전처리 데이터 저장 경로 (기본: data/Preprocessing)'
    )
    parser.add_argument(
        '--velocity_scale',
        type=float,
        default=30.0,
        help='속도 정규화 기준값 (km/h)'
    )
    parser.add_argument(
        '--max_timestamp_diff',
        type=float,
        default=0.5,
        help='타임스탐프 매칭 허용 범위 (초)'
    )
    parser.add_argument(
        '--normalize',
        type=bool,
        default=True,
        help='데이터 정규화 여부'
    )
    
    args = parser.parse_args()
    
    # 전처리 실행
    preprocessor = DataPreprocessor(
        data_root=args.data_root,
        dataset_name=args.dataset_name,
        output_root=args.output_root,
        max_timestamp_diff=args.max_timestamp_diff,
        velocity_scale=args.velocity_scale,
        normalize=args.normalize,
    )
    
    success = preprocessor.preprocess()
    
    if success:
        print("\n✅ 전처리 완료!")
        print(f"저장 위치: {preprocessor.output_root}")
    else:
        print("\n❌ 전처리 실패!")
        exit(1)


if __name__ == '__main__':
    main()
