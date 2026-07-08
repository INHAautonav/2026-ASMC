# Git 브랜치·PR 워크플로

## 1. 기본 원칙

| 원칙 | 설명 |
|------|------|
| **`main` 직접 push 금지** | PR merge만 |
| **작은 PR** | 1 PR = 1 버그 또는 1 기능 |
| **파트 격리** | [team-dev-guide.md](./team-dev-guide.md) 담당 경로만 |
| **merge 후 정리** | feature 브랜치 삭제, `main` pull |

## 2. 브랜치 종류

```
main                          ← 안정 (보호)
├── integrate/<모듈>          ← 통합 리드 (대규모 이식 — 1차 완료)
└── feature/<이름>-<기능>     ← 팀원 일상 작업
```

| 패턴 | 예 | 사용 |
|------|-----|------|
| `feature/seunghyun-lbc-train` | LBC 학습 | learning |
| `feature/yuntae-mpc-udp` | UDP 전환 | planning |
| `feature/kangtae-frenet-cost` | Frenet cost | planner |
| `feature/jang-scenario-dataset-ctrl` | D-10 | scenario |
| `feature/jaeho-inference-node` | 추론 노드 | perception |
| `integrate/interfaces` | τ·BEV 합의 | 통합 리드 |

**비권장:** 개인 이름 단일 브랜치(`va_seunghyun`, `jang`)에 무한 누적.

## 3. 표준 흐름

```bash
cd "$ASMC"
git checkout main && git pull
git checkout -b feature/seunghyun-lbc-train
# ... 담당 경로만 수정 ...
git add src/learning_by_cheating/
git commit -m "feat(lbc): improve BEV vehicle channel sync"
git push -u origin feature/seunghyun-lbc-train

gh pr create --title "feat(lbc): vehicle channel sync" --body "$(cat <<'EOF'
## Summary
- ...

## Test
- [ ] ./scripts/build_ws.sh
- [ ] sim-verification-checklist 해당 §
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

`scope` 예: `mpc`, `planner`, `behavior`, `lbc`, `perception`, `scenario`, `docker`, `integration`

## 5. 충돌 방지

| 규칙 | 설명 |
|------|------|
| 담당 디렉터리 | [team-dev-guide.md](./team-dev-guide.md) · [repository-layout.md](./repository-layout.md) |
| 공통 파일 | `integration_launch/`, `interfaces/`, `docker/` → 합의·통합 리드 리뷰 |
| msg 스키마 | `behavior_planner/msg/*` 변경 시 planner bridge 동시 |

## 6. 통합 리드 역할 (안승현)

- `integrate/*` · `main` merge 조율
- submodule·Docker·공용 docs
- τ·BEV (`interfaces`) 합의 주관

## 7. GitHub

- 조직: [INHAautonav](https://github.com/INHAautonav)
- Repo: [2026-ASMC](https://github.com/INHAautonav/2026-ASMC)
