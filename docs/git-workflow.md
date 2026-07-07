# Git 브랜치·PR 워크플로

## 1. 기본 원칙

| 원칙 | 설명 |
|------|------|
| **`main` 직접 push 금지** | PR merge만 |
| **작은 PR** | 1 PR = 1 모듈 또는 1 기능 |
| **파트 격리** | 자신 담당 `src/` 패키지만 수정 (예외는 통합 리드 합의) |
| **merge 후 정리** | feature 브랜치 삭제, `main` pull |

## 2. 브랜치 종류

```
main                          ← 안정 (보호)
├── integrate/<모듈>          ← 통합 리드 (대규모 이식)
└── feature/<이름>-<기능>     ← 팀원 일상 작업
```

| 패턴 | 예 | 사용 |
|------|-----|------|
| `feature/seunghyun-logging` | 데이터 로거 | **권장** |
| `feature/yuntae-mpc-udp` | UDP 전환 | planning |
| `feature/jang-scenario` | 시나리오 러너 | perception |
| `integrate/learning` | LBC 통합 | 통합 리드 only |
| `fix/<이름>-<이슈>` | 버그 수정 | |

**비권장:** 개인 이름 단일 브랜치(`va_seunghyun`, `jang`)에 무한 누적 — 레거시 upstream만 참고.

## 3. 표준 흐름

```bash
cd "$ASMC"
git checkout main && git pull

git checkout -b feature/seunghyun-sync-logger
# ... 작업 ...
git add src/learning/   # 담당 경로만
git commit -m "feat(logging): Time Manager step bundle 추가"
git push -u origin feature/seunghyun-sync-logger

gh pr create --title "feat(logging): sync step bundle" --body "$(cat <<'EOF'
## Summary
- ...

## Test
- [ ] ./scripts/build_ws.sh
EOF
)"
```

## 4. 커밋 메시지

```
feat(scope): 한 줄 요약
fix(scope): 버그 수정
docs: 문서만
chore(docker): Docker 설정
refactor(planner): 리팩터 (동작 변경 없음)
```

`scope` 예: `mpc`, `planner`, `lbc`, `perception`, `docker`, `integration`

## 5. 충돌 방지

| 규칙 | 설명 |
|------|------|
| 담당 디렉터리 | [repository-layout.md](./repository-layout.md) 표 준수 |
| 공통 파일 | `launch/`, `interfaces/`, `docker/` → 통합 리드 리뷰 필수 |
| 대규모 이식 | `integrate/*` 브랜치에서만, 팀 공지 후 merge |

## 6. 통합 리드 역할 (안승현)

- `integrate/*` 브랜치 관리·PR 생성
- `main` merge 권한 (또는 팀장 approve)
- submodule·Docker·CI 갱신
- 레거시 분산 repo → `src/` 이식

## 7. GitHub

- 조직: [INHAautonav](https://github.com/INHAautonav)
- Repo: [2026-ASMC](https://github.com/INHAautonav/2026-ASMC)
