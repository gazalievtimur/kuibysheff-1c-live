"""Portal: provider settings, configuration choice, free-text tasks, run results."""

from __future__ import annotations

import asyncio
import io
import json
import shutil
import subprocess
import threading
import zipfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from web import checks, codeindex, registry, runner, services
from web.cfmeta import dump_root
from web.filesetup import AGENTS, DATA, load_settings, save_settings, write_service_configs

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
app = FastAPI(title="kuibysheff-1c-live")


@app.on_event("startup")
def _startup() -> None:
    def later() -> None:
        import time

        for _ in range(60):
            try:
                services.collect()
                ok = next(item["ok"] for item in services.collect() if item["id"] == "conf-doc")
            except Exception:
                ok = False
            if ok:
                break
            time.sleep(2)
        try:
            codeindex.reload()
        except Exception:
            pass
        for row in registry.load():
            if row.get("status") in {"pending", "error", ""}:
                registry.index_config(row)
            elif row.get("status") == "indexing" and row.get("job_id"):
                registry.resume_job(row["id"], row["job_id"], bool(row.get("embeddings")))

    threading.Thread(target=later, name="bootstrap-index", daemon=True).start()


def _ctx(request: Request, **extra):
    host = request.url.hostname or "127.0.0.1"
    scheme = request.url.scheme
    extra["ui"] = {
        "confdoc": f"{scheme}://{host}:8050/",
        "sntx": f"{scheme}://{host}:8051/admin",
        "searx": f"{scheme}://{host}:8888/",
    }
    extra["job"] = runner.snapshot()
    return {"request": request, **extra}


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    rows = services.collect()
    bins = []
    for row in rows:
        if row["id"] == "platform":
            bins = row.get("bins") or []
    hint = ""
    if bins:
        hint = f"docker exec <container> sntx-sem ingest --platform-path {bins[0]}"
    return TEMPLATES.TemplateResponse(request, "services.html", _ctx(request, services=rows, ingest_hint=hint))


@app.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request, notice: str = "", error: str = ""):
    settings = load_settings()
    return TEMPLATES.TemplateResponse(
        request,
        "settings.html",
        _ctx(request, settings=settings, agents=AGENTS, notice=notice, error=error),
    )


@app.post("/settings/llm")
def save_llm(
    base_url: str = Form(...),
    api_key_env: str = Form(...),
    api_key: str = Form(""),
    keep_key: str = Form(""),
    analyst: str = Form(...),
    yaxunit: str = Form(...),
    coder: str = Form(...),
    implementer: str = Form(...),
):
    settings = load_settings()
    llm = settings.setdefault("llm", {})
    llm["base_url"] = base_url.strip()
    llm["api_key_env"] = api_key_env.strip() or "OPENAI_API_KEY"
    if api_key.strip():
        llm["api_key"] = api_key.strip()
    elif keep_key != "1":
        llm["api_key"] = ""
    llm["models"] = {
        "1c-analyst": analyst.strip(),
        "1c-yaxunit": yaxunit.strip(),
        "1c-coder": coder.strip(),
        "1c-implementer": implementer.strip(),
    }
    save_settings(settings)
    return RedirectResponse("/settings?notice=LLM+сохранён", status_code=303)


@app.post("/settings/llm/check")
def check_llm():
    llm = load_settings().get("llm") or {}
    ok, detail = checks.check_models(llm.get("base_url") or "", llm.get("api_key") or "")
    target = "/settings?notice=" if ok else "/settings?error="
    return RedirectResponse(target + _q(detail), status_code=303)


@app.post("/settings/embeddings")
def save_embeddings(
    base_url: str = Form(...),
    api_key: str = Form(""),
    keep_key: str = Form(""),
    model: str = Form(...),
    model_sntx: str = Form(""),
    model_confdoc: str = Form(""),
):
    settings = load_settings()
    previous = json.dumps(settings.get("embeddings") or {}, sort_keys=True)
    emb = settings.setdefault("embeddings", {})
    emb["base_url"] = base_url.strip()
    if api_key.strip():
        emb["api_key"] = api_key.strip()
    elif keep_key != "1":
        emb["api_key"] = ""
    emb["model"] = model.strip()
    emb["model_sntx"] = model_sntx.strip()
    emb["model_confdoc"] = model_confdoc.strip()
    save_settings(settings)
    write_service_configs(settings)
    restarted = _restart("sntx-sem", "conf-doc")
    changed = previous != json.dumps(emb, sort_keys=True)
    notice = "Эмбеддинги сохранены, сервисы перезапущены." if restarted else "Эмбеддинги сохранены, перезапуск не удался."
    if changed:
        notice += " Если модель или размерность изменились, старые индексы несовместимы — переиндексируйте."
    return RedirectResponse("/settings?notice=" + _q(notice), status_code=303)


