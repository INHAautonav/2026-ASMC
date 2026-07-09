# 2026-ASMC

**2026 대학생 AI·SW 모빌리티 경진대회** (AI 융합 자율주행) 팀 통합 개발 저장소.

| 항목 | 값 |
|------|-----|
| 조직 | [INHAautonav](https://github.com/INHAautonav) |
| 팀원 | 정윤태, 양서준, 이강태, 안승현, 장원태, 손재호 |
| 통합 리드 | 안승현 |
| 상태 | 레거시 이식 완료 (PR #1–#4). 이후는 `feature/*` 개발 |

## 문서 (팀원 필독)

| 문서 | 내용 |
|------|------|
| [docs/collaboration.md](docs/collaboration.md) | **★ 브랜치·PR·충돌 방지 (팀원 필독)** |
| [docs/getting-started.md](docs/getting-started.md) | 클론·첫 빌드 |
| [docs/team-dev-guide.md](docs/team-dev-guide.md) | **팀원별 개발 경로·검증·주의사항** |
| [docs/sim-verification-checklist.md](docs/sim-verification-checklist.md) | MORAI 시뮬 검증 (담당별) |
| [docs/competition-environment.md](docs/competition-environment.md) | 대회 PC·센서·네트워크 규정 |
| [docs/development-environment.md](docs/development-environment.md) | OS, Python 3.8, ROS Noetic, Docker |
| [docs/architecture-overview.md](docs/architecture-overview.md) | 팀 아키텍처·모듈·인터페이스 |
| [docs/git-workflow.md](docs/git-workflow.md) | 브랜치·PR 규칙 |
| [docs/repository-layout.md](docs/repository-layout.md) | 파트별 폴더 격리 |
| [docs/docker-guide.md](docs/docker-guide.md) | 컨테이너 빌드·재생성 |
| [docs/integration-plan.md](docs/integration-plan.md) | 통합 진행 상황 |
| [docs/planning-behavior-handoff.md](docs/planning-behavior-handoff.md) | behavior↔planner↔mpc |
| [docs/morai-msgs-beta-policy.md](docs/morai-msgs-beta-policy.md) | beta_drive 정렬 규약 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 기여 규칙 요약 |

## 빠른 시작

```bash
git clone --recurse-submodules https://github.com/INHAautonav/2026-ASMC.git
cd 2026-ASMC
git checkout main && git pull
git submodule update --init --recursive

xhost +local:docker
./scripts/docker_ros_up.sh build
./scripts/docker_ros_up.sh up
docker exec -it asmc-ros-noetic bash -c './scripts/build_ws.sh'
```

상세: [docs/getting-started.md](docs/getting-started.md)

## 저장소 구조 (요약)

```
2026-ASMC/
├── docs/                      # 팀 문서
├── docker/                    # ros-noetic · perception-train
├── src/
│   ├── behavior_planner/      # planning ✅
│   ├── planner/               # planning ✅
│   ├── mpc_controller/        # planning ✅ (pkg: mpc_node)
│   ├── integration_launch/    # planning ✅
│   ├── learning_by_cheating/  # learning ✅
│   ├── perception/morai_3d_detection/  # perception ✅
│   └── MORAI-ROS_morai_msgs/  # submodule beta_drive
├── tools/
│   ├── aim_scenario_runner/   # scenario ✅
│   └── grpc_inha_univ/        # gRPC ✅
├── scripts/                   # bridge, build, docker
├── mgeo_toolkit/ · R_KR_PG_KATRI/
└── config/morai_bridge.env
```

팀원별 **어느 폴더를 고칠지:** [docs/team-dev-guide.md](docs/team-dev-guide.md)

## 브랜치

- `main` — 안정 (직접 push 금지)
- `feature/<이름>-<기능>` — 일상 개발
- `integrate/<모듈>` — 통합 리드 대규모 이식 (1차 이식 완료)

## 레거시 코드

통합 이전 **분산 GitHub repo**는 읽기 전용 참조용입니다. 새 작업은 **본 repo**에서만 합니다.  
upstream 매핑: [docs/integration-plan.md](docs/integration-plan.md) §4
