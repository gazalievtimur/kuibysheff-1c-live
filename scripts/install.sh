#!/usr/bin/env bash
# Bootstrap kuibysheff-1c-live: host checks, MCP tools, .env secrets, kbshff CLI provider.
set -euo pipefail

REPO_ROOT=""
TOOLS_DIR=""
SKIP_INGEST=0
NON_INTERACTIVE=0
BASE_URL=""
MODEL=""
MODEL_ANALYST=""
MODEL_YAXUNIT=""
MODEL_CODER=""
MODEL_IMPLEMENTER=""
API_KEY_ENV_NAME=""
PLATFORM_PATH=""
OSCRIPT_VERSION="stable"
# Clone/ref for 1c-sntx-sem (default: main). Override only if you need an older tip.
SNTX_SEM_GIT_REF="${SNTX_SEM_GIT_REF:-main}"
FRESH=0

usage() {
  cat <<'EOF'
Usage: scripts/install.sh [--repo-root DIR] [--tools-dir DIR] [--skip-ingest]
                          [--non-interactive] [--fresh] [--base-url URL] [--model NAME]
                          [--model-analyst NAME] [--model-yaxunit NAME]
                          [--model-coder NAME] [--model-implementer NAME]
                          [--api-key-env NAME] [--platform-path DIR]
                          [--oscript-version VERSION] [--sntx-sem-git-ref REF]
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    --tools-dir) TOOLS_DIR="$2"; shift 2 ;;
    --skip-ingest) SKIP_INGEST=1; shift ;;
    --non-interactive) NON_INTERACTIVE=1; shift ;;
    --fresh) FRESH=1; shift ;;
    --base-url) BASE_URL="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    --model-analyst) MODEL_ANALYST="$2"; shift 2 ;;
    --model-yaxunit) MODEL_YAXUNIT="$2"; shift 2 ;;
    --model-coder) MODEL_CODER="$2"; shift 2 ;;
    --model-implementer) MODEL_IMPLEMENTER="$2"; shift 2 ;;
    --api-key-env) API_KEY_ENV_NAME="$2"; shift 2 ;;
    --platform-path) PLATFORM_PATH="$2"; shift 2 ;;
    --oscript-version) OSCRIPT_VERSION="$2"; shift 2 ;;
    --sntx-sem-git-ref) SNTX_SEM_GIT_REF="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -z "$REPO_ROOT" ]]; then
  REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
else
  REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
fi
if [[ -z "$TOOLS_DIR" ]]; then
  TOOLS_DIR="$REPO_ROOT/tools"
fi
INSTALL_STATE_PATH="$REPO_ROOT/.install-state.json"
INSTALL_COMPLETED=()
INSTALL_PLATFORM_PATH=""

step() { echo "==> $*"; }
hint() {
  if [[ "$NON_INTERACTIVE" -eq 0 ]]; then
    if [[ -z "$*" ]]; then
      echo ""
    else
      printf '\033[90m%s\033[0m\n' "$*"
    fi
  fi
}
write_input_label() {
  local prompt="$1"
  printf '\033[46;30m[ВВОД]\033[0m \033[36m%s\033[0m: ' "$prompt"
}
have() { command -v "$1" >/dev/null 2>&1; }

save_install_state() {
  COMPLETED_LINES="$(printf '%s\n' "${INSTALL_COMPLETED[@]+"${INSTALL_COMPLETED[@]}"}")" \
  PLATFORM_PATH_STATE="$INSTALL_PLATFORM_PATH" \
  python3 - "$INSTALL_STATE_PATH" <<'PY'
import datetime, json, os, sys
path = sys.argv[1]
steps = [s for s in os.environ.get("COMPLETED_LINES", "").splitlines() if s.strip()]
payload = {
    "version": 1,
    "completed": steps,
    "platform_path": os.environ.get("PLATFORM_PATH_STATE", ""),
    "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
with open(path, "w", encoding="utf-8") as f:
    f.write(json.dumps(payload, ensure_ascii=False) + "\n")
PY
}

import_install_state() {
  INSTALL_COMPLETED=()
  INSTALL_PLATFORM_PATH=""
  [[ -f "$INSTALL_STATE_PATH" ]] || return 0
  eval "$(python3 - "$INSTALL_STATE_PATH" <<'PY'
import json, shlex, sys
path = sys.argv[1]
try:
    obj = json.load(open(path, encoding="utf-8"))
except Exception as exc:
    print(f'echo "Ignoring corrupt .install-state.json: {exc}" >&2')
    sys.exit(0)
platform = obj.get("platform_path") or ""
print(f"INSTALL_PLATFORM_PATH={shlex.quote(str(platform))}")
for step in obj.get("completed") or []:
    s = str(step).strip()
    if s:
        print(f"INSTALL_COMPLETED+=({shlex.quote(s)})")
PY
)"
}

clear_install_state() {
  INSTALL_COMPLETED=()
  INSTALL_PLATFORM_PATH=""
  rm -f "$INSTALL_STATE_PATH"
}

step_done() {
  local name="$1" s
  for s in "${INSTALL_COMPLETED[@]+"${INSTALL_COMPLETED[@]}"}"; do
    [[ "$s" == "$name" ]] && return 0
  done
  return 1
}

complete_step() {
  local name="$1"
  if ! step_done "$name"; then
    INSTALL_COMPLETED+=("$name")
  fi
  save_install_state
}

initialize_install_resume() {
  if [[ "$FRESH" -eq 1 ]]; then
    echo "Fresh install: clearing .install-state.json"
    clear_install_state
    return
  fi
  import_install_state
  if [[ "${#INSTALL_COMPLETED[@]}" -eq 0 ]]; then
    return
  fi
  local last="${INSTALL_COMPLETED[$((${#INSTALL_COMPLETED[@]} - 1))]}"
  echo ""
  printf '\033[33mНайдено незавершённое install (checkpoint: %s).\033[0m\n' "$last"
  printf '\033[33mСостояние: %s\033[0m\n' "$INSTALL_STATE_PATH"
  if [[ "$NON_INTERACTIVE" -eq 1 ]]; then
    echo "NonInteractive: продолжаем с сохранённого места."
    return
  fi
  local ans
  write_input_label "Подтверждение: продолжить с сохранённого места? [Y/n]"
  read -r ans || true
  case "$(printf '%s' "$ans" | tr '[:upper:]' '[:lower:]')" in
    n|no|н|нет)
      echo "Starting from the beginning."
      clear_install_state
      ;;
    *)
      echo "Resuming install..."
      ;;
  esac
}

