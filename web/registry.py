"""Registered 1C configuration dumps."""

from __future__ import annotations

import json
import shutil
import threading
from pathlib import Path

from web import codeindex, confdoc
from web.cfmeta import configuration_name, dump_root
from web.filesetup import DATA, REGISTRY_PATH, load_settings

_lock = threading.Lock()


def load() -> list[dict]:
    if not REGISTRY_PATH.is_file():
        return []
    try:
        rows = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return rows if isinstance(rows, list) else []


def save(rows: list[dict]) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get(config_id: str) -> dict | None:
    for row in load():
        if row.get("id") == config_id:
            return row
    return None


def update(config_id: str, **fields) -> None:
    with _lock:
        rows = load()
        for row in rows:
            if row.get("id") == config_id:
                row.update(fields)
                save(rows)
                return


def embeddings_configured() -> bool:
    emb = load_settings().get("embeddings") or {}
    return bool(emb.get("api_key") and emb.get("base_url") and (emb.get("model") or emb.get("model_confdoc")))


def index_config(row: dict) -> None:
    name = row["conf_name"]
    source = str(Path(row["path"]).resolve())
    skip = not embeddings_configured()
    update(row["id"], status="indexing", error="", embeddings=not skip)
    try:
        codeindex.add(Path(source))
        try:
            codeindex.reload()
        except Exception as exc:
            update(row["id"], error=f"code-index: {exc}")
        confdoc.ensure_slot(name)
        confdoc.import_path(name, source)
        job_id = confdoc.start_index(name, skip_embeddings=skip)
        update(row["id"], job_id=job_id or "", status="indexing" if job_id else "ready")
        if job_id:
            _watch_job(row["id"], job_id, with_embeddings=not skip)
        else:
            update(row["id"], status="ready", embeddings=not skip)
    except Exception as exc:
        update(row["id"], status="error", error=str(exc))


def _watch_job(config_id: str, job_id: str, with_embeddings: bool) -> None:
    def run() -> None:
        import time

        for _ in range(720):
            time.sleep(5)
            try:
                payload = confdoc.job(job_id)
            except Exception as exc:
                update(config_id, status="error", error=str(exc))
                return
            if not confdoc.job_finished(payload):
                continue
            if confdoc.job_ok(payload):
                update(config_id, status="ready", embeddings=with_embeddings, error="")
            else:
                update(config_id, status="error", error=str(payload.get("error") or payload.get("status") or payload))
            return
        update(config_id, status="error", error="индексация не завершилась за час")

    threading.Thread(target=run, name=f"confdoc-{config_id}", daemon=True).start()


def register_upload(dest: Path) -> dict:
    root = dump_root(dest)
    if root is None:
        raise ValueError("В архиве нет Configuration.xml")
    if root != dest:
        # Zip extracted into dest; move the dump root up if it is a single child.
        pass
    name = configuration_name(root)
    config_id = _unique_id(name)
    final = DATA / "configs" / config_id
    if root.resolve() != final.resolve():
        if final.exists():
            shutil.rmtree(final)
        shutil.move(str(root), str(final))
        if dest.exists() and dest.resolve() != final.resolve():
            shutil.rmtree(dest, ignore_errors=True)
    row = {
        "id": config_id,
        "product_id": config_id,
        "product_name": name,
        "path": str(final),
        "builtin": False,
        "conf_name": name,
        "status": "pending",
        "embeddings": False,
        "job_id": "",
        "error": "",
    }
    with _lock:
        rows = load()
        rows.append(row)
        save(rows)
    threading.Thread(target=index_config, args=(row,), daemon=True).start()
    return row


def delete(config_id: str) -> None:
    row = get(config_id)
    if row is None or row.get("builtin"):
        raise ValueError("эту конфигурацию нельзя удалить")
    try:
        confdoc.delete(row["conf_name"])
    except Exception:
        pass
    try:
        codeindex.remove(Path(row["path"]))
        codeindex.reload()
    except Exception:
        pass
    path = Path(row["path"])
    if path.is_dir() and not row.get("builtin"):
        shutil.rmtree(path, ignore_errors=True)
    with _lock:
        save([item for item in load() if item.get("id") != config_id])


def resume_job(config_id: str, job_id: str, with_embeddings: bool) -> None:
    _watch_job(config_id, job_id, with_embeddings)


def reindex_all() -> None:
    for row in load():
        threading.Thread(target=index_config, args=(row,), daemon=True).start()


def _unique_id(name: str) -> str:
    base = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in name).strip("-") or "config"
    existing = {row.get("id") for row in load()}
    if base not in existing:
        return base
    n = 2
    while f"{base}-{n}" in existing:
        n += 1
    return f"{base}-{n}"
