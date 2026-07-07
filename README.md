# 2026-ASMC

**2026 대학생 AI·SW 모빌리티 경진대회** (AI 융합 자율주행) 팀 통합 개발 저장소.

| 항목 | 값 |
|------|-----|
| 조직 | [INHAautonav](https://github.com/INHAautonav) |
| 팀원 | 정윤태, 양서준, 이강태, 안승현, 장원태, 손재호 |
| 통합 리드 | 안승현 |

## 문서 (팀원 필독)

| 문서 | 내용 |
|------|------|
| [docs/getting-started.md](docs/getting-started.md) | 클론·첫 빌드 |
| [docs/competition-environment.md](docs/competition-environment.md) | 대회 PC·센서·네트워크 규정 |
| [docs/development-environment.md](docs/development-environment.md) | OS, Python 3.8, ROS Noetic, Docker |
| [docs/architecture-overview.md](docs/architecture-overview.md) | 팀 아키텍처·모듈·인터페이스 |
| [docs/git-workflow.md](docs/git-workflow.md) | 브랜치·PR 규칙 |
| [docs/repository-layout.md](docs/repository-layout.md) | 파트별 폴더 격리 |
| [docs/docker-guide.md](docs/docker-guide.md) | 컨테이너 빌드·재생성 |
| [docs/integration-plan.md](docs/integration-plan.md) | 통합 진행 상황 |
| [docs/morai-msgs-beta-policy.md](docs/morai-msgs-beta-policy.md) | beta_drive 정렬 규약 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 기여 규칙 요약 |

## 빠른 시작

```bash
export ASMC="$HOME/projects/2026-ASMC"
git clone https://github.com/INHAautonav/2026-ASMC.git "$ASMC"
cd "$ASMC"

# morai_msgs (최초 1회, submodule 등록 후)
git submodule update --init --recursive

# ROS 개발 컨테이너
xhost +local:docker
./scripts/docker_ros_up.sh build
./scripts/docker_ros_up.sh up
docker exec -it asmc-ros-noetic bash -c './scripts/build_ws.sh'
```

## 저장소 구조 (요약)

```
2026-ASMC/
├── docs/           # 팀 문서
├── docker/         # ros-noetic · perception-train
├── src/            # catkin 패키지
│   ├── mpc_controller/   # planning ✅
│   ├── planner/          # planning ✅
│   ├── integration_launch/
│   ├── learning/         # README (2차 통합)
│   ├── perception/       # README (3차 통합)
│   └── integration/
├── scripts/
└── launch/ config/
```

## 브랜치

- `main` — 안정 (직접 push 금지)
- `feature/<이름>-<기능>` — 일상 개발
- `integrate/<모듈>` — 통합 리드 대규모 이식

## 레거시 코드

통합 전 분산 개발본은 각자 GitHub upstream에 보관됩니다.  
새 작업은 **본 repo**에서 진행합니다. 매핑: [docs/integration-plan.md](docs/integration-plan.md)