require_host() {
  local name="$1" hint_msg="$2"
  if have "$name"; then
    echo "OK  $name"
    return
  fi
  echo "$name not found in PATH. $hint_msg" >&2
  exit 1
}

confirm_optional_host_gaps() {
  if [[ "$#" -eq 0 ]]; then
    return
  fi
  echo "" >&2
  echo "============================================================" >&2
  echo "ВНИМАНИЕ: рекомендуемые инструменты не найдены" >&2
  echo "============================================================" >&2
  local gap
  for gap in "$@"; do
    echo "  * $gap" >&2
  done
  echo "" >&2
  echo "Рекомендуем установить их СЕЙЧАС (до продолжения install):" >&2
  echo "  docs/prerequisites.md" >&2
  echo "Без Node.js / Java 17+ штатный MCP bsl-language-server не настроится." >&2
  echo "Без bin платформы 1С ingest справки sntx_sem будет недоступен (семантический поиск)." >&2
  echo "Свой MCP без Node/Java можно подключить позже через CLI / .env." >&2
  echo "" >&2
  if [[ "$NON_INTERACTIVE" -eq 1 ]]; then
    echo "NonInteractive: продолжаем без рекомендуемых инструментов." >&2
    return
  fi
  local ans
  write_input_label "Подтверждение: продолжить без рекомендуемых инструментов? [y/N]"
  read -r ans || true
  case "$(printf '%s' "$ans" | tr '[:upper:]' '[:lower:]')" in
    y|yes|д|да) echo "Continuing without recommended tools..." ;;
    *)
      echo "Install cancelled. Install missing tools (see docs/prerequisites.md) and re-run." >&2
      exit 1
      ;;
  esac
}

dotenv_get() {
  local file="$1" key="$2"
  [[ -f "$file" ]] || return 0
  python3 - "$file" "$key" <<'PY'
import sys
path, key = sys.argv[1], sys.argv[2]
try:
    text = open(path, encoding="utf-8").read()
except FileNotFoundError:
    sys.exit(0)
for raw in text.splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    name, value = line.split("=", 1)
    name, value = name.strip(), value.strip()
    if len(value) >= 2 and ((value[0] == value[-1] == '"') or (value[0] == value[-1] == "'")):
        value = value[1:-1]
    if name == key:
        print(value)
        break
PY
}

# Keep a simple KEY=value file; last write wins for known keys via python.
dotenv_set_many() {
  local file="$1"
  local payload
  payload="$(cat)"
  UPDATES="$payload" python3 - "$file" <<'PY'
import os, sys
path = sys.argv[1]
existing = {}
order = []
if os.path.isfile(path):
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if name not in existing:
            order.append(name)
        existing[name] = value.strip()
preferred = [
    "KBSHFF_PROVIDER_BASE_URL",
    "KBSHFF_PROVIDER_MODEL",
    "KBSHFF_PROVIDER_MODEL_1C_ANALYST",
    "KBSHFF_PROVIDER_MODEL_1C_YAXUNIT",
    "KBSHFF_PROVIDER_MODEL_1C_CODER",
    "KBSHFF_PROVIDER_MODEL_1C_IMPLEMENTER",
    "KBSHFF_PROVIDER_API_KEY_ENV",
    "OPENAI_API_KEY",
    "POLZA_API_KEY",
    "DEEPSEEK_API_KEY",
    "SNTX_SEM_CONFIG",
    "SNTX_SEM_PYTHON",
    "BSL_INDEXER",
    "CODE_INDEX_HOME",
    "BSL_LS_MCP",
    "BSL_LS_JAR",
    "JAVA_HOME",
    "KBSHFF_BIN",
    "OSCRIPT_BIN",
    "KUIBYSHEFF_SRC",
]
for raw in os.environ.get("UPDATES", "").splitlines():
    if "=" not in raw:
        continue
    k, v = raw.split("=", 1)
    existing[k] = v
    if k not in order:
        order.append(k)
lines = ["# Generated by scripts/install.sh. Secrets stay here, not in YAML or CLI argv."]
seen = set()
for k in preferred + order:
    if k in seen:
        continue
    if k not in existing or not existing[k]:
        continue
    lines.append(f"{k}={existing[k]}")
    seen.add(k)
with open(path, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lines) + "\n")
PY
}

read_default() {
  local prompt="$1" default="$2"
  if [[ "$NON_INTERACTIVE" -eq 1 ]]; then
    printf '%s' "$default"
    return
  fi
  local label="$prompt" value
  [[ -n "$default" ]] && label="${prompt} [${default}]"
  write_input_label "$label"
  read -r value || true
  if [[ -z "$value" ]]; then
    printf '%s' "$default"
  else
    printf '%s' "$value"
  fi
}

read_secret() {
  local prompt="$1" value
  if [[ "$NON_INTERACTIVE" -eq 1 ]]; then
    printf ''
    return
  fi
  write_input_label "$prompt"
  read -r -s value || true
  echo "" >&2
  printf '%s' "$value"
}

valid_env_var_name() {
  [[ "$1" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]
}

looks_like_api_key() {
  local v="$1"
  [[ -z "$v" ]] && return 1
  [[ "$v" =~ ^[Ss][Kk][-_] ]] && return 0
  if [[ ${#v} -ge 20 ]] && ! valid_env_var_name "$v"; then
    return 0
  fi
  return 1
}

env_or_file() {
  local key="$1" file="$2"
  if [[ -n "${!key:-}" ]]; then
    printf '%s' "${!key}"
    return
  fi
  dotenv_get "$file" "$key"
}

github_asset_url() {
  local repo="$1" match="$2"
  python3 - "$repo" "$match" <<'PY'
import json, sys, urllib.request
repo, match = sys.argv[1], sys.argv[2]
req = urllib.request.Request(
    f"https://api.github.com/repos/{repo}/releases/latest",
    headers={"User-Agent": "kuibysheff-1c-live-install"},
)
with urllib.request.urlopen(req) as resp:
    data = json.load(resp)
for asset in data.get("assets", []):
    name = asset.get("name") or ""
    import fnmatch
    if fnmatch.fnmatch(name, match):
        print(asset["browser_download_url"])
        sys.exit(0)
raise SystemExit(f"No GitHub asset matching {match!r} in {repo}")
PY
}

download_file() {
  local url="$1" out="$2" label="${3:-download}"
  echo "Downloading $url"
  curl -fL --progress-bar -A "kuibysheff-1c-live-install" -o "$out" "$url"
}

find_under() {
  local root="$1" name="$2"
  find "$root" -type f -name "$name" 2>/dev/null | head -n 1
}

kbshff_release_glob() {
  local u m
  u="$(uname -s)"
  m="$(uname -m)"
  case "$u-$m" in
    Linux-x86_64|Linux-amd64)
      echo "agent_Kuibysheff-*-x86_64-unknown-linux-gnu.zip"
      ;;
    *)
      echo ""
      ;;
  esac
}

find_oscript() {
  if have oscript; then
    command -v oscript
    return
  fi
  local c
  for c in \
    ${OVM_INSTALL_PATH:+"$OVM_INSTALL_PATH/current/bin/oscript"} \
    "$HOME/ovm/current/bin/oscript" \
    "$HOME/.local/share/ovm/current/bin/oscript" \
    "$HOME/.ovm/current/bin/oscript" \
    "${LOCALAPPDATA:+$LOCALAPPDATA/ovm/current/bin/oscript.exe}" \
    "$HOME/ovm/current/bin/oscript.exe"; do
    if [[ -n "$c" && -x "$c" ]]; then
      printf '%s' "$c"
      return
    fi
  done
  printf ''
}

run_ovm() {
  local ovm_exe="$1"
  shift
  local uname_s
  uname_s="$(uname -s)"
  case "$uname_s" in
    MINGW*|MSYS*|CYGWIN*)
      "$ovm_exe" "$@"
      ;;
    *)
      have mono || {
        echo "mono not found (needed to run ovm.exe on Linux/macOS). Install Mono 6+ or OneScript manually. docs/prerequisites.md" >&2
        exit 1
      }
      mono "$ovm_exe" "$@"
      ;;
  esac
}

