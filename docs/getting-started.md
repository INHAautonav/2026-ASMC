# 시작 가이드

## 1. 사전 준비

| 항목 | 요구 |
|------|------|
| Git | 2.30+ |
| GitHub CLI | `gh` (PR 생성) |
| Docker Desktop | WSL 연동 활성화 (개발 PC) |
| 대회 리허설 PC | **Ubuntu 20.04 네이티브** 1대 권장 |

### WSL 개발 PC (Windows, 최초 1회)

대회 당일 PC는 **네이티브 Ubuntu 20.04**입니다. Windows PC에서는 **WSL2 + Docker**로 일상 개발합니다.

| 항목 | 내용 |
|------|------|
| WSL | Ubuntu 20.04 권장 (`wsl --install -d Ubuntu`) |
| Docker | Docker Desktop → Settings → **WSL Integration** → Ubuntu **ON** |
| clone 위치 | **WSL 홈** (`~/...`) 어디든 가능. `/mnt/c/...` **금지** — [getting-started.md §2](./getting-started.md) |
| 맵 데이터 | repo 밖 `$ASMC_DATA`. 탐색기 `\\wsl.localhost\<배포판>\home\<user>\asmc-data` 로 복사 가능 |
| MORAI SIM | **Windows에서 실행**. 최초 실행 시 방화벽 **개인·공용 네트워크 허용** |
| IDE | WSL Remote 지원 에디터 또는 `docker exec -it asmc-ros-noetic bash` |

```bash
# Git 인증 (Windows + WSL, 선택) — 본인 환경의 credential helper 사용
git clone --recurse-submodules https://github.com/INHAautonav/2026-ASMC.git
```

셸 변수 (`~/.bashrc`, **선택** — 편하면 설정):

```bash
export ASMC="<clone한-2026-ASMC-경로>"
export ASMC_DATA="<맵·대용량-데이터-경로>"
```

`ASMC`를 설정하지 않아도, **repo 루트에서** `./scripts/...` 를 실행하면 스크립트가 경로를 자동으로 찾습니다.  
팀원마다 clone 위치가 달라도 됩니다. 통일할 필요는 없습니다.

## 2. 클론

### 주의사항 (필수)

| 규칙 | 이유 |
|------|------|
| **WSL 리눅스 파일시스템**에 clone (`~/...`) | `/mnt/c/Users/...` 는 **금지** — Git·맵·NPZ 파일명 충돌, 느린 I/O, 권한 오류 |
| **호스트 절대 경로를 코드에 넣지 않음** | 컨테이너 안은 항상 `/root/ws`. 맵은 `$ASMC_DATA` → `/data` |
| **submodule 포함 clone** | `morai_msgs` 누락 방지 |

### 명령

`ASMC` 변수를 쓰는 경우:

```bash
mkdir -p "$(dirname "$ASMC")"
git clone --recurse-submodules https://github.com/INHAautonav/2026-ASMC.git "$ASMC"
cd "$ASMC"
git checkout main && git pull
```

경로를 정하지 않고 clone하는 경우:

```bash
git clone --recurse-submodules https://github.com/INHAautonav/2026-ASMC.git <원하는-경로>
cd <원하는-경로>
git checkout main && git pull
```

이미 clone한 뒤 submodule만 받을 때:

```bash
cd <clone한-2026-ASMC-경로>
git submodule update --init --recursive
```

**하지 말 것:** 윈도우 탐색기로 repo 안의 `build/`, `devel/` 을 수정·삭제 (WSL 권한 꼬임). 데이터 파일은 repo 밖 `$ASMC_DATA`에 둡니다.

## 3. morai_msgs 추가

```bash
cd "$ASMC"
git submodule add -b beta_drive \
  https://github.com/MORAI-Autonomous/MORAI-ROS_morai_msgs.git \
  src/MORAI-ROS_morai_msgs
git submodule update --init --recursive
```

이미 submodule이 등록된 경우:

```bash
git submodule update --init --recursive
```

## 4. Docker로 ROS 환경 실행

```bash
cd "$ASMC"
xhost +local:docker
./scripts/docker_ros_up.sh build
./scripts/docker_ros_up.sh up
docker exec -it asmc-ros-noetic bash
# 컨테이너 안
./scripts/build_ws.sh
```

## 5. 작업 브랜치 생성

```bash
git checkout main && git pull
git checkout -b feature/<이름>-<기능>
```

- 브랜치 규칙: [git-workflow.md](./git-workflow.md)
- **팀원별 수정 경로·검증:** [team-dev-guide.md](./team-dev-guide.md)
- 시뮬 검증: [sim-verification-checklist.md](./sim-verification-checklist.md)

`behavior_planner` 빌드에는 Docker 이미지의 `libyaml-cpp-dev`가 필요합니다 (`./scripts/docker_ros_up.sh build`로 이미지 재생성).
