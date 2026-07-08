# perception (논리 그룹)

인지 파트. **3D detection 학습 코드 통합 완료** (`integrate/scenario-perception`).

| 경로 | 담당 | 출처 |
|------|------|------|
| `src/perception/morai_3d_detection/` | 손재호 | [sonshiny/morai-3d-detection](https://github.com/sonshiny/morai-3d-detection) |
| ROS 센서 노드 (Camera, LiDAR) | 장원태 | `aim_ws` `main` — **미이식** |

## Docker

| 용도 | 이미지 |
|------|--------|
| 학습·추론 | `docker/perception-train/` |
| ROS live 라벨링 | `docker/ros-noetic/` + `morai_3d_live.py` |

```bash
cd src/perception/morai_3d_detection
pip install -r requirements.txt   # 또는 perception-train 컨테이너
```

## 데이터·체크포인트

- `dataset/`, `*.pth` — **git 제외** (NAS·로컬 `$ASMC_DATA`)
- 상세: `morai_3d_detection/SETUP_NOTES.md`

## 시뮬 검증

[docs/sim-verification-checklist.md](../../docs/sim-verification-checklist.md) §5 — **손재호**

## 통합 브랜치

`integrate/scenario-perception`