ensure_oscript() {
  step "OneScript (ovm)"
  local existing ovm_dir ovm_exe bin_dir ans
  existing="$(find_oscript)"
  if [[ -n "$existing" ]]; then
    bin_dir="$(cd "$(dirname "$existing")" && pwd)"
    export PATH="$bin_dir:$PATH"
    echo "OK  oscript ($existing)"
    printf '%s' "$existing"
    return
  fi
  echo "oscript не найден в PATH."
  echo "Установим OneScript через OVM: https://github.com/oscript-library/ovm"
  echo "Версия: $OSCRIPT_VERSION (на Linux/macOS для ovm.exe нужен Mono 6+)."
  if [[ "$NON_INTERACTIVE" -eq 0 ]]; then
    write_input_label "Подтверждение: установить OneScript ($OSCRIPT_VERSION) через ovm? [Y/n]"
    read -r ans || true
    case "$(printf '%s' "$ans" | tr '[:upper:]' '[:lower:]')" in
      n|no|н|нет)
        echo "oscript required. Install via OVM (docs/prerequisites.md) or re-run and accept install." >&2
        exit 1
        ;;
    esac
  else
    echo "NonInteractive: installing OneScript via ovm ($OSCRIPT_VERSION)..."
  fi
  ovm_dir="$TOOLS_DIR/ovm"
  mkdir -p "$ovm_dir"
  ovm_exe="$ovm_dir/ovm.exe"
  if [[ ! -f "$ovm_exe" ]]; then
    download_file "$(github_asset_url oscript-library/ovm 'ovm.exe')" "$ovm_exe" "ovm"
  fi
  run_ovm "$ovm_exe" install "$OSCRIPT_VERSION"
  run_ovm "$ovm_exe" use "$OSCRIPT_VERSION"
  existing="$(find_oscript)"
  if [[ -z "$existing" ]]; then
    echo "oscript still not found after ovm install/use. Check OVM_INSTALL_PATH. docs/prerequisites.md" >&2
    exit 1
  fi
  bin_dir="$(cd "$(dirname "$existing")" && pwd)"
  export PATH="$bin_dir:$PATH"
  echo "OK  oscript ($existing) via ovm"
  echo "Hint: add to PATH for new shells: $bin_dir"
  printf '%s' "$existing"
}

install_kbshff_from_release() {
  local glob url zip extract found stable sha_url sha_file expected actual
  glob="$(kbshff_release_glob)"
  if [[ -z "$glob" ]]; then
    echo "No prebuilt kbshff for $(uname -s)/$(uname -m). See https://github.com/gazalievtimur/Agent-Kuibysheff/blob/main/docs/INSTALL.md" >&2
    return 1
  fi
  stable="$TOOLS_DIR/kbshff"
  url="$(github_asset_url gazalievtimur/Agent-Kuibysheff "$glob")"
  zip="$(mktemp)"
  extract="$(mktemp -d)"
  download_file "$url" "$zip" "kbshff release"
  if sha_url="$(github_asset_url gazalievtimur/Agent-Kuibysheff "${glob}.sha256" 2>/dev/null)"; then
    sha_file="$(mktemp)"
    download_file "$sha_url" "$sha_file" "kbshff checksum"
    expected="$(awk '{print tolower($1)}' "$sha_file")"
    actual="$(sha256sum "$zip" | awk '{print tolower($1)}')"
    if [[ -n "$expected" && "$expected" != "$actual" ]]; then
      echo "kbshff zip SHA256 mismatch (expected $expected, got $actual)" >&2
      rm -rf "$zip" "$extract" "$sha_file"
      return 1
    fi
    echo "OK  kbshff SHA256"
    rm -f "$sha_file"
  else
    echo "No .sha256 asset for kbshff release; skipping checksum" >&2
  fi
  unzip -qo "$zip" -d "$extract"
  found="$(find_under "$extract" kbshff)"
  [[ -n "$found" ]] || { echo "kbshff not found in release archive" >&2; rm -rf "$zip" "$extract"; return 1; }
  mkdir -p "$TOOLS_DIR"
  cp "$found" "$stable"
  chmod +x "$stable"
  rm -rf "$zip" "$extract"
  echo "Installed kbshff -> $stable"
  printf '%s' "$stable"
}

