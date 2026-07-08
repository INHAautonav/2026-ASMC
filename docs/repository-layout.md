# 저장소 레이아웃·파트 격리

> **최종 수정:** 2026-07-08

## 1. 최상위 구조

```
2026-ASMC/
├── docs/                 # 팀 문서 (본 폴더)
├── docker/
│   ├── ros-noetic/       # ROS catkin 개발
│   └── perception-train/ # PyTorch 학습
├── src/                  # catkin 패키지 (루트에 직접 배치)
├── tools/                # scenario runner, grpc (non-catkin)
├── scripts/              # build, bridge, docker 헬퍼
├── CONTRIBUTING.md
└── README.md
```

**Git에 넣지 않음:** `build/`, `devel/`, `data/`, `checkpoints/`, `.bag`

## 2. catkin 패키지 (`src/`)

ROS는 패키지가 **`src/<패키지명>/`** 바로 아래에 있어야 합니다.  
논리 그룹은 `src/<그룹>/README.md`로 문서화합니다.

### planning_control (✅ v1 merged, 🔄 v2)

| 패키지 | 경로 | 담당 |
|--------|------|------|
| Behavior planner | `src/behavior_planner/` | 정윤태·양서준 (planning-v2) |
| MPC 노드 | `src/mpc_controller/` | 정윤태, 양서준, 이강태 |
| Frenet planner | `src/planner/` | 이강태 |
| 통합 launch | `src/integration_launch/` | 정윤태 |

데이터 흐름: `behavior_planner` → `planner` → `mpc_controller` — [planning-behavior-handoff.md](./planning-behavior-handoff.md)

### learning (✅ merged)

| 패키지/경로 | 담당 | 출처 |
|-------------|------|------|
| `src/learning_by_cheating/` | 안승현 | `aim_ws` `va_seunghyun` |
| `scripts/bridge.sh`, `mgeo_toolkit/` | 안승현 | 동일 |

### perception (✅ merged)

| 경로 | 담당 | 출처 |
|------|------|------|
| `src/perception/morai_3d_detection/` | 손재호 | `morai-3d-detection` |
| `tools/aim_scenario_runner/` | 장원태 | `aim_ws` `jang` |
| `tools/grpc_inha_univ/` | 장원태 | 동일 |

### integration (⬜ 진행)

| 예정 | 담당 |
|------|------|
| bridge UDP, τ·BEV | 안승현, 정윤태 |

### interfaces (⬜ 진행)

| 예정 | 내용 |
|------|------|
| τ, BEV 스펙 | [architecture-overview.md](./architecture-overview.md) §5 |

### 공통 의존성

| 패키지 | 경로 |
|--------|------|
| morai_msgs | `src/MORAI-ROS_morai_msgs` (submodule, `beta_drive`) |

## 3. 수정 권한 매트릭스

| 경로 | planning | perception | learning/통합 |
|------|----------|------------|---------------|
| `src/behavior_planner/`, `mpc_controller/`, `planner/` | ✅ 주 | 👀 리뷰 | ❌ |
| `src/perception/`, `tools/aim_scenario_runner/` | 👀 | ✅ 주 | 👀 |
| `src/learning_by_cheating/`, `scripts/bridge*` | 👀 | 👀 | ✅ 주 |
| `docker/` | 👀 | 👀 | ✅ (리드) |
| `integration_launch/`, `interfaces/` | ✅ 합의 | ✅ 합의 | ✅ 합의 |

## 4. 외부 참조 코드 (본 repo 밖)

| 종류 | 용도 | 규칙 |
|------|------|------|
| `external/team/` | 팀원 분산 repo clone | 통합 후 **읽기 전용** diff |
| `external/baselines/` | 논문 베이스라인 | **ASMC에 복사 금지** |
| `external/morai/` | MORAI 예제 | submodule 또는 별도 clone |

MORAI 공식 clone 목록: [competition-environment.md](./competition-environment.md) §8

## 5. 아키텍처 매핑

| 아키텍처 모듈 | ASMC 경로 |
|---------------|-----------|
| Behavior / Expert | `src/behavior_planner/`, `src/planner/`, `src/mpc_controller/` |
| SA_perc | `src/perception/morai_3d_detection/` |
| SA_plan / LBC | `src/learning_by_cheating/` |
| Scenario / gRPC | `tools/aim_scenario_runner/`, `tools/grpc_inha_univ/` |
| 배포 UDP | `scripts/bridge.sh` (확장 예정) |

상세: [architecture-overview.md](./architecture-overview.md)
