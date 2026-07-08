# 저장소 레이아웃·파트 격리

> **최종 수정:** 2026-07-08  
> 팀원별 상세 경로·검증: [team-dev-guide.md](./team-dev-guide.md)

## 1. 최상위 구조

```
2026-ASMC/
├── docs/                 # 팀 문서
├── docker/
│   ├── ros-noetic/       # ROS catkin 개발 (+ libyaml-cpp)
│   └── perception-train/ # PyTorch 학습
├── src/                  # catkin 패키지 + 논리 README
├── tools/                # scenario runner, grpc (non-catkin)
├── scripts/              # bridge, build, docker 헬퍼
├── config/               # morai_bridge.env
├── mgeo_toolkit/         # HD map bake
├── R_KR_PG_KATRI/        # 맵 JSON
├── CONTRIBUTING.md
└── README.md
```

**Git에 넣지 않음:** `build/`, `devel/`, `data/`, `checkpoints/`, `.bag`, `*.pth`

## 2. catkin·코드 패키지

ROS 패키지는 **`src/<패키지명>/`** 바로 아래. 논리 그룹은 `src/<그룹>/README.md`만.

### planning_control (✅ PR #1·#4)

| 패키지 | 경로 | 담당 |
|--------|------|------|
| Behavior planner | `src/behavior_planner/` | 정윤태·양서준 |
| MPC (`mpc_node`) | `src/mpc_controller/` | 정윤태·양서준·이강태 |
| Frenet planner | `src/planner/` | 이강태 |
| 통합 launch | `src/integration_launch/` | 정윤태 |

데이터 흐름: [planning-behavior-handoff.md](./planning-behavior-handoff.md)

### learning (✅ PR #2)

| 경로 | 담당 |
|------|------|
| `src/learning_by_cheating/` | 안승현 |
| `scripts/bridge.sh`, `config/morai_bridge.env` | 안승현 |
| `mgeo_toolkit/`, `R_KR_PG_KATRI/` | 안승현 |

### perception · scenario (✅ PR #3)

| 경로 | 담당 |
|------|------|
| `src/perception/morai_3d_detection/` | 손재호 |
| `tools/aim_scenario_runner/` | 장원태 |
| `tools/grpc_inha_univ/` | 장원태 |

### interfaces (⬜ 합의 중)

| 경로 | 내용 |
|------|------|
| `src/interfaces/README.md` | τ·BEV 초안 — [architecture-overview.md](./architecture-overview.md) §5 |

### 공통

| 패키지 | 경로 |
|--------|------|
| morai_msgs | `src/MORAI-ROS_morai_msgs` (submodule, `beta_drive`) |

## 3. 수정 권한 매트릭스

| 경로 | 정윤태 | 양서준 | 이강태 | 안승현 | 장원태 | 손재호 |
|------|--------|--------|--------|--------|--------|--------|
| `src/behavior_planner/` | ✅ | ✅ | 👀 | 👀 | — | — |
| `src/mpc_controller/` | ✅ | ✅ | 👀 | 👀 | — | — |
| `src/planner/` | 👀 | 👀 | ✅ | 👀 | — | — |
| `src/integration_launch/` | ✅ | 👀 | 👀 | 👀 | — | — |
| `src/learning_by_cheating/` | — | — | — | ✅ | — | — |
| `scripts/bridge*` | — | — | — | ✅ | — | — |
| `tools/aim_scenario_runner/` | — | — | — | 👀 | ✅ | 👀 |
| `tools/grpc_inha_univ/` | — | — | — | 👀 | ✅ | — |
| `src/perception/morai_3d_detection/` | — | — | — | 👀 | 👀 | ✅ |
| `docker/` | 👀 | 👀 | 👀 | ✅ | 👀 | ✅ train |
| `docs/` | 👀 | 👀 | 👀 | ✅ | 👀 | 👀 |
| `src/interfaces/` | ✅ 합의 | ✅ 합의 | ✅ 합의 | ✅ 주관 | ✅ 합의 | ✅ 합의 |

✅ 주 수정 · 👀 리뷰·합의 · — 원칙적 미수정

## 4. 외부 참조 (본 repo 밖)

| 종류 | 규칙 |
|------|------|
| `external/team/` | 팀원 upstream clone — **읽기 전용** diff |
| `external/baselines/` | 논문 코드 — **ASMC 복사 금지** |
| `external/morai/` | MORAI 예제 |

## 5. 아키텍처 → 경로

| 모듈 | ASMC 경로 |
|------|-----------|
| Behavior / Frenet / MPC | `src/behavior_planner/`, `planner/`, `mpc_controller/` |
| SA_perc | `src/perception/morai_3d_detection/` |
| SA_plan / LBC | `src/learning_by_cheating/` |
| Scenario / gRPC | `tools/aim_scenario_runner/`, `tools/grpc_inha_univ/` |
| Bridge | `scripts/bridge.sh` (UDP 확장 예정) |

상세 파일명: [team-dev-guide.md](./team-dev-guide.md)
