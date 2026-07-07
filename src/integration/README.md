# integration (논리 그룹)

MORAI bridge·UDP·런타임 연동.

| 경로 | 내용 | 상태 |
|------|------|------|
| `scripts/bridge.sh` | roscore + rosbridge (beta_drive 검증) | ✅ |
| `scripts/wait_morai_topic.sh` | MORAI 토픽 대기 | ✅ |
| `scripts/diagnose_morai_bridge.sh` | 연결 진단 | ✅ |
| `config/morai_bridge.env` | Bridge 포트·ROS env | ✅ |
| UDP 전환 | planning 팀 | ⬜ `feature/yuntae-*` |

## 사용법

```bash
./scripts/bridge.sh                    # 터미널 1
./scripts/diagnose_morai_bridge.sh     # 연결 확인
```

MORAI 시뮬 연동 smoke는 담당자가 로컬에서 검증합니다.
