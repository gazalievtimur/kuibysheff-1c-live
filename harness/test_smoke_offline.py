#!/usr/bin/env python3
"""Offline smoke for 1c-live copy-unit (no LLM / Docker / platform)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    proc = subprocess.run(
        [sys.executable, str(HERE / "eval.py"), "--dry-run"],
        cwd=str(HERE),
        check=False,
    )
    if proc.returncode != 0:
        return proc.returncode
    print("OK: 1c-live offline smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
