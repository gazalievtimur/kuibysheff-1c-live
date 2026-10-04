"""First-boot layout for /data: configs, Caddy, SearXNG secret, daemon.toml."""

from __future__ import annotations

import json
import os
import secrets
import subprocess
from pathlib import Path

DATA = Path(os.environ.get("DATA_DIR", "/data"))
APP = Path(os.environ.get("REPO_ROOT", "/app"))
SETTINGS_PATH = DATA / "settings.json"
REGISTRY_PATH = DATA / "configs" / "registry.json"

AGENTS = ("1c-analyst", "1c-yaxunit", "1c-coder", "1c-implementer")


def embeddings_api_key() -> str:
    settings = load_settings()
    return str(settings.get("embeddings", {}).get("api_key") or "")


def load_settings() -> dict:
    if not SETTINGS_PATH.is_file():
        return {}
    try:
        return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_settings(settings: dict) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def default_settings() -> dict:
    llm_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY") or ""
    llm_url = os.environ.get("KBSHFF_PROVIDER_BASE_URL") or os.environ.get("LLM_BASE_URL") or "https://api.openai.com/v1"
    model = os.environ.get("KBSHFF_PROVIDER_MODEL") or "gpt-4o"
    models = {}
    for agent in AGENTS:
        env_name = "KBSHFF_PROVIDER_MODEL_" + agent.upper().replace("-", "_")
        models[agent] = os.environ.get(env_name) or model
    embed_url = os.environ.get("EMBEDDINGS_BASE_URL") or llm_url
    embed_key = os.environ.get("EMBEDDINGS_API_KEY") or llm_key
    embed_model = os.environ.get("EMBEDDINGS_MODEL") or "text-embedding-3-small"
    return {
        "llm": {
            "base_url": llm_url,
            "api_key_env": os.environ.get("KBSHFF_PROVIDER_API_KEY_ENV") or "OPENAI_API_KEY",
            "api_key": llm_key,
            "models": models,
        },
        "embeddings": {
            "base_url": embed_url,
            "api_key": embed_key,
            "model": embed_model,
            "model_sntx": os.environ.get("EMBEDDINGS_MODEL_SNTX") or "",
            "model_confdoc": os.environ.get("EMBEDDINGS_MODEL_CONFDOC") or "",
        },
    }


def render_sntx(settings: dict) -> str:
    emb = settings.get("embeddings") or {}
    model = emb.get("model_sntx") or emb.get("model") or "text-embedding-3-small"
    base = emb.get("base_url") or "https://api.openai.com/v1"
    return f"""platform_version: "8.3.27"
hbk_dir: /data/sntx-sem/hbk
data_dir: /data/sntx-sem/data
export_dir: /data/sntx-sem/data/export
index_dir: /data/sntx-sem/data/index

local_configs: []

bsp:
  enabled: false

embedding:
  provider: openai_compatible
  base_url: "{base}"
  model: "{model}"
  api_key_env: "EMBEDDINGS_API_KEY"
  query_prefix: ""
  passage_prefix: ""
  batch_size: 16
  timeout: 600

api:
  host: 127.0.0.1
  port: 18051

search:
  build_vector_index: false

mcp:
  log_level: INFO
  log_file: ""
"""


def render_confdoc(settings: dict) -> str:
    emb = settings.get("embeddings") or {}
    model = emb.get("model_confdoc") or emb.get("model") or "text-embedding-3-small"
    base = emb.get("base_url") or "https://api.openai.com/v1"
    key = str(emb.get("api_key") or "").replace("\\", "\\\\").replace('"', '\\"')
    return f"""source: /data/configs
output: /data/conf-doc/output

configuration: null

import_roots:
  - /app/harness/cf
  - /data/configs

embeddings:
  provider: openai
  base_url: "{base}"
  model: "{model}"
  openai_api_key: "{key}"

faiss:
  index_type: flat

chunking:
  max_tokens: 1500
  overlap_tokens: 100

llm:
  provider: none

api:
  host: 127.0.0.1
  port: 18050
"""


def write_service_configs(settings: dict) -> None:
    sntx = DATA / "sntx-sem" / "config.yaml"
    conf = DATA / "conf-doc" / "config.yaml"
    sntx.parent.mkdir(parents=True, exist_ok=True)
    conf.parent.mkdir(parents=True, exist_ok=True)
    sntx.write_text(render_sntx(settings), encoding="utf-8")
    conf.write_text(render_confdoc(settings), encoding="utf-8")


def write_searx() -> None:
    dest = DATA / "searxng" / "settings.yml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    template = (APP / "docker" / "searxng" / "settings.yml").read_text(encoding="utf-8")
    if dest.is_file() and "CHANGE_ME" not in dest.read_text(encoding="utf-8"):
        return
    secret = secrets.token_hex(32)
    dest.write_text(template.replace("CHANGE_ME", secret), encoding="utf-8")


def write_daemon() -> None:
    path = DATA / "code-index" / "daemon.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        return
    path.write_text(
        "[daemon]\nhttp_port = 0\nmax_concurrent_initial = 1\n",
        encoding="utf-8",
    )


def write_caddy() -> None:
    dest = DATA / "caddy" / "Caddyfile"
    dest.parent.mkdir(parents=True, exist_ok=True)
    password = os.environ.get("WEB_PASSWORD") or ""
    user = os.environ.get("WEB_USER") or "admin"
    auth = ""
    if password:
        hashed = subprocess.check_output(
            ["caddy", "hash-password", "--plaintext", password],
            text=True,
        ).strip()
        auth = f"\tbasic_auth {{\n\t\t{user} {hashed}\n\t}}\n"
    else:
        print("WEB_PASSWORD is empty: Caddy will not require authentication.", flush=True)
    sites = [
        (8080, "127.0.0.1:18080"),
        (8050, "127.0.0.1:18050"),
        (8051, "127.0.0.1:18051"),
        (8888, "127.0.0.1:18888"),
    ]
    blocks = ["{\n\tadmin off\n\tauto_https off\n}\n"]
    for port, upstream in sites:
        blocks.append(
            f":{port} {{\n{auth}\treverse_proxy {upstream}\n}}\n"
        )
    dest.write_text("\n".join(blocks), encoding="utf-8")


def ensure_registry() -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    if REGISTRY_PATH.is_file():
        try:
            rows = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            rows = []
    if not any(row.get("id") == "sklad" for row in rows):
        from web.cfmeta import configuration_name

        cf = APP / "harness" / "cf"
        rows.insert(0, {
            "id": "sklad",
            "product_id": "sklad",
            "product_name": "Склад",
            "path": str(cf),
            "builtin": True,
            "conf_name": configuration_name(cf),
            "status": "pending",
            "embeddings": False,
            "job_id": "",
            "error": "",
        })
        REGISTRY_PATH.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    for name in (
        "logs", "code-index", "configs", "tasks", "runs",
        "sntx-sem/hbk", "sntx-sem/data", "conf-doc/output", "searxng", "caddy", "jobs",
    ):
        (DATA / name).mkdir(parents=True, exist_ok=True)
    if not SETTINGS_PATH.is_file():
        save_settings(default_settings())
    write_service_configs(load_settings() or default_settings())
    write_searx()
    write_daemon()
    write_caddy()
    ensure_registry()


if __name__ == "__main__":
    main()
