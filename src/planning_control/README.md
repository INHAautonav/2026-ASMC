# planning_control (논리 그룹)

판단·제어 파트. **실제 코드는 아래 catkin 패키지**에 있습니다 (이 폴더는 README만).

| 패키지 (`src/`) | 담당 | 상태 |
|-----------------|------|------|
| `behavior_planner/` | 정윤태·양서준 | ✅ planning-v2 (PR #4) |
| `mpc_controller/` (`mpc_node`) | 정윤태·양서준·이강태 | ✅ |
| `planner/` | 이강태 | ✅ |
| `integration_launch/` | 정윤태 | ✅ |

## 수정 범위

- 위 패키지만 수정. 상세 파일: [docs/team-dev-guide.md](../../docs/team-dev-guide.md) §1–3
- 핸드오프: [docs/planning-behavior-handoff.md](../../docs/planning-behavior-handoff.md)
- 시뮬 검증: [docs/sim-verification-checklist.md](../../docs/sim-verification-checklist.md) §1

## 의존성

`morai_msgs` submodule (`beta_drive`), Docker에 `libyaml-cpp-dev` (behavior_planner).

```bash
roslaunch integration_launch integration.launch
```
