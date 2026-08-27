#!/usr/bin/env bash
# Thin wrapper: oscript scripts/1c-live-regression.os
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec oscript -encoding=utf-8 "$SCRIPT_DIR/1c-live-regression.os" "$@"
