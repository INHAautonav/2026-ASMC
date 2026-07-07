# 2026-ASMC

**2026 대학생 AI·SW 모빌리티 경진대회** (AI 융합 자율주행 부문) 팀 **통합 개발 코드** 저장소입니다.

> Repo 이름은 대회 약자(ASMC)를 사용합니다. 로컬 경로·셸 변수: `$ASMC`

- **팀원**: 정윤태, 양서준, 이강태, 안승현, 장원태, 손재호
- **GitHub**: https://github.com/INHAautonav/2026-ASMC
- **조직**: [INHAautonav](https://github.com/INHAautonav)

## 클론

```bash
git clone https://github.com/INHAautonav/2026-ASMC.git
cd 2026-ASMC
```

로컬 워크스페이스에 둘 때:

```bash
cd "$AIM_PROJECT"
git clone https://github.com/INHAautonav/2026-ASMC.git
```

## 브랜치·PR

- `main` 직접 push 금지 (팀 규칙 확정 후 CONTRIBUTING에 반영)
- `feature/<이름>-<기능>` 브랜치 → PR → merge

## 디렉터리 (예정)

```
2026-ASMC/
├── perception/          # 인지 모듈
├── planning_control/    # MPC·플래너
├── integration/         # ROS bridge, 실행·런치
└── docker/              # 실행 환경 (필요 시)
```

구조는 통합 진행에 맞춰 확정합니다.
