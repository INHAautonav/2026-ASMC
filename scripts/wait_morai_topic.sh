#!/usr/bin/env bash
# Wait until a ROS topic appears (and optionally receives one message).
# Usage: wait_morai_topic.sh /Ego_topic [max_seconds]
set -euo pipefail

TOPIC="${1:?topic required}"
MAX_SEC="${2:-120}"

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
# shellcheck source=asmc_env.sh
source "$SCRIPT_DIR/asmc_env.sh"

cd "$ASMC_WS_ROOT"
source /opt/ros/noetic/setup.bash
source devel/setup.bash 2>/dev/null || true
[ -f "$MORAI_BRIDGE_ENV" ] && source "$MORAI_BRIDGE_ENV"
export ROS_MASTER_URI="${ROS_MASTER_URI:-http://127.0.0.1:11311}"

if ! rostopic list >/dev/null 2>&1; then
  echo "ERROR: roscore not reachable (ROS_MASTER_URI=$ROS_MASTER_URI)"
  exit 1
fi

echo "ROS_MASTER_URI=$ROS_MASTER_URI"
echo "Waiting for ${TOPIC} (max ${MAX_SEC}s, MORAI Play + Connected)..."

found=0
for i in $(seq 1 "$MAX_SEC"); do
  if rostopic list 2>/dev/null | grep -F "${TOPIC}" >/dev/null 2>&1; then
    if timeout 2 rostopic echo -n 1 "${TOPIC}" >/dev/null 2>&1; then
      echo "OK ${TOPIC} publishing (after ${i}s)"
      exit 0
    fi
    found=1
    echo "  ... topic listed, waiting for first message (${i}/${MAX_SEC}s)"
  else
    if [ $((i % 10)) -eq 0 ]; then
      echo "  ... still waiting (${i}/${MAX_SEC}s)"
    fi
  fi
  sleep 1
done

echo "ERROR: ${TOPIC} not ready after ${MAX_SEC}s."
if [ "$found" -eq 1 ]; then
  echo "  Topic is listed but no message received — check MORAI Play / sync mode."
else
  echo "  Topic not in rostopic list. MORAI Bridge IP should match:"
  echo "    hostname -I | awk '{print \$1}'  ->  ${MORAI_BRIDGE_IP:-?}"
  echo "  Current topics:"
  rostopic list 2>/dev/null | head -20
fi
exit 1
