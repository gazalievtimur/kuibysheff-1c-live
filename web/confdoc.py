"""HTTP client for the in-container 1c-conf-doc API."""

from __future__ import annotations

import os
from urllib.parse import quote

import httpx

BASE = os.environ.get("CONF_DOC_API_URL", "http://127.0.0.1:18050").rstrip("/")


def _url(path: str) -> str:
    return BASE + path


def health() -> dict:
    response = httpx.get(_url("/health"), timeout=5)
    response.raise_for_status()
    data = response.json()
    return data if isinstance(data, dict) else {"ok": True}


def configurations() -> list:
    response = httpx.get(_url("/configurations"), timeout=15)
    response.raise_for_status()
    data = response.json()
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("configurations", "items", "results"):
            if isinstance(data.get(key), list):
                return data[key]
    return []


def ensure_slot(name: str) -> None:
    response = httpx.post(_url("/configurations"), json={"name": name}, timeout=60)
    if response.status_code in (200, 201, 409):
        return
    text = response.text.lower()
    if response.status_code == 400 and ("exist" in text or "уже" in text or "существ" in text):
        return
    response.raise_for_status()


def import_path(name: str, source: str) -> None:
    response = httpx.post(
        _url(f"/configurations/{quote(name, safe='')}/import-path"),
        json={"source": source, "mirror": False},
        timeout=180,
    )
    response.raise_for_status()


def start_index(name: str, skip_embeddings: bool) -> str:
    response = httpx.post(
        _url(f"/configurations/{quote(name, safe='')}/index"),
        json={"skip_embeddings": skip_embeddings},
        timeout=60,
    )
    response.raise_for_status()
    return _job_id(response.json())


def job(job_id: str) -> dict:
    response = httpx.get(_url(f"/configurations/jobs/{quote(job_id, safe='')}"), timeout=30)
    response.raise_for_status()
    data = response.json()
    return data if isinstance(data, dict) else {"raw": data}


def delete(name: str) -> None:
    response = httpx.delete(_url(f"/configurations/{quote(name, safe='')}"), timeout=60)
    if response.status_code == 404:
        return
    response.raise_for_status()


def _job_id(payload) -> str:
    if isinstance(payload, str):
        return payload
    if not isinstance(payload, dict):
        return ""
    for key in ("id", "job_id"):
        if payload.get(key):
            return str(payload[key])
    nested = payload.get("job")
    if isinstance(nested, dict) and nested.get("id"):
        return str(nested["id"])
    return ""


def job_finished(payload: dict) -> bool:
    status = str(payload.get("status") or payload.get("state") or "").lower()
    if payload.get("done") is True or payload.get("finished") is True:
        return True
    return status in {"done", "success", "succeeded", "completed", "complete", "error", "failed", "failure"}


def job_ok(payload: dict) -> bool:
    status = str(payload.get("status") or payload.get("state") or "").lower()
    if status in {"error", "failed", "failure"}:
        return False
    if payload.get("error"):
        return False
    return True
