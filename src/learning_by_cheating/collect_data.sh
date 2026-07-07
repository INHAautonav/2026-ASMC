#!/bin/bash
# ============================================================================
# BEV 맵 데이터 수집 스크립트
# 
# run_experiment.sh와 hd_map_crop_ver2.py를 동시에 실행하여 데이터 수집
# 사용법: ./collect_data.sh [시간(초)] [선택적: 시나리오 번호]
# 예시:
#   ./collect_data.sh 180           # 180초(3분) 동안 데이터 수집
#   ./collect_data.sh 300 3         # 300초 동안 시나리오 3으로 수집
# ============================================================================

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 경로 설정
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
# shellcheck source=scripts/lbc_env.sh
source "$SCRIPT_DIR/scripts/lbc_env.sh"
DATA_DIR="$LBC_DIR/data"

# 파라미터
DURATION=${1:-180}  # 기본값 180초 (3분)
SCENARIO=${2:-3}    # 기본값 시나리오 3

# 함수: 정리 (Cleanup)
cleanup() {
    echo ""
    echo -e "${YELLOW}[INFO] 데이터 수집 중지 중...${NC}"
    
    # 모든 백그라운드 프로세스 종료
    kill $(jobs -p) 2>/dev/null || true
    
    echo -e "${GREEN}[INFO] 정리 완료${NC}"
    exit 0
}

# Ctrl+C 시 cleanup 함수 실행
trap cleanup SIGINT SIGTERM

# 필수 파일 확인
if [ ! -f "$WS_ROOT/run_experiment.sh" ]; then
    echo -e "${RED}[ERROR] run_experiment.sh를 찾을 수 없습니다: $WS_ROOT${NC}"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/lbc_bev_collector.py" ]; then
    echo -e "${RED}[ERROR] lbc_bev_collector.py를 찾을 수 없습니다: $SCRIPT_DIR${NC}"
    exit 1
fi

# 디렉토리 생성
mkdir -p "$DATA_DIR/raw"
mkdir -p "$DATA_DIR/bev_map"

# 환경 변수 설정
export PATH="/root/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   BEV 맵 데이터 수집 시작${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}[INFO] 설정:${NC}"
echo -e "  - 워크스페이스: $WS_ROOT"
echo -e "  - 수집 시간: ${DURATION}초"
echo -e "  - 시나리오: $SCENARIO"
echo -e "  - 데이터 저장 위치: $DATA_DIR"
echo ""

# 공통 타임스탐프 생성 (폴더명 통일용)
COMMON_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
export COMMON_TIMESTAMP

# Step 1: MORAI 시뮬레이터 실행 (백그라운드)
echo -e "${YELLOW}[STEP 1/3] MORAI 시뮬레이터 시작...${NC}"
echo -e "${GREEN}[INFO] 공통 타임스탐프: $COMMON_TIMESTAMP${NC}"
cd "$WS_ROOT"
./run_experiment.sh $SCENARIO &
SIMULATOR_PID=$!
echo -e "${GREEN}[INFO] 시뮬레이터 PID: $SIMULATOR_PID${NC}"

# Step 2: 시뮬레이터 초기화 대기
echo -e "${YELLOW}[STEP 2/3] 시뮬레이터 초기화 대기 (5초)...${NC}"
sleep 5

# Step 3: BEV 맵 생성 스크립트 실행 (포그라운드)
echo -e "${YELLOW}[STEP 3/3] BEV 맵 생성 시작...${NC}"
cd "$WS_ROOT"
source devel/setup.bash 2>/dev/null || true

# BEV 맵 생성 스크립트를 백그라운드에서 실행
python3 "$SCRIPT_DIR/hd_map_crop_ver2.py" &
BEV_PID=$!
echo -e "${GREEN}[INFO] BEV 맵 생성 PID: $BEV_PID${NC}"

echo ""
echo -e "${GREEN}[INFO] 데이터 수집 진행 중 (${DURATION}초)...${NC}"
echo -e "${YELLOW}[INFO] Ctrl+C 를 누르면 수집을 중지합니다.${NC}"
echo ""

# 타이머 시작
START_TIME=$(date +%s)
END_TIME=$((START_TIME + DURATION))

# 진행 상황 표시
while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    REMAINING=$((END_TIME - CURRENT_TIME))
    
    if [ $REMAINING -le 0 ]; then
        echo ""
        echo -e "${GREEN}[INFO] 수집 시간 종료!${NC}"
        cleanup
    fi
    
    # CSV 파일 개수
    CSV_COUNT=$(find "$DATA_DIR/raw" -name "*.csv" -type f 2>/dev/null | wc -l)
    
    # NPZ 파일 개수
    NPZ_COUNT=$(find "$DATA_DIR/bev_map" -name "*.npz" -type f 2>/dev/null | wc -l)
    
    echo -ne "${BLUE}[${ELAPSED}/${DURATION}s] CSV: ${CSV_COUNT} | NPZ: ${NPZ_COUNT} | 남은 시간: ${REMAINING}s${NC}\r"
    
    sleep 2
done
