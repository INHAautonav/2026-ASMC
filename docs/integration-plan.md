# 통합 계획·진행 상황

> **통합 리드:** 안승현  
> **최종 수정:** 2026-07-07

## 1. 전략

1. **환경·규약·Docker** 통일 (본 문서 시점)
2. **폴더 격리** 후 모듈별 `integrate/*` PR
3. 레거시 분산 repo는 **읽기 전용** 참조 (본 repo에 통합 후)

**하지 않는 것**
- `external/baselines` ASMC 복사
- aim_ws 3브랜치 통째 merge
- `main`에 개인별 전체 복사본
- **26.R1 필드명 그대로 merge** — 이식 PR마다 [beta 정렬](./morai-msgs-beta-policy.md) 선행

## 2. 진행 체크리스트

| 단계 | 내용 | 상태 |
|------|------|------|
| 0 | `docs/`, Docker, `scripts/`, CONTRIBUTING, **beta 정렬 규약** | ✅ |
| 1 | `mpc_ws` → `src/{mpc_controller,planner,integration_launch}` | ✅ |
| 2 | `morai_msgs` submodule (`beta_drive`) | ✅ `integrate/planning-v1` — Docker catkin green |
| 3 | `aim_ws` learning/LBC/bridge | ✅ `integrate/learning` |
| 4 | `aim_scenario_runner` (jang) | ⬜ `integrate/scenario` — LBC 제외 |
| 5 | `morai-3d-detection` (jaeho) | ⬜ `integrate/perception` |
| 6 | `interfaces/` τ·BEV 확정 | ⬜ [architecture-overview.md](./architecture-overview.md) §5 |
| — | jang LBC gRPC multi-TL | ⬜ **추후** D-09 검증 후 판단 (통합 차단 아님) |

## 3. 레거시 → ASMC 매핑

