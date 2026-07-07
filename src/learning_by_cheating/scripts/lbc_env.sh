#!/usr/bin/env bash
# Shared env for learning_by_cheating shell scripts.
_LBC_ENV_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../../scripts/asmc_env.sh
source "$_LBC_ENV_DIR/../../../scripts/asmc_env.sh"
export WS_ROOT="$ASMC_WS_ROOT"
export LBC_DIR="$WS_ROOT/src/learning_by_cheating"
export LBC_SCRIPTS="$LBC_DIR/scripts"
