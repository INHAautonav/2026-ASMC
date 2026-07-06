# External repositories

팀이 직접 개발·배포하는 **메인 저장소가 아닌** 참조용 클론입니다.  
수정이 필요하면 각 upstream을 따르거나, 팀 통합 워크스페이스로 필요한 부분만 가져옵니다.

클론:

```bash
./scripts/clone-external.sh
```

| 하위 폴더 | 용도 | Upstream |
|-----------|------|----------|
| [aim_ws/](./aim_ws/) | **레거시** 팀 ROS catkin 워크스페이스 (대회 이전 통합본) | [kante2/aim_ws](https://github.com/kante2/aim_ws) |
| [baselines/](./baselines/) | 논문·베이스라인 구현 (carla-roach, morai-roach, LearningByCheating) | — |
| [morai/](./morai/) | MORAI 공식 예제·SDK (MGeo, ROS msgs, SensorExample) | — |

## aim_ws (레거시)

대회 전부터 사용하던 통합 ROS 워크스페이스입니다. Lattice planner, Learning by Cheating, gRPC, Docker 설정이 포함되어 있습니다.

- **역할**: 참조·실행 환경 베이스라인. 개인 브랜치/레포에서 작업한 내용을 여기로 머지하던 흐름이 있었습니다.
- **팀 통합**: 이후 경진대회용 개발은 **이 레포 루트**(`2026-ai-sw-mobility-competition-autonav`)를 기준으로 진행합니다.
- **실행**: [aim_ws/README.md](./aim_ws/README.md), Docker: [aim_ws/docker-noetic/readme.txt](./aim_ws/docker-noetic/readme.txt)

각 저장소의 `README` / `README_TEAM.md`를 먼저 읽으세요.
