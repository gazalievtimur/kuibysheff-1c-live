"""Register configuration dumps in the code-index daemon."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

INDEXER = os.environ.get("BSL_INDEXER", "/opt/tools/bsl-indexer")
HOME = Path(os.environ.get("CODE_INDEX_HOME", "/data/code-index"))


def daemon_toml() -> Path:
    return HOME / "daemon.toml"


def tracks(path: Path) -> bool:
    text = daemon_toml().read_text(encoding="utf-8") if daemon_toml().is_file() else ""
    target = str(path.resolve())
    return target in text


def add(path: Path) -> None:
    path = path.resolve()
    toml = daemon_toml()
    toml.parent.mkdir(parents=True, exist_ok=True)
    if tracks(path):
        return
    block = f'\n[[paths]]\npath = "{path}"\nlanguage = "bsl"\n'
    existing = toml.read_text(encoding="utf-8") if toml.is_file() else "[daemon]\nhttp_port = 0\nmax_concurrent_initial = 1\n"
    if not existing.endswith("\n"):
        existing += "\n"
    toml.write_text(existing + block, encoding="utf-8")


def remove(path: Path) -> None:
    toml = daemon_toml()
    if not toml.is_file():
        return
    target = str(path.resolve())
    lines = toml.read_text(encoding="utf-8").splitlines()
    kept: list[str] = []
    skip = 0
    i = 0
    while i < len(lines):
        if lines[i].strip() == "[[paths]]":
            block = lines[i:i + 4]
            if any(target in line for line in block):
                i += 4
                if i < len(lines) and lines[i].strip() == "":
                    i += 1
                continue
        kept.append(lines[i])
        i += 1
        skip += 0
    toml.write_text("\n".join(kept).rstrip() + "\n", encoding="utf-8")


def reload() -> str:
    result = subprocess.run(
        [INDEXER, "daemon", "reload"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        raise RuntimeError(output.strip() or f"daemon reload exited {result.returncode}")
    return output.strip()