@app.post("/settings/embeddings/check")
def check_embeddings():
    emb = load_settings().get("embeddings") or {}
    model = emb.get("model_confdoc") or emb.get("model") or "text-embedding-3-small"
    ok, detail = checks.check_embeddings(emb.get("base_url") or "", emb.get("api_key") or "", model)
    target = "/settings?notice=" if ok else "/settings?error="
    return RedirectResponse(target + _q(detail), status_code=303)


@app.post("/settings/reindex")
def reindex():
    registry.reindex_all()
    return RedirectResponse("/configs?notice=" + _q("Переиндексация conf-doc запущена. Справку sntx-sem пересоберите в её /admin."), status_code=303)


@app.get("/configs", response_class=HTMLResponse)
def configs_page(request: Request, notice: str = "", error: str = ""):
    return TEMPLATES.TemplateResponse(
        request,
        "configs.html",
        _ctx(request, configs=registry.load(), notice=notice, error=error, embeddings=registry.embeddings_configured()),
    )


@app.post("/configs/upload")
async def upload_config(archive: UploadFile = File(...)):
    raw = await archive.read()
    if not raw:
        raise HTTPException(400, "пустой файл")
    tmp = DATA / "configs" / "_upload"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as bundle:
            _safe_extract(bundle, tmp)
    except zipfile.BadZipFile as exc:
        shutil.rmtree(tmp, ignore_errors=True)
        return RedirectResponse("/configs?error=" + _q(f"не zip: {exc}"), status_code=303)
    if dump_root(tmp) is None:
        shutil.rmtree(tmp, ignore_errors=True)
        return RedirectResponse("/configs?error=" + _q("В архиве нет Configuration.xml"), status_code=303)
    try:
        row = registry.register_upload(tmp)
    except Exception as exc:
        shutil.rmtree(tmp, ignore_errors=True)
        return RedirectResponse("/configs?error=" + _q(str(exc)), status_code=303)
    return RedirectResponse("/configs?notice=" + _q(f"Конфигурация {row['product_name']} поставлена в индексацию"), status_code=303)


@app.post("/configs/{config_id}/delete")
def delete_config(config_id: str):
    try:
        registry.delete(config_id)
    except Exception as exc:
        return RedirectResponse("/configs?error=" + _q(str(exc)), status_code=303)
    return RedirectResponse("/configs?notice=" + _q("Удалено"), status_code=303)


@app.post("/configs/{config_id}/reindex")
def reindex_one(config_id: str):
    row = registry.get(config_id)
    if row is None:
        raise HTTPException(404)
    threading.Thread(target=registry.index_config, args=(row,), daemon=True).start()
    return RedirectResponse("/configs?notice=" + _q("Индексация запущена"), status_code=303)


@app.get("/tasks/new", response_class=HTMLResponse)
def new_task(request: Request, error: str = ""):
    bins = services.platform_bins()
    return TEMPLATES.TemplateResponse(
        request,
        "task.html",
        _ctx(request, configs=registry.load(), platform=bool(bins), error=error),
    )


@app.post("/tasks")
def start_task(
    config_id: str = Form(...),
    title: str = Form(...),
    brief: str = Form(...),
    with_searxng: str = Form(""),
    require_platform: str = Form(""),
):
    row = registry.get(config_id)
    if row is None:
        return RedirectResponse("/tasks/new?error=" + _q("конфигурация не найдена"), status_code=303)
    if not title.strip() or not brief.strip():
        return RedirectResponse("/tasks/new?error=" + _q("нужны заголовок и текст задачи"), status_code=303)
    job = runner.submit({
        "title": title.strip(),
        "brief": brief,
        "config_id": row["id"],
        "product_id": row["product_id"],
        "product_name": row["product_name"],
        "cf_dir": row["path"],
        "conf_name": row.get("conf_name") or "",
        "with_searxng": with_searxng == "1",
        "require_platform": require_platform == "1",
    })
    return RedirectResponse(f"/jobs/{job['id']}", status_code=303)


@app.get("/jobs/{job_id}", response_class=HTMLResponse)
def job_page(request: Request, job_id: str):
    return TEMPLATES.TemplateResponse(request, "job.html", _ctx(request, job_id=job_id))