ensure_kbshff() {
  step "kbshff"
  local explicit src parent found release downloaded
  explicit="$(env_or_file KBSHFF_BIN "$ENV_FILE")"
  if [[ -n "$explicit" && -f "$explicit" ]]; then
    printf '%s' "$(cd "$(dirname "$explicit")" && pwd)/$(basename "$explicit")"
    return
  fi
  if [[ -f "$TOOLS_DIR/kbshff" ]]; then
    printf '%s' "$(cd "$TOOLS_DIR" && pwd)/kbshff"
    return
  fi
  if have kbshff; then
    command -v kbshff
    return
  fi
  parent="$(cd "$REPO_ROOT/.." && pwd)"
  src="$(env_or_file KUIBYSHEFF_SRC "$ENV_FILE")"
  found=""
  for c in "$src" "$parent/Agent-Kuibysheff" "$parent/Agent Kuibyshev"; do
    [[ -n "$c" && -f "$c/Cargo.toml" ]] || continue
    found="$(cd "$c" && pwd)"
    release="$found/target/release/kbshff"
    if [[ -f "$release" ]]; then
      printf '%s' "$release"
      return
    fi
    break
  done
  if downloaded="$(install_kbshff_from_release)"; then
    printf '%s' "$downloaded"
    return
  fi
  echo "GitHub release download failed; trying cargo build..." >&2
  if [[ -z "$found" ]]; then
    have git || { echo "kbshff not found and git is missing." >&2; exit 1; }
    have cargo || { echo "kbshff not found. Install cargo or set KBSHFF_BIN. https://github.com/gazalievtimur/Agent-Kuibysheff" >&2; exit 1; }
    found="$parent/Agent-Kuibysheff"
    echo "Cloning Agent-Kuibysheff -> $found"
    git clone --depth 1 https://github.com/gazalievtimur/Agent-Kuibysheff.git "$found"
  fi
  release="$found/target/release/kbshff"
  if [[ -f "$release" ]]; then
    printf '%s' "$release"
    return
  fi
  have cargo || { echo "cargo not found (needed to build kbshff from $found)" >&2; exit 1; }
  echo "Building kbshff from $found"
  (cd "$found" && cargo build --release -p agent_Kuibysheff --bin kbshff)
  [[ -f "$release" ]] || { echo "kbshff missing after cargo build" >&2; exit 1; }
  printf '%s' "$release"
}

indexer_asset_glob() {
  local u
  u="$(uname -s)"
  case "$u" in
    Linux) echo "bsl-indexer-linux-x64.tar.gz" ;;
    Darwin)
      if [[ "$(uname -m)" == "arm64" ]]; then
        echo "bsl-indexer-macos-arm64.tar.gz"
      else
        echo "bsl-indexer-macos-x64.tar.gz"
      fi
      ;;
    *) echo "bsl-indexer-linux-x64.tar.gz" ;;
  esac
}

ensure_indexer() {
  step "bsl-indexer"
  local existing rel dest url archive found stable
  for name in BSL_INDEXER CODE_INDEX_BIN BSL_INDEXER_EXE; do
    existing="$(env_or_file "$name" "$ENV_FILE")"
    if [[ -n "$existing" && -f "$existing" ]]; then
      printf '%s' "$(cd "$(dirname "$existing")" && pwd)/$(basename "$existing")"
      return
    fi
  done
  for rel in bsl-indexer code-index/bsl-indexer; do
    if [[ -f "$TOOLS_DIR/$rel" ]]; then
      printf '%s' "$(cd "$(dirname "$TOOLS_DIR/$rel")" && pwd)/$(basename "$TOOLS_DIR/$rel")"
      return
    fi
  done
  dest="$TOOLS_DIR/code-index"
  mkdir -p "$dest"
  url="$(github_asset_url Regsorm/code-index-mcp "$(indexer_asset_glob)")"
  archive="$(mktemp)"
  download_file "$url" "$archive" "bsl-indexer"
  tar -xzf "$archive" -C "$dest"
  rm -f "$archive"
  found="$(find_under "$dest" bsl-indexer)"
  [[ -n "$found" ]] || { echo "bsl-indexer not found after extract" >&2; exit 1; }
  stable="$TOOLS_DIR/bsl-indexer"
  cp "$found" "$stable"
  chmod +x "$stable"
  printf '%s' "$stable"
}

ensure_jar() {
  step "bsl-language-server JAR (optional)"
  local existing stable home_jar url
  existing="$(env_or_file BSL_LS_JAR "$ENV_FILE")"
  if [[ -n "$existing" && -f "$existing" ]]; then
    printf '%s' "$(cd "$(dirname "$existing")" && pwd)/$(basename "$existing")"
    return
  fi
  stable="$TOOLS_DIR/bsl-ls/bsl-language-server.jar"
  if [[ -f "$stable" ]]; then
    printf '%s' "$stable"
    return
  fi
  home_jar="${HOME}/.claude/bsl-ls/bsl-language-server.jar"
  mkdir -p "$(dirname "$stable")"
  if [[ -f "$home_jar" ]]; then
    cp "$home_jar" "$stable"
    printf '%s' "$stable"
    return
  fi
  if ! url="$(github_asset_url 1c-syntax/bsl-language-server '*-exec.jar' 2>/dev/null)"; then
    echo "Skipping BSL LS JAR download. docs/prerequisites.md" >&2
    printf ''
    return
  fi
  if ! download_file "$url" "$stable" "bsl-language-server JAR"; then
    echo "Skipping BSL LS JAR. docs/prerequisites.md" >&2
    printf ''
    return
  fi
  printf '%s' "$stable"
}

ensure_mcp_js() {
  step "bsl-ls-mcp (optional; needs Node.js)"
  local existing home_js vendor_js
  existing="$(env_or_file BSL_LS_MCP "$ENV_FILE")"
  [[ -n "$existing" ]] || existing="$(env_or_file BSL_LS_SERVER "$ENV_FILE")"
  home_js="${HOME}/.claude/bsl-ls-mcp/server.js"
  vendor_js="$TOOLS_DIR/bsl-ls-mcp/server.js"
  if [[ -n "$existing" && -f "$existing" ]]; then
    printf '%s' "$(cd "$(dirname "$existing")" && pwd)/$(basename "$existing")"
    return
  fi
  if [[ -f "$home_js" ]]; then
    printf '%s' "$home_js"
    return
  fi
  if ! have npm; then
    echo "Skipping tools/bsl-ls-mcp (Node.js/npm not found). docs/prerequisites.md" >&2
    printf ''
    return
  fi
  if [[ ! -f "$vendor_js" ]]; then
    echo "Skipping bsl-ls-mcp: missing $vendor_js" >&2
    printf ''
    return
  fi
  if ! (cd "$TOOLS_DIR/bsl-ls-mcp" && npm install --omit=dev); then
    echo "Skipping bsl-ls-mcp (npm install failed). docs/prerequisites.md" >&2
    printf ''
    return
  fi
  printf '%s' "$vendor_js"
}

find_1c_platform_bins() {
  local root ver bin
  for root in /opt/1cv8/x86_64 /opt/1cv8 /usr/lib/1cv8; do
    [[ -d "$root" ]] || continue
    for ver in "$root"/8.3.*; do
      [[ -d "$ver" ]] || continue
      bin="$ver/bin"
      if [[ -d "$bin" ]] && { [[ -x "$bin/1cv8" ]] || [[ -x "$bin/ibcmd" ]]; }; then
        printf '%s\n' "$bin"
      fi
    done
  done | sort -r
}

