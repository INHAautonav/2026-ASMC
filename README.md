# 2026 AI·SW Mobility Competition — Autonav

**2026 대학생 AI·SW 모빌리티 경진대회** (AI 융합 자율주행 부문) 팀 **통합 개발 코드** 저장소입니다.

- **팀원**: 정윤태, 양서준, 이강태, 안승현, 장원태, 손재호
- **GitHub**: https://github.com/ahnsh03/2026-ai-sw-mobility-competition-autonav

## 이 repo에 담는 것

- 팀이 함께 개발·배포하는 **소스 코드** (인지, 판단·제어, 통합 실행 등)

## 이 repo에 담지 않는 것

| 내용 | 위치 (로컬) |
|------|-------------|
| 규정 PDF, 논문, 팀 운영 메모 | `../docs/` |
| 베이스라인·팀원 분산 레포 클론 | `../external/` |
| 통합 전 스테이징 | `../external/team/` |

로컬 워크스페이스 루트: `~/projects/2026-ai-sw-mobility-competition/`

## 클론

```bash
git clone https://github.com/ahnsh03/2026-ai-sw-mobility-competition-autonav.git \
  ~/projects/2026-ai-sw-mobility-competition/2026-ai-sw-mobility-competition-autonav
```

## 브랜치·PR

- `main` 직접 push 금지 (팀 규칙 확정 후 CONTRIBUTING에 반영)
- `feature/<이름>-<기능>` 브랜치 → PR → merge

## 통합 현황

`external/team/`에 모아 둔 분산 코드를 이 repo로 단계적으로 통합 중입니다.

| 파트 | 출처 (external/team) | 통합 상태 |
|------|----------------------|-----------|
| 판단·제어 | `mpc_ws/` | 대기 |
| 인지 | `morai-3d-detection/`, `aim_ws-*` | 대기 |
| 학습 인프라 | `aim_ws-va_seunghyun/` | 대기 |

## 디렉터리 (예정)

```
2026-ai-sw-mobility-competition-autonav/
├── perception/          # 인지 모듈
├── planning_control/    # MPC·플래너
├── integration/         # ROS bridge, 실행·런치
└── docker/              # 실행 환경 (필요 시)
```

구조는 통합 진행에 맞춰 확정합니다.
