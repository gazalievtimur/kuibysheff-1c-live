#!/usr/bin/env bash
# Entry point for 1c-live «Склад» LLM eval.
set -euo pipefail

WORKFLOW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${WORKFLOW_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

export KUIBYSHEFF_ALLOW_UNSANDBOXED_MCP="${KUIBYSHEFF_ALLOW_UNSANDBOXED_MCP:-1}"

if [[ -f "${REPO_ROOT}/scripts/import-dotenv.sh" ]]; then
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/scripts/import-dotenv.sh" || true
  import_dotenv "${REPO_ROOT}/.env" || true
fi

DRY_RUN=0
ALL=0
REQUIRE_PLATFORM=0
WITH_SEARXNG=0
SKIP_BUILD=0
CONFIG=""
AGENT_BIN=""
TASK_IDS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --all) ALL=1; shift ;;
    --require-platform) REQUIRE_PLATFORM=1; shift ;;
    --with-searxng) WITH_SEARXNG=1; shift ;;
    --skip-build) SKIP_BUILD=1; shift ;;
    --config) CONFIG="$2"; shift 2 ;;
    --agent-bin) AGENT_BIN="$2"; shift 2 ;;
    --task-id) TASK_IDS+=("$2"); shift 2 ;;
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ "${DRY_RUN}" -eq 1 ]]; then
  python3 "${WORKFLOW_DIR}/eval.py" --dry-run \
    --bank-dir "${WORKFLOW_DIR}/bank" \
    --cf-dir "${WORKFLOW_DIR}/cf"
  echo "1c-live dry-run OK."
  exit 0
fi

RESOLVE_ARGS=()
[[ -n "${AGENT_BIN}" ]] && RESOLVE_ARGS+=(--agent-bin "${AGENT_BIN}")
[[ "${SKIP_BUILD}" -eq 0 && -z "${AGENT_BIN}" ]] && RESOLVE_ARGS+=(--build)
AGENT_BIN="$("${REPO_ROOT}/scripts/resolve-kbshff.sh" "${RESOLVE_ARGS[@]+"${RESOLVE_ARGS[@]}"}")"

if [[ -z "${CONFIG}" ]]; then
  if [[ -f "${REPO_ROOT}/agent-config.local.yaml" ]]; then
    CONFIG="${REPO_ROOT}/agent-config.local.yaml"
  else
    CONFIG="${REPO_ROOT}/profiles/1c-analyst/agent-config.example.yaml"
  fi
fi

ARGS=(
  "${WORKFLOW_DIR}/eval.py"
  --repo-root "${REPO_ROOT}"
  --config "${CONFIG}"
  --bank-dir "${WORKFLOW_DIR}/bank"
  --cf-dir "${WORKFLOW_DIR}/cf"
  --runs-root "${WORKFLOW_DIR}/runs"
  --agent-bin "${AGENT_BIN}"
)

if [[ "${ALL}" -eq 1 ]]; then
  ARGS+=(--all)
fi
for id in "${TASK_IDS[@]:-}"; do
  [[ -n "${id}" ]] && ARGS+=(--task-id "${id}")
done
if [[ "${REQUIRE_PLATFORM}" -eq 1 ]]; then
  ARGS+=(--require-platform)
fi
if [[ "${WITH_SEARXNG}" -eq 1 ]]; then
  ARGS+=(--with-searxng)
fi

echo "Using kbshff: ${AGENT_BIN}"
echo "Running 1c-live eval..."
python3 "${ARGS[@]}"

LATEST="$(tr -d '\r\n' < "${WORKFLOW_DIR}/runs/LATEST")"
python3 "${WORKFLOW_DIR}/assert_regression.py" "${LATEST}/report.json"
