#!/usr/bin/env bash
# Thin wrapper: harness/run.sh
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/../harness/run.sh" "$@"
