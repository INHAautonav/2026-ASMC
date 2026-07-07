# planning_control (논리 그룹)

판단·제어 파트 코드. **물리 경로는 `src/` 루트의 catkin 패키지**입니다.

| 패키지 (`src/`) | 담당 | 상태 |
|-----------------|------|------|
| `mpc_controller/` | 정윤태, 양서준, 이강태 | ✅ 1차 통합 (`mpc_ws`) |
| `planner/` | 이강태 | ✅ 1차 통합 |
| `integration_launch/` | 정윤태 | ✅ 1차 통합 |

## 수정 범위

- 이 그룹 패키지와 `launch/`, `config/planning/`만 수정
- `src/learning/`, `src/perception/` 직접 수정 시 PR에 planning 담당 리뷰어 태그

## 의존성

`morai_msgs`는 `src/MORAI-ROS_morai_msgs` (submodule, `beta_drive`) 필요.  
설정: [docs/development-environment.md](../docs/development-environment.md)
