"""Health of the processes that share this container."""

from __future__ import annotations

import os
import socket
import subprocess
from pathlib import Path

import httpx


def _tcp(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1.5):
            return True
    except OSError:
        return False


def _get(url: str) -> tuple[bool, str]:
    try:
        response = httpx.get(url, timeout=4)
        if response.status_code < 500:
            return True, f"HTTP {response.status_code}"
        return False, f"HTTP {response.status_code}"
    except Exception as exc:
        return False, str(exc)


def platform_bins() -> list[str]:
    found = []
    root = Path("/opt/1cv8")
    if not root.is_dir():
        return found
    for ibcmd in root.rglob("ibcmd"):
        if ibcmd.is_file() and os.access(ibcmd, os.X_OK):
            found.append(str(ibcmd.parent))
    return sorted(set(found))


def collect() -> list[dict]:
    indexer = os.environ.get("BSL_INDEXER", "/opt/tools/bsl-indexer")
    try:
        result = subprocess.run([indexer, "daemon", "status"], capture_output=True, text=True, timeout=8)
        code_ok = result.returncode == 0
        code_detail = (result.stdout or result.stderr or "").strip().splitlines()
        code_detail = code_detail[-1] if code_detail else f"exit {result.returncode}"
    except Exception as exc:
        code_ok, code_detail = False, str(exc)

    conf_ok, conf_detail = _get("http://127.0.0.1:18050/health")
    sntx_ok, sntx_detail = _get("http://127.0.0.1:18051/health")
    if not sntx_ok:
        sntx_ok, sntx_detail = _get("http://127.0.0.1:18051/")
    searx_ok, searx_detail = _get("http://127.0.0.1:18888/search?q=test&format=json")
    mcp_ok = _tcp(3000)
    bins = platform_bins()
    return [
        {"id": "code-index", "title": "code-index", "ok": code_ok, "detail": code_detail, "href": ""},
        {"id": "conf-doc", "title": "1c-conf-doc", "ok": conf_ok, "detail": conf_detail, "href_port": 8050, "href_path": "/"},
        {"id": "sntx-sem", "title": "1c-sntx-sem", "ok": sntx_ok, "detail": sntx_detail, "href_port": 8051, "href_path": "/admin"},
        {"id": "searxng", "title": "SearXNG", "ok": searx_ok, "detail": searx_detail, "href_port": 8888, "href_path": "/"},
        {"id": "mcp-searxng", "title": "mcp-searxng", "ok": mcp_ok, "detail": "127.0.0.1:3000" if mcp_ok else "порт 3000 закрыт", "href": ""},
        {
            "id": "platform",
            "title": "Платформа 1С",
            "ok": bool(bins),
            "detail": bins[0] if bins else "не смонтирована (/opt/1cv8)",
            "href": "",
            "bins": bins,
        },
    ]
