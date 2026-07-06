# 2026 AI·SW Mobility Competition — Autonav Team

**2026 대학생 AI·SW 모빌리티 경진대회** (AI 융합 자율주행 부문) 팀 통합 저장소입니다.

- **GitHub**: [ahnsh03/2026-ai-sw-mobility-competition-autonav](https://github.com/ahnsh03/2026-ai-sw-mobility-competition-autonav)
- **로컬 경로**: `~/projects/2026-ai-sw-mobility-competition`

## 디렉터리 구조

```
2026-ai-sw-mobility-competition/
├── scripts/                   # 온보딩·유틸 스크립트
│   └── clone-external.sh      # external/ 참조 레포 일괄 클론
├── external/                  # 참조용 외부·레거시 저장소 (git 미포함)
│   ├── aim_ws/                # 레거시 팀 ROS catkin 워크스페이스
│   ├── baselines/             # 논문·베이스라인 구현체
│   └── morai/                 # MORAI 공식 예제·SDK
└── docs/                      # 문서·자료 (대용량 PDF는 git 미포함)
    ├── competition/           # 대회 규정, 연구계획서
    ├── papers/                # 논문 PDF·보충자료
    └── courses/               # 강의 자료
```

## 온보딩

```bash
git clone https://github.com/ahnsh03/2026-ai-sw-mobility-competition-autonav.git \
  ~/projects/2026-ai-sw-mobility-competition
cd ~/projects/2026-ai-sw-mobility-competition

# 참조용 external 레포 클론 (aim_ws 포함)
./scripts/clone-external.sh
```

## 저장소

| 경로 | 설명 | 문서 |
|------|------|------|
| [external/aim_ws](./external/aim_ws/) | **레거시** ROS 워크스페이스 (Lattice, LBC, gRPC, Docker) | [README.md](./external/aim_ws/README.md) |
| [external/baselines/carla-roach](./external/baselines/carla-roach/) | Roach(ICCV 2021) CARLA 공식 코드 | [README_TEAM.md](./external/baselines/carla-roach/README_TEAM.md) |
| [external/baselines/morai-roach](./external/baselines/morai-roach/) | Roach MORAI SIM 포팅 | [README.md](./external/baselines/morai-roach/README.md) |
| [external/baselines/LearningByCheating](./external/baselines/LearningByCheating/) | Learning by Cheating 논문 코드 | — |
| [external/morai/MORAI-MGeoModule](./external/morai/MORAI-MGeoModule/) | MORAI MGeo 맵·기하 데이터 | [README_TEAM.md](./external/morai/MORAI-MGeoModule/README_TEAM.md) |
| [external/morai/MORAI-ROS_morai_msgs](./external/morai/MORAI-ROS_morai_msgs/) | MORAI SIM ROS 메시지 | [README_TEAM.md](./external/morai/MORAI-ROS_morai_msgs/README_TEAM.md) |
| [external/morai/MORAI-SensorExample](./external/morai/MORAI-SensorExample/) | MORAI 센서 예제 | [README_TEAM.md](./external/morai/MORAI-SensorExample/README_TEAM.md) |

## HD Map 데이터

K-City 맵은 **`external/aim_ws`** 에 통합되어 있습니다.

| 경로 | 설명 |
|------|------|
| `external/aim_ws/R_KR_PG_KATRI/` | HD Map JSON |
| `external/aim_ws/mgeo_toolkit/data/KATRI/` | 주행 가능 영역 BEV GT |

## 의존 관계 (개략)

```
carla-roach          ← 논문·학습 파이프라인 기준선
      ↓
morai-roach          ← MORAI SIM 포팅 (팀 구현)
      ↓
aim_ws (레거시)      ← Lattice·LBC·gRPC·Docker 통합 실행

MORAI-MGeoModule     ← 맵 포맷 참고
MORAI-ROS_morai_msgs ← ROS msg/srv 정의
MORAI-SensorExample  ← 센서 패턴 학습용
```

## 빠른 시작 (레거시 aim_ws)

```bash
cd ~/projects/2026-ai-sw-mobility-competition/external/aim_ws
./build.sh
```

Docker: [external/aim_ws/docker-noetic/readme.txt](./external/aim_ws/docker-noetic/readme.txt) 참고.

## 팀 워크플로

1. **이 레포** — 대회용 통합·문서·온보딩
2. **external/aim_ws** — 기존 통합 ROS 환경 참조 (개인 레포 작업 후 머지하던 흐름의 베이스)
3. **개인 브랜치/레포** — 기능별 개발 후 PR로 통합

대회 규정: [docs/competition/](./docs/competition/)
