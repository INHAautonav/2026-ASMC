#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dataset loader for preprocessed data (pickle format)

사용 방법:
1. 전처리된 pickle 파일 사용: data/Preprocessing/LBC_*.pkl
2. pickle 파일에는 이미 정규화된 데이터 포함:
   - bev_map: (3, 320, 320) 정규화됨 → (3, 256, 256)으로 resize
   - velocity: 0-1 정규화됨
   - target_x, target_y: [-1, 1] 정규화됨
"""

import pickle
import numpy as np
from pathlib import Path
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader


class PreprocessedPADataset(Dataset):
    """
    PyTorch Dataset for preprocessed pickle files
    
    각 샘플은 이미 정규화된 데이터를 포함합니다:
    - bev_map: (3, 320, 320) float32, 값 범위 [0, 1]
    - velocity: float32, 값 범위 [0, 1] (0-30km/h)
    - target_x, target_y: float32, 값 범위 [-1, 1] (±16m)
    """
    
    def __init__(
        self,
        pickle_file,
        split='train',
        train_ratio=0.8,
        num_waypoints=1,
    ):
        """
        Initialize dataset
        
        Args:
            pickle_file: Path to preprocessed pickle file (e.g., data/Preprocessing/LBC_20260331_145605_processed.pkl)
            split: 'train', 'val', or 'all'
            train_ratio: Fraction of data for training (0-1)
            num_waypoints: Number of waypoints to predict (default 4)
        """
        self.pickle_file = Path(pickle_file)
        self.split = split
        self.train_ratio = train_ratio
        self.num_waypoints = num_waypoints
        
        if not self.pickle_file.exists():
            raise FileNotFoundError(f"Pickle file not found: {self.pickle_file}")
        
        # Load preprocessed data
        print(f"📖 로딩 중: {self.pickle_file.name}")
        with open(self.pickle_file, 'rb') as f:
            self.all_samples = pickle.load(f)
        
        print(f"✅ {len(self.all_samples)}개 샘플 로드됨")
        
        # Split into train/val
        self._split_data()
        
        print(f"📊 '{split}' 분할: {len(self.samples)}개 샘플")
    
    def _split_data(self):
        """Split data into train/val sets"""
        total_samples = len(self.all_samples)
        train_size = int(total_samples * self.train_ratio)
        
        if self.split == 'train':
            self.samples = self.all_samples[:train_size]
        elif self.split == 'val':
            self.samples = self.all_samples[train_size:]
        elif self.split == 'all':
            self.samples = self.all_samples
        else:
            raise ValueError(f"Invalid split: {self.split}")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        """Get sample by index"""
        sample = self.samples[idx]
        
        # BEV map: (3, 320, 320) → (3, 256, 256)으로 resize
        bev_map = torch.from_numpy(sample['bev_map'].astype(np.float32))  # (3, 320, 320)
        
        # Bilinear interpolation으로 resize
        bev_map = F.interpolate(
            bev_map.unsqueeze(0),  # (1, 3, 320, 320)
            size=(256, 256),
            mode='bilinear',
            align_corners=False
        ).squeeze(0)  # (3, 256, 256)
        
        # Velocity: scalar float32 [0, 1]
        velocity = torch.tensor(sample['velocity'], dtype=torch.float32).unsqueeze(0)
        
        # Target waypoints: (2,) float32 [-1, 1]
        # Note: PA 모델은 4개의 future waypoints를 예측하지만,
        # 각 시간스탭의 데이터는 1개의 목표점만 가짐
        target_x = torch.tensor(sample['target_x'], dtype=torch.float32)
        target_y = torch.tensor(sample['target_y'], dtype=torch.float32)
        
        # Waypoints: (1, 2) - 현재 목표점만
        waypoints = torch.stack([target_x, target_y]).unsqueeze(0)  # (1, 2)
        
        # 4개 waypoints로 확장 (간단한 방법: 같은 값 반복)
        # 실제로는 시간 시퀀스 데이터를 사용해야 함
        waypoints = waypoints.repeat(self.num_waypoints, 1)  # (4, 2)
        
        return {
            'bev_map': bev_map,        # (3, 256, 256)
            'velocity': velocity,      # (1,)
            'waypoints': waypoints,    # (4, 2)
        }


def create_dataloaders(
    pickle_file,
    batch_size=32,
    num_workers=4,
    train_ratio=0.8,
    num_waypoints=4,
):
    """
    Create train and val dataloaders from pickle file
    
    Args:
        pickle_file: Path to preprocessed pickle file
        batch_size: Batch size
        num_workers: Number of data loading workers
        train_ratio: Fraction of training data
        num_waypoints: Number of waypoints to predict
    
    Returns:
        train_loader, val_loader
    """
    train_dataset = PreprocessedPADataset(
        pickle_file=pickle_file,
        split='train',
        train_ratio=train_ratio,
        num_waypoints=num_waypoints,
    )
    
    val_dataset = PreprocessedPADataset(
        pickle_file=pickle_file,
        split='val',
        train_ratio=train_ratio,
        num_waypoints=num_waypoints,
    )
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )
    
    return train_loader, val_loader


if __name__ == "__main__":
    # Test dataset
    pickle_file = Path("/root/aim_ws/src/learning_by_cheating/data/Preprocessing/LBC_20260331_145605_processed.pkl")
    
    dataset = PreprocessedPADataset(
        pickle_file=pickle_file,
        split='train',
        train_ratio=0.8,
    )
    
    # Check sample
    sample = dataset[0]
    print(f"\n🔍 샘플 정보:")
    print(f"  - BEV map shape: {sample['bev_map'].shape}")
    print(f"  - Velocity shape: {sample['velocity'].shape}")
    print(f"  - Waypoints shape: {sample['waypoints'].shape}")
    print(f"  - BEV map dtype: {sample['bev_map'].dtype}")
    print(f"  - Velocity value: {sample['velocity'].item():.3f}")
