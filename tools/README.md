# tools/

catkin이 아닌 **Python·gRPC·시나리오** 도구.

| 경로 | 담당 | 엔트리 |
|------|------|--------|
| `aim_scenario_runner/` | 장원태 | `run.sh`, `scenario_launcher.py` |
| `grpc_inha_univ/` | 장원태 | `run_mode.sh`, `src/api/morai_sim_client.py` |

설정: `aim_scenario_runner/config/runtime.yaml` (gRPC host)  
가이드: [docs/team-dev-guide.md](../docs/team-dev-guide.md) §5  
검증: [docs/sim-verification-checklist.md](../docs/sim-verification-checklist.md) §4

```bash
./tools/aim_scenario_runner/run.sh
```
