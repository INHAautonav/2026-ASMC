# integration (논리 그룹)

ROS↔UDP 브리지, 런치, 배포 진입점. **2차 통합 예정.**

| 예정 | 담당 | 출처 |
|------|------|------|
| MORAI bridge, UDP 어댑터 | 안승현, 정윤태 | `aim_ws` bridge 스크립트 |
| 통합 launch | 전원 | `integration_launch` 확장 |

## 수정 범위

- `src/integration_*` 패키지, `launch/`, `scripts/`
- 대회 배포 경로(UDP `Ctrl_cmd`) 변경 시 **반드시 planning 리뷰**
