# perception (논리 그룹)

인지 파트. **3D detection은 `morai_3d_detection/`**, 시나리오는 `tools/` (이 README는 인덱스).

| 경로 | 담당 | 상태 |
|------|------|------|
| `src/perception/morai_3d_detection/` | 손재호 | ✅ PR #3 |
| `tools/aim_scenario_runner/` | 장원태 | ✅ PR #3 |
| `tools/grpc_inha_univ/` | 장원태 | ✅ |
| Camera/LiDAR ROS 레거시 | — | **미이식** |

상세: [docs/team-dev-guide.md](../../docs/team-dev-guide.md) §5–6  
검증: [docs/sim-verification-checklist.md](../../docs/sim-verification-checklist.md) §4–5

## Docker

| 용도 | 이미지 |
|------|--------|
| 학습·추론 | `docker/perception-train/` + `scripts/docker_perception_up.sh` |
| ROS live | `docker/ros-noetic/` + `morai_3d_live.py` |

## 데이터

`dataset/`, `*.pth` → `$ASMC_DATA` / NAS. 노트: `morai_3d_detection/SETUP_NOTES.md`
