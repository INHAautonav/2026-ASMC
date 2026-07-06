#!/usr/bin/env bash
# Clone reference repositories into external/
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXT="${ROOT}/external"

clone_if_missing() {
  local url="$1"
  local dest="$2"
  local branch="${3:-}"

  if [ -d "${dest}/.git" ]; then
    echo "[skip] ${dest} (already cloned)"
    return
  fi

  mkdir -p "$(dirname "${dest}")"
  if [ -n "${branch}" ]; then
    git clone --branch "${branch}" --single-branch "${url}" "${dest}"
  else
    git clone "${url}" "${dest}"
  fi
  echo "[ok]   ${dest}"
}

echo "==> Cloning external repositories into ${EXT}"

# Legacy team ROS workspace (pre-competition integration)
clone_if_missing \
  "https://github.com/kante2/aim_ws.git" \
  "${EXT}/aim_ws" \
  "va_seunghyun"

# Baselines
clone_if_missing "https://github.com/zhejz/carla-roach.git" "${EXT}/baselines/carla-roach"
clone_if_missing "https://github.com/ahnsh03/morai-roach.git" "${EXT}/baselines/morai-roach"
clone_if_missing "https://github.com/dotchen/LearningByCheating.git" "${EXT}/baselines/LearningByCheating"

# MORAI official
clone_if_missing "https://github.com/MORAI-Autonomous/MORAI-MGeoModule" "${EXT}/morai/MORAI-MGeoModule"
clone_if_missing "https://github.com/MORAI-Autonomous/MORAI-ROS_morai_msgs.git" "${EXT}/morai/MORAI-ROS_morai_msgs"
clone_if_missing "https://github.com/MORAI-Autonomous/MORAI-SensorExample.git" "${EXT}/morai/MORAI-SensorExample"

echo "==> Done."
