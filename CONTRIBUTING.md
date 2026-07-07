# 기여 가이드 (CONTRIBUTING)

## 빠른 링크

- [docs/getting-started.md](docs/getting-started.md)
- [docs/git-workflow.md](docs/git-workflow.md)
- [docs/repository-layout.md](docs/repository-layout.md)
- [docs/development-environment.md](docs/development-environment.md)
- [docs/morai-msgs-beta-policy.md](docs/morai-msgs-beta-policy.md)

## 필수 규칙

1. **`main`에 직접 push 하지 않습니다.** PR로 merge합니다.
2. **담당 파트 외 `src/` 패키지를 수정하지 않습니다.** (합의·통합 PR 예외)
3. **대용량 파일·데이터·체크포인트를 커밋하지 않습니다.**
4. **privileged 정보(ObjectStatus 등)를 배포/추론 경로에 넣지 않습니다.**
5. **Python 3.8 / ROS Noetic / Ubuntu 20.04** 기준으로 코드·의존성을 맞춥니다.
6. **morai_msgs는 `beta_drive`만** — [morai-msgs-beta-policy.md](docs/morai-msgs-beta-policy.md)

## PR 전 체크리스트

- [ ] `git checkout main && git pull` 후 브랜치 생성
- [ ] 담당 경로만 변경
- [ ] `./scripts/build_ws.sh` (해당 패키지 빌드) 통과
- [ ] ROS/msg 변경 시 [morai-msgs-beta-policy.md](docs/morai-msgs-beta-policy.md) 체크리스트
- [ ] 커밋 메시지 규칙 준수 (`feat(scope): ...`)
- [ ] breaking change 시 `src/interfaces/`·팀 공지

## 리뷰어

| 파트 | 기본 리뷰어 |
|------|-------------|
| planning | 정윤태 |
| perception | 손재호, 장원태 |
| learning·integration | 안승현 |
| docker·repo 구조 | 안승현 |

## 통합 문의

레거시 분산 repo 이식·공통 인터페이스 변경은 **통합 리드(안승현)** 에게 먼저 이슈/디스코드로 공유하세요.
