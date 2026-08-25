#!/usr/bin/env bash
# Resolve kbshff: KBSHFF_BIN, PATH, or cargo build from KUIBYSHEFF_SRC / sibling clone.
set -euo pipefail

AGENT_BIN=""
FORCE_BUILD=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent-bin)
      AGENT_BIN="${2:-}"
      shift 2
      ;;
    --build)
      FORCE_BUILD=1
      shift
      ;;
    -h|--help)
      echo "Usage: resolve-kbshff.sh [--agent-bin PATH] [--build]" >&2
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXAMPLE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

find_kuibysheff_src() {
  if [[ -n "${KUIBYSHEFF_SRC:-}" && -f "${KUIBYSHEFF_SRC}/Cargo.toml" ]]; then
    cd "$KUIBYSHEFF_SRC" && pwd
    return 0
  fi
  local parent sibling
  parent="$(cd "$EXAMPLE_ROOT/.." && pwd)"
  for sibling in "Agent-Kuibysheff" "Agent Kuibyshev"; do
    if [[ -f "$parent/$sibling/Cargo.toml" ]]; then
      cd "$parent/$sibling" && pwd
      return 0
    fi
  done
  return 1
}

release_kbshff() {
  local root="$1"
  if [[ -x "$root/target/release/kbshff" ]]; then
    echo "$root/target/release/kbshff"
    return 0
  fi
  if [[ -f "$root/target/release/kbshff.exe" ]]; then
    echo "$root/target/release/kbshff.exe"
    return 0
  fi
  return 1
}

if [[ -n "$AGENT_BIN" ]]; then
  if [[ ! -f "$AGENT_BIN" ]]; then
    echo "kbshff binary not found: $AGENT_BIN" >&2
    exit 1
  fi
  cd "$(dirname "$AGENT_BIN")" && echo "$(pwd)/$(basename "$AGENT_BIN")"
  exit 0
fi

if [[ -n "${KBSHFF_BIN:-}" ]]; then
  if [[ ! -f "$KBSHFF_BIN" ]]; then
    echo "KBSHFF_BIN not found: $KBSHFF_BIN" >&2
    exit 1
  fi
  cd "$(dirname "$KBSHFF_BIN")" && echo "$(pwd)/$(basename "$KBSHFF_BIN")"
  exit 0
fi

if [[ "$FORCE_BUILD" -eq 0 ]] && command -v kbshff >/dev/null 2>&1; then
  command -v kbshff
  exit 0
fi

SRC=""
if SRC="$(find_kuibysheff_src)"; then
  :
else
  cat >&2 <<'EOF'
kbshff not found.

Install a release binary and ensure it is on PATH, or set one of:
  KBSHFF_BIN=/path/to/kbshff
  KUIBYSHEFF_SRC=/path/to/Agent-Kuibysheff   (then cargo build --release --bin kbshff)

See https://github.com/gazalievtimur/Agent-Kuibysheff
EOF
  exit 1
fi

echo "Building kbshff from $SRC ..." >&2
(
  cd "$SRC"
  cargo build --release -p agent_Kuibysheff --bin kbshff
)
release_kbshff "$SRC"