@app.get("/jobs/{job_id}/events")
async def job_events(job_id: str):
    async def stream():
        offset = 0
        idle = 0
        while True:
            chunk, offset = runner.read_log(job_id, offset)
            if chunk:
                idle = 0
                for line in chunk.splitlines():
                    yield f"data: {json.dumps(line, ensure_ascii=False)}\n\n"
            else:
                idle += 1
            status = runner.job_status(job_id)
            if status in {"passed", "failed", "error", "done"} and idle > 2:
                yield f"event: end\ndata: {status}\n\n"
                return
            if idle > 3600:
                return
            await asyncio.sleep(0.7)

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.post("/jobs/stop")
def stop_job():
    runner.stop()
    return RedirectResponse("/", status_code=303)


@app.get("/runs", response_class=HTMLResponse)
def runs_page(request: Request):
    return TEMPLATES.TemplateResponse(request, "runs.html", _ctx(request, runs=_runs()))


@app.get("/runs/{run_id}", response_class=HTMLResponse)
def run_page(request: Request, run_id: str):
    run_dir = _run_dir(run_id)
    report = _read_json(run_dir / "report.json")
    notes = ""
    notes_path = run_dir / "NOTES.md"
    if notes_path.is_file():
        notes = notes_path.read_text(encoding="utf-8", errors="replace")
    return TEMPLATES.TemplateResponse(
        request,
        "run.html",
        _ctx(request, run_id=run_id, report=report, notes=notes, files=_out_files(run_dir)),
    )


@app.get("/runs/{run_id}/file")
def run_file(run_id: str, path: str):
    run_dir = _run_dir(run_id)
    target = (run_dir / path).resolve()
    if not str(target).startswith(str(run_dir.resolve())) or not target.is_file():
        raise HTTPException(404)
    text = target.read_text(encoding="utf-8", errors="replace")
    if len(text) > 200_000:
        text = text[:200_000] + "\n…обрезано"
    return HTMLResponse(f"<pre>{_escape(text)}</pre>")


@app.get("/runs/{run_id}/cfe.zip")
def download_cfe(run_id: str, kind: str = "cfe"):
    run_dir = _run_dir(run_id)
    folder_name = "cfe" if kind != "cfe-tests" else "cfe-tests"
    found = list(run_dir.rglob(f"implementer/out/{folder_name}"))
    if not found:
        raise HTTPException(404, "каталог не найден")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as bundle:
        root = found[0]
        for file in root.rglob("*"):
            if file.is_file():
                bundle.write(file, file.relative_to(root).as_posix())
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{run_id}-{folder_name}.zip"'},
    )


def _runs() -> list[dict]:
    root = DATA / "runs"
    rows = []
    if not root.is_dir():
        return rows
    for child in sorted(root.iterdir(), reverse=True):
        report_path = child / "report.json"
        if not child.is_dir() or not report_path.is_file():
            continue
        report = _read_json(report_path)
        rows.append({
            "id": child.name,
            "passed": report.get("passed"),
            "failed": report.get("failed"),
            "total": report.get("total"),
            "product": report.get("product"),
        })
    return rows


def _run_dir(run_id: str) -> Path:
    if "/" in run_id or "\\" in run_id or run_id in {"", ".", ".."}:
        raise HTTPException(404)
    path = (DATA / "runs" / run_id).resolve()
    if not str(path).startswith(str((DATA / "runs").resolve())) or not path.is_dir():
        raise HTTPException(404)
    return path


def _out_files(run_dir: Path) -> list[str]:
    files = []
    for path in run_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(run_dir).as_posix()
        if "/out/" in f"/{rel}" or rel.endswith("report.json") or rel.endswith("NOTES.md"):
            files.append(rel)
    return sorted(files)[:400]


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _restart(*names: str) -> bool:
    try:
        result = subprocess.run(
            ["supervisorctl", "-c", "/app/docker/supervisord.conf", "restart", *names],
            capture_output=True,
            text=True,
            timeout=40,
        )
        return result.returncode == 0
    except Exception:
        return False


def _q(text: str) -> str:
    from urllib.parse import quote
    return quote(text)


def _safe_extract(bundle: zipfile.ZipFile, dest: Path) -> None:
    root = dest.resolve()
    for info in bundle.infolist():
        target = (root / info.filename).resolve()
        if target != root and not str(target).startswith(str(root) + "\\") and not str(target).startswith(str(root) + "/"):
            raise ValueError(f"недопустимый путь в архиве: {info.filename}")
    bundle.extractall(root)


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
