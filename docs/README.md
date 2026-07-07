# 2026-ASMC 팀 문서

> **대상:** 팀원 전원  
> **통합 리드:** 안승현  
> **최종 수정:** 2026-07-07

## 읽는 순서

1. [getting-started.md](./getting-started.md) — 클론·첫 실행
2. [competition-environment.md](./competition-environment.md) — **대회 PC·센서·네트워크 규정**
3. [development-environment.md](./development-environment.md) — OS, Python, ROS, Docker 표준
4. [architecture-overview.md](./architecture-overview.md) — 팀 아키텍처·모듈·인터페이스
5. [git-workflow.md](./git-workflow.md) — 브랜치·PR·커밋 규칙
6. [repository-layout.md](./repository-layout.md) — 폴더·파트 격리
7. [docker-guide.md](./docker-guide.md) — 컨테이너 빌드·재생성
8. [integration-plan.md](./integration-plan.md) — 통합 진행 상황
9. [morai-msgs-versions.md](./morai-msgs-versions.md) — 레포별 morai_msgs 버전
10. [morai-msgs-beta-policy.md](./morai-msgs-beta-policy.md) — **beta_drive 정렬 규약 (통합·일상 작업)**

## 본 repo에 포함되는 것

| 포함 | 미포함 (로컬·별도 관리) |
|------|-------------------------|
| catkin 패키지·통합 코드 | 맵·대용량 데이터 (`ASMC_DATA`) |
| Docker·빌드 스크립트 | 학습 체크포인트 |
| 팀 작업 규약·아키텍처 | 논문 PDF, 베이스라인 코드 clone |

베이스라인·MORAI 예제 코드는 필요 시 각자 GitHub에서 clone하여 **참조만** 합니다. 본 repo에 복사하지 않습니다.
