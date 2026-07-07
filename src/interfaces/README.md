# interfaces

팀 공통 인터페이스 정의 (τ, BEV 스펙, 메시지 타입).

## 궤적 τ (초안)

| 필드 | 제안 | 확정 |
|------|------|------|
| 좌표계 | ego-centric 또는 map frame (하나로 통일) | ☐ |
| 표현 | waypoint `(x, y)` × N | ☐ |
| N | 5~10 (LBC: N_STEP=5) | ☐ |
| 시간 간격 | 0.1s (10Hz) | ☐ |
| 속도 프로파일 | MPC에 별도 전달 여부 | ☐ |

## BEV 텐서 (초안)

| 필드 | 제안 | 확정 |
|------|------|------|
| 크기 | 192×192 (LBC 기본) 또는 팀 합의 | ☐ |
| pixels_per_meter | morai-roach 설정과 동일 | ☐ |
| 채널 | road, lane, vehicle, pedestrian, … (GT·pred 동일) | ☐ |
| 원점 | ego vehicle center | ☐ |

## MPC ↔ UDP

| 필드 | 값 |
|------|-----|
| 입력 | τ, current speed, yaw rate |
| 출력 | steering, accel, brake |
| UDP | `Ctrl_cmd`, longi type **1** |

## 로그 레코드 (1 frame)

```yaml
timestamp:
scenario_id:
ego: {x, y, yaw, speed}
sensors: {cameras, lidar, gps, imu}
gt_bev: ...
tau_expert: ...
tau_pa: ...      # optional
command: ...
mpc_cmd: ...
weather: ...
```

## 코드 (예정)

| 항목 | 경로 |
|------|------|
| 메시지 타입 | `asmc_msgs` (예정) |
| privileged 분리 | train/eval 가드 — [CONTRIBUTING.md](../../CONTRIBUTING.md) |

**담당:** 통합 리드(안승현) + planning(τ) + perception(BEV)

인터페이스 변경은 **3파트 합의 후** PR. breaking change 시 `interfaces/CHANGELOG.md` 갱신.
