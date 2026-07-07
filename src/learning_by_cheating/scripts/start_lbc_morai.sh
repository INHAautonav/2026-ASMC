#!/usr/bin/env bash
# LBC BEV NPZ collection with MORAI
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
# shellcheck source=lbc_env.sh
source "$SCRIPT_DIR/lbc_env.sh"
WAIT_SEC="${1:-120}"

cd "$WS_ROOT"
source /opt/ros/noetic/setup.bash
source devel/setup.bash
[ -f "$MORAI_BRIDGE_ENV" ] && source "$MORAI_BRIDGE_ENV"
export ROS_MASTER_URI="${ROS_MASTER_URI:-http://127.0.0.1:11311}"

echo "=============================================="
echo " LBC 7ch BEV collector (MORAI)"
echo "=============================================="
echo "  ASMC_WS_ROOT:         $WS_ROOT"
echo "  Bridge IP (MORAI UI): ${MORAI_BRIDGE_IP:-127.0.0.1}"
echo "  Bridge PORT:          ${MORAI_BRIDGE_PORT:-9090}"
echo "  ROS_MASTER_URI:       ${ROS_MASTER_URI}"
echo "=============================================="
echo ""

"$WS_ROOT/scripts/wait_morai_topic.sh" /Ego_topic "$WAIT_SEC"
exec python3 "$LBC_SCRIPTS/lbc_bev_collector.py"
