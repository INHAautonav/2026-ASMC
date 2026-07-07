# perception (논리 그룹)

인지 파트. **3차 통합 예정.**

| 예정 | 담당 | 출처 |
|------|------|------|
| ROS 센서 노드 (Camera, LiDAR) | 장원태, 손재호 | `aim_ws` `main` |
| 3D detection 학습·추론 | 손재호 | `morai-3d-detection` |
| 시나리오 러너 | 장원태 | `aim_scenario_runner` |

## Docker

ML 학습은 **`docker/perception-train/`** 컨테이너 사용.  
ROS 연동 실험은 **`docker/ros-noetic/`** 와 동일 워크스페이스 마운트.

## 통합 브랜치

`integrate/perception` (예정)
