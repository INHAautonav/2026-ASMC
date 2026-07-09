## Summary

<!-- 무엇을 변경했는지 한 줄 요약 -->

## Git 규약 확인

- [ ] `main`에서 **feature 브랜치**를 생성해 작업했습니다 (`main` 직접 push 아님)
- [ ] PR 전 `git pull origin main` 또는 rebase로 main과 맞췄습니다
- [ ] 개인 `aim_ws` / `mpc_ws` 가 아닌 **2026-ASMC** 에서 작업했습니다

## 담당 파트 (해당 항목만 체크)

- [ ] planning — `behavior_planner/` (정윤태·양서준)
- [ ] planning — `mpc_controller/` (정윤태·양서준)
- [ ] planning — `planner/` (이강태)
- [ ] planning — `integration_launch/` (정윤태)
- [ ] learning — `learning_by_cheating/` (안승현)
- [ ] perception — `perception/morai_3d_detection/` (손재호)
- [ ] scenario — `tools/aim_scenario_runner/` (장원태)
- [ ] gRPC — `tools/grpc_inha_univ/` (장원태)
- [ ] 통합 — `docker/`, `interfaces/`, submodule (통합 리드 only)

## 변경 범위 확인

- [ ] [team-dev-guide.md](../docs/team-dev-guide.md) 담당 경로만 수정했습니다
- [ ] `src/MORAI-ROS_morai_msgs/` submodule을 직접 커밋하지 않았습니다
- [ ] 호스트 절대경로(`/home/…`)를 코드에 넣지 않았습니다
- [ ] 대용량 데이터·체크포인트를 포함하지 않았습니다

## 테스트

- [ ] `./scripts/build_ws.sh` (또는 해당 패키지만) 성공
- [ ] morai_msgs / msg 변경 시 [morai-msgs-beta-policy.md](../docs/morai-msgs-beta-policy.md) 확인
- [ ] (가능 시) [sim-verification-checklist.md](../docs/sim-verification-checklist.md) 해당 § 실행

## Breaking change (해당 시)

- [ ] `src/interfaces/` 또는 토픽/msg 스키마 변경 → 팀 카톡/Notion 공지

## 스크린샷 / 로그 (선택)

<!-- rostopic, MORAI 시뮬, build 로그 등 -->
