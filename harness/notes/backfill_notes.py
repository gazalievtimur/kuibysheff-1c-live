#!/usr/bin/env python3
"""Backfill NOTES.md for an existing 1c-live run from report.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from eval import _write_run_notes, _write_task_notes  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("usage: backfill_notes.py <run-dir>", file=sys.stderr)
        return 2
    run_dir = Path(args[0]).resolve()
    report_path = run_dir / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8-sig"))
    notes_dir = _ROOT / "notes"
    for task in report.get("tasks") or []:
        if not isinstance(task, dict):
            continue
        task_id = str(task.get("id") or "")
        task_dir = run_dir / task_id
        homes_root = (
            task_dir
            / "project"
            / ".kuibysheff"
            / "homes"
            / task_id
        )
        stage_homes: dict[str, Path] = {}
        for name in ("analyst", "yaxunit", "coder", "implementer"):
            home = homes_root / name
            if home.is_dir():
                stage_homes[name] = home
        bank = _ROOT / "bank" / f"{task_id}.json"
        expect: dict = {}
        if bank.is_file():
            loaded = json.loads(bank.read_text(encoding="utf-8-sig"))
            raw = loaded.get("expect") if isinstance(loaded, dict) else {}
            expect = raw if isinstance(raw, dict) else {}
        _write_task_notes(
            notes_dir=notes_dir,
            task_dir=task_dir,
            run_id=str(report.get("run_id") or run_dir.name),
            row=task,
            expect=expect,
            stage_homes=stage_homes,
        )
    _write_run_notes(run_dir, notes_dir, report)
    print(f"OK: notes backfilled for {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