| 출처 (GitHub) | ASMC | 브랜치 |
|---------------|------|--------|
| [yuntae12-sudo/mpc_ws](https://github.com/yuntae12-sudo/mpc_ws) | `src/mpc_controller`, `planner`, `integration_launch` | ✅ main via PR 예정 |
| [kante2/aim_ws](https://github.com/kante2/aim_ws) `va_seunghyun` | learning, integration, mgeo | integrate/learning |
| [kante2/aim_ws](https://github.com/kante2/aim_ws) `jang` | `aim_scenario_runner` | integrate/scenario |
| [kante2/aim_ws](https://github.com/kante2/aim_ws) `ochang` | path logger, run_mpc 흔적 | cherry-pick |
| [sonshiny/morai-3d-detection](https://github.com/sonshiny/morai-3d-detection) | `src/perception/` 학습 코드 | integrate/perception |

## 4. LBC 신호등 — 통합 전 확인 (요약)

| 구분 | va_seunghyun | jang |
|------|--------------|------|
| `morai_adapters.py` | 동일 | 동일 (차용, 미수정) |
| `lbc_bev_collector` | ROS 토픽만 | ROS 토픽만 (save 경로 등 소규모 diff) |
| `lbc_bev_visualizer` | ROS, `ego_facing_only` | **gRPC 폴링** + ROS 병합, scenario 연동 |

**핵심:** jang의 “여러 신호등”은 `morai_adapters` 변경이 아니라 **visualizer의 gRPC `GetTrafficLightInfo` 폴링**(반경 100m, 최대 32개)으로 캐시를 채운 뒤 BEV에 그리는 방식. scenario runner는 기본 `state_source=grpc`, `traffic_light_mode: fast`로 gRPC로 신호를 **강제 설정**하기도 함.

**va가 ego 진행 방향 1그룹 위주인 이유:** `IntscnTL_topic`은 교차로 **phase index**만 제공(신호별 실시간 색 아님). `GetTrafficLightStatus`는 신호별 enum이나 프레임마다 초기화·교차로 단위 갱신이라 **동시 다중 교차로 색 정합**이 ROS만으로는 어렵다는 전제.

**통합 기준선 (확정 2026-07-07):** LBC·학습 GT는 **va_seunghyun**만 이식. jang의 gRPC multi-TL visualizer는 **추후 D-09 검증 후** cherry-pick 여부 판단.

## 5. 미결정 (D-08)

KATRI 확장 맵 레이어를 K-city 2025로 제공받을 수 있는지 **MORAI 디스코드 문의 중** (답변 대기).

| 시나리오 | 대응 |
|----------|------|
| A. 제공됨 | `data/`·MapService를 2025 기준으로 전환 |
| B. 미제공 | KATRI 보조 + 2025 link/node 병행 (현행) |

## 6. 추후 검토 (D-09) LBC 신호등 — jang gRPC

**상태:** 통합 **차단 안 함**. va 기준으로 진행, jang LBC는 별도 검증 후 업데이트 판단.

**질문:** jang의 gRPC multi-TL BEV가 시뮬 실제 색과 일치하는가? 학습용 collector에도 적용할 것인가?

**검증 절차** (`spike/tl-bev-validation`, learning 이식 전)

1. KATRI에서 MORAI 구동, 동일 ego 위치·시각 기준으로 비교
2. **A — va ROS visualizer:** `/IntscnTL_topic`, `/GetTrafficLightStatus`만
3. **B — jang gRPC visualizer:** `state_source=grpc`, scenario runner 미사용(순수 폴링)
4. **C — jang scenario:** `traffic_light_mode: fast` 켜/끔
5. 각 모드에서 BEV 신호등 색 vs 시뮬 3D 뷰·gRPC `GetTrafficLightInfo` 직접 조회
6. 교차로 2개 이상 동시 가시 시 **stale cache·phase vs per-sig color 불일치** 여부 기록

| 결과 | 조치 |
|------|------|
| gRPC 폴링이 ROS보다 정합 | visualizer/scenario에만 반영; collector는 ROS 유지 또는 옵션 플래그 |
| 불일치·stale 확인 | jang multi-TL 미통합; va `ego_facing_only` 유지 |
| fast TL 모드만 불일치 | scenario 디버그 전용으로 문서화, 대회 런타임 비활성 |

**담당 제안:** 안승현(va 기준) + 장원태(jang gRPC) 페어 리뷰, 결과 `docs/` 또는 PR 코멘트에 1페이지 요약.

## 7. 통합 실행 순서

아래 순서대로 **브랜치·PR 단위**로 진행. 각 단계는 `main` merge 전 Docker catkin build 통과가 완료 조건.

| 순서 | 브랜치 | 작업 | 완료 조건 |
|------|--------|------|-----------|
| **0** | — | 문서·Docker·beta 규약 | ✅ |
| **1** | `integrate/planning-v1` | morai_msgs **submodule** 등록, `mpc_params.yaml` 경로 수정, `scripts/build_ws.sh` 검증 | catkin build 전 패키지 green |
| **2** | `integrate/learning` | `va_seunghyun` → `src/learning_by_cheating/` + bridge·mgeo 등 | beta 필드 마이그레이션, LBC collector/viz ROS 기준 |
| **3** | `integrate/scenario` | jang `aim_scenario_runner` → `tools/aim_scenario_runner/` (LBC·gRPC viz **미포함**) | runtime·dataset·PNG git 제외 |
| **4** | `integrate/perception` | `morai-3d-detection` → `src/perception/` (또는 합의 경로) | 학습 Docker smoke |
| **5** | `integrate/interfaces` | τ·BEV·토픽명 합의, `integration_launch` 확장 | architecture §5 반영 |
| **6** | 팀별 `feature/*` | planning UDP, perception 추론 노드 등 | ASMC 위에서 개발 |

**병렬 가능:** 3(scenario)과 4(perception)은 2(learning) 이후 **서로 독립**하면 동시 PR 가능.

**이식하지 않음:** `ochang` 브랜치 통째, `aim_ws/src/main` 레거시, `external/baselines` 복사, jang `lbc_bev_visualizer` gRPC 경로(추후 판단).

## 8. 다음 PR (통합 리드)

1. **`integrate/planning-v1`** — submodule + build green + mpc yaml 경로
2. **`integrate/learning`** — va_seunghyun LBC/bridge (jang LBC 제외)
3. **`integrate/scenario`** — scenario runner only
4. **`integrate/perception`** — 3D detection
5. 팀 리뷰 후 `main` merge
6. planning 팀: UDP 전환 `feature/yuntae-*`
