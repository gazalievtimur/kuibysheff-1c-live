"""Shared helpers for 1c-live MCP analysis scripts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

STAGES = ["analyst", "yaxunit", "coder", "implementer"]


def resolve_run_dir(explicit: str | None = None) -> Path:
    """Return .../runs/<run_id>/cfe-qty-check-01 task directory."""
    runs = Path(__file__).resolve().parents[1] / "runs"
    if explicit:
        p = Path(explicit)
        if p.is_dir():
            if (p / "logs").is_dir() and (p / "logs" / "analyst.run.json").exists():
                return p
            task = p / "cfe-qty-check-01"
            if task.is_dir():
                return task
            raise SystemExit(f"not a gate task dir: {p}")
        run_id = p.name if p.parent.name == "runs" else str(p)
        task = runs / run_id / "cfe-qty-check-01"
        if not task.is_dir():
            raise SystemExit(f"run not found: {task}")
        return task

    latest = runs / "LATEST"
    if latest.exists():
        run_id = latest.read_text(encoding="utf-8").strip()
        task = runs / run_id / "cfe-qty-check-01"
        if task.is_dir():
            return task

    candidates = sorted(
        (d for d in runs.iterdir() if d.is_dir() and d.name != "LATEST"),
        key=lambda d: d.name,
        reverse=True,
    )
    for run_dir in candidates:
        task = run_dir / "cfe-qty-check-01"
        if task.is_dir():
            return task
    raise SystemExit(f"no gate runs under {runs}")


def run_pass_status(task_dir: Path) -> bool | None:
    report = task_dir.parent / "report.json"
    if not report.exists():
        return None
    try:
        data = json.loads(report.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    tasks = data.get("tasks") or []
    if not tasks:
        return None
    return bool(tasks[0].get("pass"))


def add_run_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "run",
        nargs="?",
        default=None,
        help="Run id (20260825-211924), task dir, or omit for LATEST",
    )


def parse_run_args() -> tuple[Path, str, bool | None]:
    parser = argparse.ArgumentParser(description="1c-live MCP run analysis")
    add_run_arg(parser)
    args = parser.parse_args()
    task_dir = resolve_run_dir(args.run)
    run_id = task_dir.parent.name
    return task_dir, run_id, run_pass_status(task_dir)
