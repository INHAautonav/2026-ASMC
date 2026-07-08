# LBC 7-channel BEV (MORAI KATRI)

공식: [dotchen/LearningByCheating](https://github.com/dotchen/LearningByCheating) — `carla_utils.get_birdview`, `models/common.crop_birdview`, `train_birdview` (`input_channel=7`).

## 규격 대조

| 항목 | 공식 LBC | MORAI `lbc_bev` |
|------|----------|-----------------|
| 크기 | 320×320 | 동일 |
| Crop | 192×192 (ego row 260, col 160) | `crop_birdview()` 동일 |
| ppm / ahead | 5 / 100px | 동일 |
| 채널 | 7 (road, lane, TL×3, veh, ped) | 동일 순서 |
| Road/Lane | CARLA map | `road_mesh_out_line`, `lane_boundary_set` |

## 진단 리포트 (문제 시 이 파일을 공유)

```bash
cd "$(git rev-parse --show-toplevel)"
source devel/setup.bash
# bridge.sh + MORAI Connected 후
./src/learning_by_cheating/scripts/run_lbc_diagnose.sh
# → data/diag/lbc_report_*.txt 생성
```

## 오프라인 검증 (시뮬 불필요)

```bash
cd "$(git rev-parse --show-toplevel)/src/learning_by_cheating"
python3 scripts/verify_lbc_spec.py
# → ALL PASSED (~4초)
```

## MORAI 네트워크 설정

Ego Network · Simulator Network **동일**하게 설정합니다.

| 항목 | 값 |
|------|-----|
| Protocol | **ROS** |
| Bridge PORT | `9090` |
| **Bridge IP** | 아래 표 참고 |
| Status | Play 후 **Connected** |

**Bridge IP**

| 환경 | Bridge IP |
|------|-----------|
| Docker Desktop (WSL) | `hostname -I \| awk '{print $1}'` → 예: `192.168.65.6` |
| Linux 네이티브 | `127.0.0.1` |

`morai_bridge.env`는 Docker에서 IP를 자동 감지합니다. MORAI UI에 **같은 IP**를 넣어야 합니다.

## 실행 순서

### 터미널 1 — Bridge

```bash
cd "$(git rev-parse --show-toplevel)" && ./bridge.sh
```

### MORAI — Play + Connected

### 터미널 2 — 연결 확인

```bash
cd "$(git rev-parse --show-toplevel)" && ./check_morai_ros.sh
```

### 실시간 OpenCV imshow (권장)

```bash
cd "$(git rev-parse --show-toplevel)/src/learning_by_cheating"
./scripts/start_lbc_imshow.sh      # /Ego_topic 대기 120초 (기본)
./scripts/start_lbc_imshow.sh 180
```

- WSL/X11: `export DISPLAY=:0` 후 실행
- Ioniq 5 후륜축 기준 ego, 차량 신호등은 정지선 방향(빨/노/초)으로 표시
- 종료: 창에서 `q`

### 실시간 RViz (NPZ 저장 없음)

```bash
./scripts/start_lbc_rviz.sh
```

- 토픽: `/lbc_bev/image_full`, `/lbc_bev/image_cropped`
- RViz 설정: `config/lbc_bev.rviz` (Image 2개)
- DISPLAY 없으면: `LAUNCH_RVIZ=0 ./scripts/start_lbc_rviz.sh` 후 수동 `rviz -d config/lbc_bev.rviz`

### NPZ 수집

```bash
./scripts/start_lbc_morai.sh      # 기본 120초 대기
./scripts/start_lbc_morai.sh 180
```

- ROS: `/Ego_topic`, `/Object_topic`
- 신호등: `/GetTrafficLightStatus`, `/IntscnTL_topic`, `/TrafficLight_status` (가용 토픽 자동 구독)
- 저장: `data/bev_map/LBC_<timestamp>/*.npz`

## 좌회전 깜박이 · 신호등 색 (MoraiEventCmd)

뷰어·수집기 모두 **`/Service_MoraiEventCmd` 서비스를 10Hz로 폴링**해 `response.lamps.turnSignal` 을 읽습니다.

| turnSignal | 의미 | BEV TL 모드 |
|------------|------|-------------|
| 0 | 꺼짐 | straight (직진 표시 규칙) |
| 1 | 좌회전 | left (좌회전 표시 규칙) |
| 2 | 우회전 | straight (직진과 동일) |

KATRI 맵에서는 `/Lamps_topic` 이 비어 있어 **구독하지 않습니다.** 폴백으로 `turnSignal=0` 이 고정되면 enum 5·20 등이 직진 기준 **빨강**으로 보일 수 있습니다.

**확인**

```bash
rosservice call /Service_MoraiEventCmd "{request: {option: 0}}"
```

뷰어 로그 예:

```text
[LBCBEV-Viz] turnSignal=1 → TL mode=left
```

좌회전 ON 시 status 5 (RED_YELLOW), 20 (GREEN_YELLOW) 등은 **노랑**으로 표시됩니다.

**ROS 파라미터** (노드 private `~`):

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `morai_event_cmd_service` | `/Service_MoraiEventCmd` | 서비스 이름 |
| `morai_event_cmd_hz` | `10.0` | 폴링 주기 |
| `morai_event_cmd_wait_s` | `10.0` | 시작 시 서비스 대기(초) |

## API

```python
from lbc_bev import LBCRenderer
out = LBCRenderer("/root/aim_ws").render(x, y, yaw_deg)  # Docker container
```
