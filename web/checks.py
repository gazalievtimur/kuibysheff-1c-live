"""Probe the operator's OpenAI-compatible endpoints."""

from __future__ import annotations

import httpx


def check_models(base_url: str, api_key: str) -> tuple[bool, str]:
    url = base_url.rstrip("/") + "/models"
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    try:
        response = httpx.get(url, headers=headers, timeout=20)
    except Exception as exc:
        return False, str(exc)
    if response.status_code >= 400:
        return False, f"HTTP {response.status_code}: {response.text[:300]}"
    return True, f"HTTP {response.status_code}"


def check_embeddings(base_url: str, api_key: str, model: str) -> tuple[bool, str]:
    url = base_url.rstrip("/") + "/embeddings"
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    body = {"model": model, "input": "ping"}
    try:
        response = httpx.post(url, headers=headers, json=body, timeout=40)
    except Exception as exc:
        return False, str(exc)
    if response.status_code >= 400:
        return False, f"HTTP {response.status_code}: {response.text[:300]}"
    try:
        data = response.json()
        dim = len(data["data"][0]["embedding"])
    except Exception:
        dim = 0
    return True, f"HTTP {response.status_code}, размерность {dim}" if dim else f"HTTP {response.status_code}"
