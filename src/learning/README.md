# learning (논리 그룹)

학습·로깅·LBC 파이프라인. **va_seunghyun 기준 통합 완료.**

| 패키지/경로 | 담당 | 출처 |
|-------------|------|------|
| `src/learning_by_cheating/` | 안승현 | `aim_ws` `va_seunghyun` |
| `mgeo_toolkit/` | 안승현 | HD map bake (KATRI) |
| `R_KR_PG_KATRI/` | — | MORAI 맵 JSON (신호·차선) |
| `scripts/bridge.sh` | 안승현 | MORAI rosbridge |

## 빠른 시작 (MORAI 연동은 담당자가 시뮬에서 검증)

```bash
# 터미널 1
./scripts/bridge.sh

# 터미널 2 (컨테이너 또는 Noetic 환경)
source devel/setup.bash
./src/learning_by_cheating/scripts/start_lbc_morai.sh
```

## beta_drive 정렬

- `autonomous_driving.py`: `EgoVehicleStatus.wheel_angle`
- `CtrlCmd.steering` publish
- jang gRPC multi-TL visualizer는 **미포함** (추후 검증 후 판단)

## 통합 브랜치

`integrate/learning`
