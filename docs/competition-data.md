# 본선 공개 데이터

> **v1.0** (2026.07.11) · 로컬 `$ASMC_DATA` 또는 `$AIM_PROJECT/data/R_KR_PG_K-city_2025/`  
> 규정: [competition-environment.md](./competition-environment.md)

본 repo에는 **대용량·주최 배포 파일을 포함하지 않습니다.** 각자 동일 경로에 배치하세요.

## 파일 목록

| 파일 | 설명 |
|------|------|
| `2026_molit_comp_cam_set.json` | 고정 카메라 3대 + UDP/ROS 설정 |
| `2026_molit_comp_global_path.txt` | 본선 전역 경로 (x y z, **4429점**) |
| `2026_molit_comp_sample_scene.json` | 본선 샘플 시나리오 (Ego spawn 등) |

기존 HD Map: `link_set.json`, `node_set.json`, `global_info.json`

- 당일 **새 맵 제시 없음** (시나리오만 변동 가능)
- **MGeo**로 별도 경로 생성·주행 **허용** — 미션 순서·체크포인트 통과에 유의
- 확정 해석 전문: 로컬 `docs/competition/faq-official.md`

## 로컬 배치

```bash
# 예: ASMC_DATA 환경변수 사용 시
ls "$ASMC_DATA/R_KR_PG_K-city_2025/2026_molit_comp_"*
```

Google Drive: 로컬 `docs/competition/resources.md` (팀 Notion/디스코드 공지 링크 동일)

## 1. 카메라 센서셋

MORAI **Sensor Setting Load**로 사용.

| Camera | pos (m) | rot (deg) | 해상도 | FOV |
|--------|---------|-----------|--------|-----|
| Front | 1.9, 0, 1.2 | 0, 2, 0 | 1280×720 | 90º |
| Left | 1.15, 0.65, 1.2 | 0, 10, 70 | 640×480 | 130º |
| Right | 1.15, −0.65, 1.2 | 0, 10, 290 | 640×480 | 130º |

- 4번째 카메라: 규정 범위 내 **자유** 배치
- 본선: **UDP** — `udpConfig` 포트를 팀 PC와 맞출 것

## 2. 전역 경로

- 형식: 한 줄 `x y z`
- 용도: behavior/planner **레퍼런스 경로**
- 출발 미션 5%: 누적 호 길이 기준 ~221번째 절 근처 (4429점 기준)

```python
# 경로 로드 예시
path = []
with open("2026_molit_comp_global_path.txt") as f:
    for line in f:
        x, y, z = map(float, line.split())
        path.append((x, y, z))
```

## 3. 샘플 시나리오

- MORAI 시나리오 **Load**로 본선 형식 확인
- Ego 초기 pose ≈ (−131.49, −427.96, 28.88), yaw ≈ 62.5º
- **실제 본선** 시나리오는 당일 운영 요원 Load (2회 동일)

## 4. 통합 체크리스트

- [ ] perception: cam_set UDP 포트 ↔ 노드 구독
- [ ] planning: global_path → `path_route` 또는 Frenet 입력
- [ ] integration: sample_scene Load 후 Ego topic·Ctrl_cmd E2E
- [ ] 60kph·15분·GPS blackout 구간 시뮬 테스트

상세 (로컬 전용): `docs/competition/regulations/07-finals-data.md`
