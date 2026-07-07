#!/usr/bin/env bash
# catkin 워크스페이스 빌드 (컨테이너 또는 네이티브 Noetic 내부)
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."

if [[ ! -d src/MORAI-ROS_morai_msgs && ! -L src/MORAI-ROS_morai_msgs ]]; then
  echo "[build_ws] ERROR: src/MORAI-ROS_morai_msgs 가 없습니다."
  echo "  docs/getting-started.md §3 참고 (submodule 또는 symlink)"
  exit 1
fi

source /opt/ros/noetic/setup.bash
catkin_make "$@"
echo "[build_ws] done. source devel/setup.bash"