select_platform_bin_for_ingest() {
  local bins=() i choice manual skip
  if [[ -n "$PLATFORM_PATH" ]]; then
    printf '%s' "$PLATFORM_PATH"
    return
  fi
  if [[ "$NON_INTERACTIVE" -eq 1 ]]; then
    printf ''
    return
  fi
  hint ""
  hint "Ingest строит индекс справки платформы для MCP sntx_sem (поиск на live-прогоне)."
  hint "Нужен каталог bin лицензионной платформы 1С (обычно .../8.3.xx/bin)."
  hint "HBK в репозиторий не копируется."
  mapfile -t bins < <(find_1c_platform_bins)
  if [[ "${#bins[@]}" -eq 0 ]]; then
    hint "Установленные 8.3.*/bin не найдены автоматически."
    read_default "Путь к bin платформы 1С (пусто = пропуск)" ""
    return
  fi
  echo "Найдены каталоги bin платформы:"
  for i in "${!bins[@]}"; do
    echo "  [$((i + 1))] ${bins[$i]}"
  done
  manual=$((${#bins[@]} + 1))
  skip=$((${#bins[@]} + 2))
  echo "  [$manual] ввести путь вручную"
  echo "  [$skip] пропустить ingest"
  choice="$(read_default "Номер выбора" "1")"
  if [[ "$choice" =~ ^[0-9]+$ ]] && [[ "$choice" -ge 1 && "$choice" -le "${#bins[@]}" ]]; then
    printf '%s' "${bins[$((choice - 1))]}"
    return
  fi
  if [[ "$choice" == "$manual" ]]; then
    read_default "Путь к bin платформы 1С (пусто = пропуск)" ""
    return
  fi
  printf ''
}

ensure_sntx_git_checkout() {
  local src="$1"
  if [[ -f "$src/src/sntx_sem/config.py" || -f "$src/src/sntx_sem/config/__init__.py" ]]; then
    return
  fi
  have git || { echo "1c-sntx-sem missing sntx_sem.config and git is unavailable to checkout $SNTX_SEM_GIT_REF" >&2; exit 1; }
  echo "1c-sntx-sem missing sntx_sem.config. Checking out $SNTX_SEM_GIT_REF" >&2
  [[ -d "$src/.git" ]] || { echo "Cannot repair $src (not a git checkout). Delete it and re-run install." >&2; exit 1; }
  git -C "$src" fetch --depth 1 origin "$SNTX_SEM_GIT_REF"
  git -C "$src" checkout --force FETCH_HEAD
  if [[ ! -f "$src/src/sntx_sem/config.py" && ! -f "$src/src/sntx_sem/config/__init__.py" ]]; then
    echo "1c-sntx-sem still missing sntx_sem.config after checkout $SNTX_SEM_GIT_REF" >&2
    exit 1
  fi
}

clone_sntx_sem() {
  local dest="$1"
  echo "Cloning 1c-sntx-sem @$SNTX_SEM_GIT_REF -> $dest"
  mkdir -p "$dest"
  git -C "$dest" init
  git -C "$dest" remote add origin https://github.com/gybson63/1c-sntx-sem.git
  git -C "$dest" fetch --depth 1 origin "$SNTX_SEM_GIT_REF"
  git -C "$dest" checkout FETCH_HEAD
}

ensure_sntx() {
  step "1c-sntx-sem"
  local existing src parent venv_py config chosen do_ingest setup_ok
  existing="$(env_or_file SNTX_SEM_CONFIG "$ENV_FILE")"
  src=""
  if [[ -n "$existing" && -f "$existing" ]]; then
    src="$(cd "$(dirname "$existing")" && pwd)"
  else
    parent="$(cd "$REPO_ROOT/.." && pwd)"
    for c in "$parent/1c-sntx-sem" "$TOOLS_DIR/1c-sntx-sem"; do
      if [[ -f "$c/pyproject.toml" ]]; then
        src="$(cd "$c" && pwd)"
        break
      fi
    done
  fi
  venv_py=""
  config=""
  if [[ -n "$src" ]]; then
    venv_py="$src/.venv/bin/python"
    config="$src/config.yaml"
  fi
  setup_ok=0
  if step_done sntx_setup && [[ -n "$src" && -x "$venv_py" && -f "$config" ]] \
    && (cd "$src" && "$venv_py" -c "from sntx_sem.config import load_config" >/dev/null 2>&1); then
    setup_ok=1
  fi
  if [[ "$setup_ok" -eq 1 ]]; then
    echo "OK  1c-sntx-sem setup (skipped, checkpoint)"
  else
    if step_done sntx_setup && [[ -n "$src" ]]; then
      echo "Checkpoint sntx_setup present, but sntx_sem import failed - repairing checkout/venv." >&2
    fi
    if [[ -z "$src" ]]; then
      have git || { echo "git not found (needed to clone 1c-sntx-sem)" >&2; exit 1; }
      src="$TOOLS_DIR/1c-sntx-sem"
      clone_sntx_sem "$src"
    fi
    ensure_sntx_git_checkout "$src"
    venv_py="$src/.venv/bin/python"
    if [[ ! -x "$venv_py" ]]; then
      python3 -m venv "$src/.venv"
    fi
    "$venv_py" -m pip install -U pip
    (cd "$src" && "$venv_py" -m pip install -e .)
    if ! (cd "$src" && "$venv_py" -c "from sntx_sem.config import load_config"); then
      echo "1c-sntx-sem import check failed. Try --sntx-sem-git-ref main or delete tools/1c-sntx-sem and re-run." >&2
      exit 1
    fi
    config="$src/config.yaml"
    if [[ ! -f "$config" ]]; then
      [[ -f "$src/config.yaml.example" ]] || { echo "missing config.yaml.example" >&2; exit 1; }
      cp "$src/config.yaml.example" "$config"
      echo "Created $config from example — edit local_configs / ingest as needed."
    fi
    complete_step sntx_setup
  fi
  do_ingest=1
  [[ "$SKIP_INGEST" -eq 1 ]] && do_ingest=0
  step_done ingest && do_ingest=0
  if [[ "$do_ingest" -eq 1 ]]; then
    chosen="$PLATFORM_PATH"
    if [[ -z "$chosen" && -n "$INSTALL_PLATFORM_PATH" ]]; then
      chosen="$INSTALL_PLATFORM_PATH"
    fi
    if [[ -z "$chosen" ]]; then
      chosen="$(select_platform_bin_for_ingest)"
    fi
    if [[ -n "$chosen" ]]; then
      INSTALL_PLATFORM_PATH="$chosen"
      save_install_state
    fi
    if [[ -z "$chosen" ]]; then
      echo "Skipping ingest: no platform path." >&2
      complete_step ingest
    else
      if (cd "$src" && "$venv_py" -m sntx_sem ingest --platform-path "$chosen"); then
        complete_step ingest
      else
        echo "sntx_sem ingest failed (install continues without platform help index)." >&2
        echo "Re-run later: $venv_py -m sntx_sem ingest --platform-path \"$chosen\"" >&2
        echo "Or re-run install.sh to resume from ingest after fixing 1c-sntx-sem." >&2
      fi
    fi
  elif step_done ingest; then
    echo "OK  sntx_sem ingest (skipped, checkpoint)"
  else
    echo "Skipping ingest. Run ingest before a live eval if the index is empty." >&2
    complete_step ingest
  fi
  printf '%s\n%s\n' "$config" "$venv_py"
}

resolve_java_home() {
  local existing detected
  existing="$(env_or_file JAVA_HOME "$ENV_FILE")"
  if [[ -n "$existing" && -d "$existing" ]]; then
    printf '%s' "$existing"
    return
  fi
  if ! have java; then
    echo "Java not found (optional). Default BSL language-server MCP needs JDK 17+. docs/prerequisites.md" >&2
    printf ''
    return
  fi
  detected="$(java -XshowSettings:properties -version 2>&1 | awk -F'= ' '/java.home/ {print $2; exit}')"
  if [[ "$NON_INTERACTIVE" -eq 1 || -z "$detected" ]]; then
    printf '%s' "$detected"
    return
  fi
  hint ""
  hint "JAVA_HOME нужен штатному MCP bsl-language-server (анализ BSL). Можно оставить пустым, если свой MCP без Java."
  hint "Обнаружен Java home: $detected"
  read_default "Путь JAVA_HOME" "$detected"
}

apply_provider() {
  local kbshff="$1" project="$2" agent="$3" base="$4" model="$5" keyenv="$6" label="$7"
  shift 7
  local expected_skills=("$@")
  local staging settings name listed skill
  step "$label kbshff CLI: init / import skills / provider set / check ($agent)"
  mkdir -p "$project"
  "$kbshff" init "$agent" --project-root "$project" --force
  staging="$project/.kuibysheff/.1c-live-import/$agent"
  rm -rf "$staging"
  mkdir -p "$staging"
  settings="$REPO_ROOT/profiles/$agent"
  for name in master_prompt.md skills.dsl rules.md; do
    if [[ ! -f "$settings/$name" ]]; then
      echo "missing $settings/$name — conveyor profile $agent is incomplete" >&2
      exit 1
    fi
    cp "$settings/$name" "$staging/$name"
  done
  "$kbshff" config --project-root "$project" --agent "$agent" import --from "$staging" --force
  "$kbshff" config --project-root "$project" --agent "$agent" provider set \
    --base-url "$base" --model "$model" --api-key-env "$keyenv"
  listed="$("$kbshff" config --project-root "$project" --agent "$agent" --format json skill list)"
  for skill in "${expected_skills[@]}"; do
    if ! grep -F -q "$skill" <<<"$listed"; then
      echo "skill '$skill' missing after import of $agent. skill list: $listed" >&2
      exit 1
    fi
  done
  echo "OK  $agent skills: ${expected_skills[*]}"
  "$kbshff" check --project-root "$project" --agent "$agent" --skip-mcp --skip-sandbox
}

install_conveyor_profiles() {
  local kbshff="$1" project="$2" base="$3" keyenv="$4"
  step "Conveyor profiles (all skills)"
  local agent i=0
  local -a agents=(1c-analyst 1c-yaxunit 1c-coder 1c-implementer)
  local -a skills_analyst=(workspace platform_help conf_docs code_index local_research web_search)
  local -a skills_yaxunit=(workspace yaxunit_docs platform_help code_index bsl_lint local_research web_search)
  local -a skills_coder=(workspace platform_help code_index bsl_lint local_research)
  local -a skills_impl=(workspace platform_help code_index local_research bsl_lint)
  for agent in "${agents[@]}"; do
    i=$((i + 1))
    if step_done "profile:$agent"; then
      echo "OK  profile:$agent (skipped, checkpoint)"
      continue
    fi
    case "$agent" in
      1c-analyst)
        apply_provider "$kbshff" "$project" "$agent" "$base" "${AGENT_MODELS[$agent]}" "$keyenv" "[$i/4]" \
          "${skills_analyst[@]}"
        ;;
      1c-yaxunit)
        apply_provider "$kbshff" "$project" "$agent" "$base" "${AGENT_MODELS[$agent]}" "$keyenv" "[$i/4]" \
          "${skills_yaxunit[@]}"
        ;;
      1c-coder)
        apply_provider "$kbshff" "$project" "$agent" "$base" "${AGENT_MODELS[$agent]}" "$keyenv" "[$i/4]" \
          "${skills_coder[@]}"
        ;;
      1c-implementer)
        apply_provider "$kbshff" "$project" "$agent" "$base" "${AGENT_MODELS[$agent]}" "$keyenv" "[$i/4]" \
          "${skills_impl[@]}"
        ;;
    esac
    complete_step "profile:$agent"
  done
  complete_step profiles
}

agent_model_env_name() {
  # 1c-analyst -> KBSHFF_PROVIDER_MODEL_1C_ANALYST
  local id="$1"
  local suffix
  suffix="$(printf '%s' "$id" | tr '[:lower:]' '[:upper:]' | tr '-' '_')"
  echo "KBSHFF_PROVIDER_MODEL_${suffix}"
}

ENV_FILE="$REPO_ROOT/.env"
initialize_install_resume
mkdir -p "$TOOLS_DIR"

step "Host tools"
require_host git "https://git-scm.com/ — see docs/prerequisites.md"
require_host curl "curl is required to download GitHub releases"
have unzip || { echo "unzip not found (needed to extract kbshff / ovm packages). docs/prerequisites.md" >&2; exit 1; }
echo "OK  unzip"
OSCRIPT_BIN="$(ensure_oscript)"
OPTIONAL_GAPS=()
if have node; then
  echo "OK  node (recommended for BSL LS MCP)"
else
  OPTIONAL_GAPS+=("Node.js (LTS) + npm — штатный tools/bsl-ls-mcp. https://nodejs.org/  (docs/prerequisites.md)")
fi
if have java; then
  echo "OK  java (recommended for BSL LS JAR, JDK 17+)"
else
  OPTIONAL_GAPS+=("Java / JDK 17+ — запуск bsl-language-server JAR. https://adoptium.net/  (docs/prerequisites.md)")
fi
require_host python3 "Python 3 is required for 1c-sntx-sem. docs/prerequisites.md"
if [[ "$SKIP_INGEST" -eq 0 && -z "$PLATFORM_PATH" ]]; then
  mapfile -t _platform_bins < <(find_1c_platform_bins)
  if [[ "${#_platform_bins[@]}" -eq 0 ]]; then
    OPTIONAL_GAPS+=("Платформа 1С (каталог bin 8.3.* с 1cv8/ibcmd) — для ingest sntx_sem. Либо --platform-path, либо --skip-ingest.")
  else
    echo "OK  1C platform bin (found ${#_platform_bins[@]})"
  fi
fi
if step_done host_tools; then
  echo "OK  host tools (skipped optional confirm, checkpoint)"
else
  confirm_optional_host_gaps "${OPTIONAL_GAPS[@]}"
  complete_step host_tools
fi

step "AI provider"
PROVIDER_FROM_CHECKPOINT=0
if step_done provider; then
  [[ -n "$BASE_URL" ]] || BASE_URL="$(env_or_file KBSHFF_PROVIDER_BASE_URL "$ENV_FILE")"
  [[ -n "$BASE_URL" ]] || BASE_URL="https://api.openai.com/v1"
  [[ -n "$API_KEY_ENV_NAME" ]] || API_KEY_ENV_NAME="$(env_or_file KBSHFF_PROVIDER_API_KEY_ENV "$ENV_FILE")"
  [[ -n "$API_KEY_ENV_NAME" ]] || API_KEY_ENV_NAME="OPENAI_API_KEY"
  API_KEY="$(env_or_file "$API_KEY_ENV_NAME" "$ENV_FILE")"
  if [[ -z "$API_KEY" ]]; then
    API_KEY="${!API_KEY_ENV_NAME-}"
  fi
  if [[ -n "$API_KEY" ]]; then
    [[ -n "$MODEL" ]] || MODEL="$(env_or_file KBSHFF_PROVIDER_MODEL "$ENV_FILE")"
    [[ -n "$MODEL" ]] || MODEL="gpt-4o"
    declare -A AGENT_MODELS=()
    for agent in 1c-analyst 1c-yaxunit 1c-coder 1c-implementer; do
      env_name="$(agent_model_env_name "$agent")"
      chosen="$(env_or_file "$env_name" "$ENV_FILE")"
      [[ -n "$chosen" ]] || chosen="$MODEL"
      AGENT_MODELS["$agent"]="$chosen"
    done
    export "$API_KEY_ENV_NAME=$API_KEY"
    echo "OK  AI provider (skipped, checkpoint)"
    PROVIDER_FROM_CHECKPOINT=1
  else
    echo "Checkpoint 'provider' set, but API key for $API_KEY_ENV_NAME missing - asking again." >&2
  fi
fi

if [[ "$PROVIDER_FROM_CHECKPOINT" -eq 0 ]]; then
  if [[ "$NON_INTERACTIVE" -eq 0 ]]; then
    echo ""
    echo "Нужен любой OpenAI-compatible HTTP API (Chat Completions)."
    echo "Эндпоинт (base_url) и ключ - общие; модель задаётся отдельно для каждого агента конвейера."
    echo "Параметры попадут в kbshff через: config provider set --base-url --model --api-key-env"
    echo "Сам ключ хранится только в .env / окружении и НЕ передаётся в argv CLI."
    echo "Значения по умолчанию — плейсхолдеры формата, не рекомендация конкретного вендора."
    echo ""
  fi
  if [[ -z "$BASE_URL" ]]; then
    BASE_URL="$(env_or_file KBSHFF_PROVIDER_BASE_URL "$ENV_FILE")"
    [[ -n "$BASE_URL" ]] || BASE_URL="https://api.openai.com/v1"
    hint "base_url — общий URL эндпоинта до /v1 для всех агентов."
    hint "Пример формата: https://api.example.com/v1"
    BASE_URL="$(read_default "URL эндпоинта (base_url)" "$BASE_URL")"
  fi
  PASTED_API_KEY=""
  if [[ -z "$API_KEY_ENV_NAME" ]]; then
    API_KEY_ENV_NAME="$(env_or_file KBSHFF_PROVIDER_API_KEY_ENV "$ENV_FILE")"
    [[ -n "$API_KEY_ENV_NAME" ]] || API_KEY_ENV_NAME="OPENAI_API_KEY"
    hint ""
    hint "Имя переменной окружения для API-ключа (не сам ключ)."
    hint "Пример: OPENAI_API_KEY. Сам ключ спросим следующим шагом (ввод скрыт)."
    hint "kbshff читает секрет из env с этим именем."
    RAW_ENV_NAME="$(read_default "Имя переменной для API-ключа" "$API_KEY_ENV_NAME")"
    if looks_like_api_key "$RAW_ENV_NAME"; then
      echo "Похоже, вы вставили сам API-ключ вместо имени переменной. Ключ сохраним как секрет; имя env = OPENAI_API_KEY." >&2
      PASTED_API_KEY="$RAW_ENV_NAME"
      API_KEY_ENV_NAME="OPENAI_API_KEY"
      API_KEY_ENV_NAME="$(read_default "Имя переменной для API-ключа" "$API_KEY_ENV_NAME")"
    else
      API_KEY_ENV_NAME="$RAW_ENV_NAME"
    fi
    if ! valid_env_var_name "$API_KEY_ENV_NAME"; then
      echo "Invalid API key env var name '$API_KEY_ENV_NAME'. Use something like OPENAI_API_KEY." >&2
      exit 1
    fi
  fi
  API_KEY="$PASTED_API_KEY"
  if [[ -z "$API_KEY" ]]; then
    API_KEY="$(env_or_file "$API_KEY_ENV_NAME" "$ENV_FILE")"
  fi
  if [[ -z "$API_KEY" ]]; then
    hint ""
    hint "Значение ключа для переменной ${API_KEY_ENV_NAME}."
    hint "Ввод скрыт (символы не видны). Вставьте ключ и нажмите Enter."
    attempt=1
    while [[ $attempt -le 3 ]]; do
      API_KEY="$(read_secret "Значение API-ключа (${API_KEY_ENV_NAME})")"
      [[ -n "$API_KEY" ]] && break
      echo "Пустой ввод (попытка $attempt/3). Вставьте ключ ещё раз — символы не отображаются." >&2
      attempt=$((attempt + 1))
    done
  fi
  if [[ -z "$API_KEY" ]]; then
    echo "API key for $API_KEY_ENV_NAME is required" >&2
    exit 1
  fi
  export "$API_KEY_ENV_NAME=$API_KEY"

  if [[ -z "$MODEL" ]]; then
    MODEL="$(env_or_file KBSHFF_PROVIDER_MODEL "$ENV_FILE")"
  fi
  [[ -n "$MODEL" ]] || MODEL="gpt-4o"

  declare -A AGENT_MODELS=()
  declare -A CLI_MODELS=(
    ["1c-analyst"]="$MODEL_ANALYST"
    ["1c-yaxunit"]="$MODEL_YAXUNIT"
    ["1c-coder"]="$MODEL_CODER"
    ["1c-implementer"]="$MODEL_IMPLEMENTER"
  )
  hint ""
  hint "model — id модели у провайдера. Один эндпоинт, но модель можно выбрать разной для каждой стадии."
  hint "Плейсхолдер формата: gpt-4o (Enter — принять значение в скобках)."
  for agent in 1c-analyst 1c-yaxunit 1c-coder 1c-implementer; do
    env_name="$(agent_model_env_name "$agent")"
    chosen="${CLI_MODELS[$agent]}"
    if [[ -z "$chosen" ]]; then
      chosen="$(env_or_file "$env_name" "$ENV_FILE")"
    fi
    if [[ -z "$chosen" ]]; then
      chosen="$MODEL"
    fi
    chosen="$(read_default "Модель для $agent" "$chosen")"
    if [[ -z "$chosen" ]]; then
      echo "model for $agent is required" >&2
      exit 1
    fi
    AGENT_MODELS["$agent"]="$chosen"
  done
  complete_step provider
fi

KBSHFF_BIN="$(ensure_kbshff)"
complete_step kbshff
BSL_INDEXER="$(ensure_indexer)"
complete_step indexer
BSL_LS_MCP="$(ensure_mcp_js)"
BSL_LS_JAR=""
if [[ -n "$BSL_LS_MCP" ]] || [[ -n "$(env_or_file BSL_LS_JAR "$ENV_FILE")" ]]; then
  BSL_LS_JAR="$(ensure_jar)"
else
  echo "Skipping BSL LS JAR (no bsl-ls-mcp path). Set BSL_LS_MCP / install Node, or use your own MCP."
fi
complete_step bsl
SNTX_OUT="$(ensure_sntx)"
SNTX_SEM_CONFIG="$(printf '%s\n' "$SNTX_OUT" | sed -n '1p')"
SNTX_SEM_PYTHON="$(printf '%s\n' "$SNTX_OUT" | sed -n '2p')"
JAVA_HOME_VAL=""
if [[ -n "$BSL_LS_JAR" || -n "$BSL_LS_MCP" ]]; then
  JAVA_HOME_VAL="$(resolve_java_home || true)"
fi

{
  echo "KBSHFF_PROVIDER_BASE_URL=$BASE_URL"
  echo "KBSHFF_PROVIDER_MODEL=$MODEL"
  echo "KBSHFF_PROVIDER_MODEL_1C_ANALYST=${AGENT_MODELS[1c-analyst]}"
  echo "KBSHFF_PROVIDER_MODEL_1C_YAXUNIT=${AGENT_MODELS[1c-yaxunit]}"
  echo "KBSHFF_PROVIDER_MODEL_1C_CODER=${AGENT_MODELS[1c-coder]}"
  echo "KBSHFF_PROVIDER_MODEL_1C_IMPLEMENTER=${AGENT_MODELS[1c-implementer]}"
  echo "KBSHFF_PROVIDER_API_KEY_ENV=$API_KEY_ENV_NAME"
  echo "${API_KEY_ENV_NAME}=$API_KEY"
  echo "SNTX_SEM_CONFIG=$SNTX_SEM_CONFIG"
  echo "SNTX_SEM_PYTHON=$SNTX_SEM_PYTHON"
  echo "BSL_INDEXER=$BSL_INDEXER"
  echo "CODE_INDEX_HOME=$(dirname "$BSL_INDEXER")"
  echo "BSL_LS_MCP=$BSL_LS_MCP"
  echo "BSL_LS_JAR=$BSL_LS_JAR"
  echo "KBSHFF_BIN=$KBSHFF_BIN"
  echo "OSCRIPT_BIN=$OSCRIPT_BIN"
  echo "JAVA_HOME=$JAVA_HOME_VAL"
} | dotenv_set_many "$ENV_FILE"
if step_done env; then
  echo "OK  .env (refreshed, checkpoint)"
else
  echo "Wrote $ENV_FILE"
  complete_step env
fi

export KBSHFF_PROVIDER_BASE_URL="$BASE_URL"
export KBSHFF_PROVIDER_MODEL="$MODEL"
export KBSHFF_PROVIDER_MODEL_1C_ANALYST="${AGENT_MODELS[1c-analyst]}"
export KBSHFF_PROVIDER_MODEL_1C_YAXUNIT="${AGENT_MODELS[1c-yaxunit]}"
export KBSHFF_PROVIDER_MODEL_1C_CODER="${AGENT_MODELS[1c-coder]}"
export KBSHFF_PROVIDER_MODEL_1C_IMPLEMENTER="${AGENT_MODELS[1c-implementer]}"
export KBSHFF_PROVIDER_API_KEY_ENV="$API_KEY_ENV_NAME"
export SNTX_SEM_CONFIG BSL_INDEXER KBSHFF_BIN OSCRIPT_BIN SNTX_SEM_PYTHON
[[ -n "$BSL_LS_MCP" ]] && export BSL_LS_MCP
[[ -n "$BSL_LS_JAR" ]] && export BSL_LS_JAR
[[ -n "$JAVA_HOME_VAL" ]] && export JAVA_HOME="$JAVA_HOME_VAL"

install_conveyor_profiles "$KBSHFF_BIN" "$REPO_ROOT" "$BASE_URL" "$API_KEY_ENV_NAME"

step "harness dry-run"
if step_done dry_run; then
  echo "OK  harness dry-run (skipped, checkpoint)"
else
  "$OSCRIPT_BIN" -encoding=utf-8 "$REPO_ROOT/harness/run.os" --repo-root "$REPO_ROOT" --dry-run
  complete_step dry_run
fi

clear_install_state

echo ""
echo "Install OK. Conveyor is ready."
echo "Profiles with skills: 1c-analyst, 1c-yaxunit, 1c-coder, 1c-implementer"
echo "Live eval:  ./harness/run.sh"
echo "Howto:      docs/howto-pipeline.md"
echo "CLI help:   kbshff help config"
