#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
# shellcheck source=../../scripts/asmc_env.sh
source "$REPO_ROOT/scripts/asmc_env.sh"
WS_ROOT="$ASMC_WS_ROOT"

cd "$WS_ROOT"

RUNNER_ARGS=("$@")
set --

if [ -f "$WS_ROOT/devel/setup.bash" ]; then
  # shellcheck disable=SC1091
  source "$WS_ROOT/devel/setup.bash"
fi

if [ -f "$MORAI_BRIDGE_ENV" ]; then
  # shellcheck disable=SC1091
  source "$MORAI_BRIDGE_ENV"
fi

export GRPC_POLL_STRATEGY="${GRPC_POLL_STRATEGY:-epoll1}"

set -- "${RUNNER_ARGS[@]}"

if [ "$#" -eq 0 ]; then
  set -- --zone urban --scenario random_route_drive
elif [ "${1#--}" = "$1" ]; then
  zone="$1"
  scenario="${2:-random_route_drive}"
  set -- --zone "$zone" --scenario "$scenario"
fi

exec python3 "$SCRIPT_DIR/scenario_launcher.py" "$@"
