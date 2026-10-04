"""One live-eval at a time. Extra tasks wait in a queue."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import threading
import time
import uuid
from pathlib import Path

from web.filesetup import AGENTS, DATA, load_settings

_lock = threading.Lock()
_queue: list[dict] = []
_current: dict | None = None
_process: subprocess.Popen | None = None
_worker_started = False


def snapshot() -> dict:
    with _lock:
        return {
            "current": _public(_current) if _current else None,
            "queued": [_public(item) for item in _queue],
        }


def submit(spec: dict) -> dict:
    job = {
        "id": time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6],
        "title": spec["title"],
        "brief": spec["brief"],
        "config_id": spec["config_id"],
        "product_id": spec["product_id"],
        "product_name": spec["product_name"],
        "cf_dir": spec["cf_dir"],
        "conf_name": spec["conf_name"],
        "with_searxng": bool(spec.get("with_searxng", True)),
        "require_platform": bool(spec.get("require_platform")),
        "status": "queued",
        "error": "",
        "run_dir": "",
        "log": "",
    }
    log_path = DATA / "jobs" / f"{job['id']}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("", encoding="utf-8")
    job["log"] = str(log_path)
    with _lock:
        _queue.append(job)
        _ensure_worker()
    return _public(job)


def stop() -> None:
    global _process
    with _lock:
        proc = _process
    if proc is None or proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except OSError:
        proc.terminate()


def _ensure_worker() -> None:
    global _worker_started
    if _worker_started:
        return
    _worker_started = True
    threading.Thread(target=_loop, name="eval-worker", daemon=True).start()


def _loop() -> None:
    global _current, _process
    while True:
        with _lock:
            if not _queue:
                _current = None
                _worker_started_reset()
                return
            job = _queue.pop(0)
            job["status"] = "running"
            _current = job
        try:
            _run(job)
        except Exception as exc:
            job["status"] = "error"
            job["error"] = str(exc)
            _append(job, f"\nERROR: {exc}\n")
        finally:
            with _lock:
                _process = None
                if job.get("status") == "running":
                    job["status"] = "finished"


def _worker_started_reset() -> None:
    global _worker_started
    _worker_started = False


def _run(job: dict) -> None:
    global _process
    bank = DATA / "tasks" / job["id"]
    bank.mkdir(parents=True, exist_ok=True)
    task = {
        "id": job["id"],
        "title": job["title"],
        "brief": job["brief"],
        "stages": ["analyst", "yaxunit", "coder", "implementer"],
        "expect": {},
    }
    (bank / f"{job['id']}.json").write_text(json.dumps(task, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cmd = [
        os.environ.get("OSCRIPT_BIN", "oscript"),
        "-encoding=utf-8",
        "/app/harness/run.os",
        "--repo-root", "/app",
        "--bank-dir", str(bank),
        "--task-id", job["id"],
        "--cf-dir", job["cf_dir"],
        "--runs-root", str(DATA / "runs"),
        "--product-id", job["product_id"],
        "--product-name", job["product_name"],
        "--skip-build",
    ]
    if job.get("conf_name"):
        cmd.extend(["--conf-doc-configuration", job["conf_name"]])
    if job["with_searxng"]:
        cmd.append("--with-searxng")
    if job["require_platform"]:
        cmd.append("--require-platform")
    env = os.environ.copy()
    env.update(_provider_env())
    env["KUIBYSHEFF_ALLOW_UNSANDBOXED_MCP"] = "1"
    _append(job, "$ " + " ".join(cmd) + "\n")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
        start_new_session=True,
        cwd="/app",
    )
    with _lock:
        _process = proc
    assert proc.stdout is not None
    for line in proc.stdout:
        _append(job, line)
    code = proc.wait()
    latest = (Path("/app/harness/runs/LATEST")).read_text(encoding="utf-8").strip() if Path("/app/harness/runs/LATEST").is_file() else ""
    # Harness writes LATEST inside the repo harness/runs unless --runs-root is honored.
    runs_latest = DATA / "runs" / "LATEST"
    if runs_latest.is_file():
        latest = runs_latest.read_text(encoding="utf-8").strip()
    job["run_dir"] = latest
    job["exit_code"] = code
    job["status"] = "passed" if code == 0 else "failed"
    _append(job, f"\nexit {code}\n")


def _provider_env() -> dict[str, str]:
    settings = load_settings()
    llm = settings.get("llm") or {}
    key_env = llm.get("api_key_env") or "OPENAI_API_KEY"
    models = llm.get("models") or {}
    env = {
        "KBSHFF_PROVIDER_BASE_URL": llm.get("base_url") or "https://api.openai.com/v1",
        "KBSHFF_PROVIDER_API_KEY_ENV": key_env,
        "KBSHFF_PROVIDER_MODEL": models.get("1c-analyst") or "gpt-4o",
        key_env: llm.get("api_key") or "",
    }
    for agent in AGENTS:
        env["KBSHFF_PROVIDER_MODEL_" + agent.upper().replace("-", "_")] = models.get(agent) or env["KBSHFF_PROVIDER_MODEL"]
    return env


def _append(job: dict, text: str) -> None:
    path = Path(job["log"])
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)


def _public(job: dict | None) -> dict | None:
    if job is None:
        return None
    return {key: job.get(key) for key in (
        "id", "title", "config_id", "status", "error", "run_dir", "exit_code", "with_searxng", "require_platform",
    )}


def read_log(job_id: str, offset: int) -> tuple[str, int]:
    path = DATA / "jobs" / f"{job_id}.log"
    if not path.is_file():
        return "", offset
    data = path.read_text(encoding="utf-8", errors="replace")
    if offset > len(data):
        offset = 0
    return data[offset:], len(data)


def job_status(job_id: str) -> str:
    with _lock:
        if _current and _current.get("id") == job_id:
            return str(_current.get("status") or "running")
        for item in _queue:
            if item.get("id") == job_id:
                return "queued"
    return "done"
