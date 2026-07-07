# 저장소 레이아웃·파트 격리

## 1. 최상위 구조

```
2026-ASMC/
├── docs/                 # 팀 문서 (본 폴더)
├── docker/
│   ├── ros-noetic/       # ROS catkin 개발
│   └── perception-train/ # PyTorch 학습
├── src/                  # catkin 패키지 (루트에 직접 배치)
├── launch/               # 통합 launch (2차)
├── config/               # 파트별 yaml
├── scripts/              # build, docker 헬퍼
├── CONTRIBUTING.md
└── README.md
```

**Git에 넣지 않음:** `build/`, `devel/`, `data/`, `checkpoints/`, `.bag`

## 2. catkin 패키지 (`src/`)

ROS는 패키지가 **`src/<패키지명>/`** 바로 아래에 있어야 합니다.  
논리 그룹은 `src/<그룹>/README.md`로 문서화합니다.

### planning_control (✅ 1차 통합)

| 패키지 | 경로 | 담당 |
|--------|------|------|
| MPC 노드 | `src/mpc_controller/` | 정윤태, 양서준, 이강태 |
| 플래너 | `src/planner/` | 이강태 |
| 통합 launch | `src/integration_launch/` | 정윤태 |

### learning (⬜ 2차)

| 예정 | 담당 | 레거시 출처 |
|------|------|-------------|
| `learning_by_cheating` | 안승현 | `kante2/aim_ws` `va_seunghyun` 브랜치 |

### perception (⬜ 3차)

| 예정 | 담당 | 레거시 출처 |
|------|------|-------------|
| Camera, LiDAR ROS | 장원태 | `kante2/aim_ws` |
| 3D detection | 손재호 | `sonshiny/morai-3d-detection` |
| scenario runner | 장원태 | `aim_scenario_runner` |

### integration (⬜ 2차)

| 예정 | 담당 |
|------|------|
| bridge, UDP | 안승현, 정윤태 |

### interfaces (⬜ 진행)

| 예정 | 내용 |
|------|------|
| τ, BEV 스펙 | [architecture-overview.md](../docs/architecture-overview.md) §5 |

### 공통 의존성

| 패키지 | 경로 |
|--------|------|
| morai_msgs | `src/MORAI-ROS_morai_msgs` (submodule) |

## 3. 수정 권한 매트릭스

| 경로 | planning | perception | learning/통합 |
|------|----------|------------|---------------|
| `src/mpc_controller/`, `src/planner/` | ✅ 주 | 👀 리뷰 | ❌ |
| `src/perception_*` (예정) | 👀 | ✅ 주 | 👀 |
| `src/learning_*` (예정) | 👀 | 👀 | ✅ 주 |
| `docker/` | 👀 | 👀 | ✅ (리드) |
| `launch/`, `interfaces/` | ✅ 합의 | ✅ 합의 | ✅ 합의 |

## 4. 외부 참조 코드 (본 repo 밖)

| 종류 | 용도 | 규칙 |
|------|------|------|
| 논문 베이스라인 | TransFuser, LBC 등 **참조** | **ASMC에 복사 금지** |
| MORAI 예제 | UDP, msg, Python 튜토리얼 | submodule 또는 별도 clone |
| 레거시 분산 repo | 통합 전 팀원 개별 작업본 | 통합 후 **읽기 전용** 참조 |

MORAI 공식 clone 목록: [competition-environment.md](./competition-environment.md) §8

## 5. 아키텍처 매핑

| 아키텍처 모듈 | ASMC 경로 |
|---------------|-----------|
| Expert / MPC | `src/planner/`, `src/mpc_controller/` |
| SA_perc | `src/perception_*` (예정) |
| SA_plan / LBC | `src/learning_*` (예정) |
| 배포 UDP | `src/integration_*` (예정) |

상세: [architecture-overview.md](./architecture-overview.md)
