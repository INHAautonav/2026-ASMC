#!/usr/bin/env bash
# ROS Noetic 개발 컨테이너 제어
set -euo pipefail
COMPOSE_DIR="$(dirname "$(readlink -f "$0")")/../docker/ros-noetic"
export ASMC="${ASMC:-$(dirname "$(readlink -f "$0")")/..}"

cmd="${1:-up}"
case "$cmd" in
  build)
    docker compose -f "$COMPOSE_DIR/docker-compose.yaml" build
    ;;
  up)
    docker compose -f "$COMPOSE_DIR/docker-compose.yaml" up -d --force-recreate
    docker ps --filter name=asmc-ros-noetic
    ;;
  down)
    docker compose -f "$COMPOSE_DIR/docker-compose.yaml" down
    ;;
  rebuild)
    docker compose -f "$COMPOSE_DIR/docker-compose.yaml" build --no-cache
    docker compose -f "$COMPOSE_DIR/docker-compose.yaml" up -d --force-recreate
    ;;
  *)
    echo "Usage: $0 {build|up|down|rebuild}"
    exit 1
    ;;
esac
