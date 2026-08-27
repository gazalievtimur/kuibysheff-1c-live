#!/usr/bin/env bash
# Entry point for 1c-live «Склад» LLM eval (OneScript).
set -euo pipefail

WORKFLOW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${WORKFLOW_DIR}/.." && pwd)"

if ! command -v oscript >/dev/null 2>&1; then
  echo "oscript not found in PATH (install OneScript 2.0)" >&2
  exit 1
fi

exec oscript -encoding=utf-8 "${WORKFLOW_DIR}/run.os" --repo-root "${REPO_ROOT}" "$@"
