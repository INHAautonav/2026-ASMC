# 기여 가이드 (CONTRIBUTING)

## 빠른 링크

- [docs/collaboration.md](docs/collaboration.md) ← **★ 브랜치·PR·충돌 방지**
- [docs/getting-started.md](docs/getting-started.md)
- [docs/team-dev-guide.md](docs/team-dev-guide.md) ← **팀원별 개발·검증**
- [docs/git-workflow.md](docs/git-workflow.md)
- [docs/repository-layout.md](docs/repository-layout.md)
- [docs/sim-verification-checklist.md](docs/sim-verification-checklist.md)
- [docs/development-environment.md](docs/development-environment.md)
- [docs/morai-msgs-beta-policy.md](docs/morai-msgs-beta-policy.md)

## 필수 규칙

1. **`main`에 직접 push 하지 않습니다.** PR로 merge합니다.
2. **담당 파트 외 `src/`·`tools/` 패키지를 수정하지 않습니다.** (합의·통합 PR 예외) — 경로는 [team-dev-guide.md](docs/team-dev-guide.md)
3. **대용량 파일·데이터·체크포인트를 커밋하지 않습니다.**
4. **privileged 정보(ObjectStatus 등)를 배포/추론 경로에 넣지 않습니다.**
5. **Python 3.8 / ROS Noetic / Ubuntu 20.04** 기준으로 코드·의존성을 맞춥니다.
6. **morai_msgs는 `beta_drive`만** — [morai-msgs-beta-policy.md](docs/morai-msgs-beta-policy.md)
7. **새 작업은 ASMC에서만.** 개인 `aim_ws`/`mpc_ws`에 기능을 쌓지 않습니다.

## PR 전 체크리스트

- [ ] `git checkout main && git pull` 후 `feature/<이름>-…` 생성
- [ ] 담당 경로만 변경 ([team-dev-guide.md](docs/team-dev-guide.md))
- [ ] `./scripts/build_ws.sh` (해당 패키지) 통과
- [ ] ROS/msg 변경 시 [morai-msgs-beta-policy.md](docs/morai-msgs-beta-policy.md)
- [ ] 절대경로(`/home/…`) 없음
- [ ] 커밋 메시지 `feat(scope): …`
- [ ] breaking change 시 `src/interfaces/`·팀 공지
- [ ] [.github/pull_request_template.md](.github/pull_request_template.md) 작성

## 리뷰어

| 파트 | 기본 리뷰어 | GitHub |
|------|-------------|--------|
| planning (`behavior_planner`, `mpc_controller`, `integration_launch`) | 정윤태 · 양서준 | @yuntae12-sudo · @yangseojun |
| Frenet (`planner`) | 이강태 · 정윤태 | @kante2 · @yuntae12-sudo |
| perception (`morai_3d_detection`) | 손재호 | @sonshiny |
| scenario / gRPC (`tools/`) | 장원태 | @wkddnjsxo |
| learning·bridge·docs·docker | 안승현 | @ahnsh03 |

전체 계정표: [docs/collaboration.md §0](docs/collaboration.md#0-팀-github-계정)

## 통합 문의

공통 인터페이스(τ·BEV)·레거시 추가 이식은 **통합 리드(안승현)** 에게 먼저 공유하세요.
