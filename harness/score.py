#!/usr/bin/env python3
"""Per-task scoring for 1c-live (artifact schema + needles)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError:
        return ""


def _collect_texts(root: Path, patterns: tuple[str, ...] = ("*.bsl", "*.xml", "*.md", "*.json")) -> str:
    if not root.is_dir():
        return ""
    chunks: list[str] = []
    for pattern in patterns:
        for path in root.rglob(pattern):
            if path.is_file():
                chunks.append(_read_text(path))
    return "\n".join(chunks)


def _contains_all(haystack: str, needles: list[str] | None) -> list[str]:
    missing: list[str] = []
    for needle in needles or []:
        if needle and needle not in haystack:
            missing.append(needle)
    return missing


def _contains_any(haystack: str, needles: list[str] | None) -> bool:
    items = [n for n in (needles or []) if n]
    if not items:
        return True
    return any(n in haystack for n in items)


def _agreement_needles(expect: dict[str, Any]) -> list[str]:
    needles: list[str] = []
    for group in (
        expect.get("plan_contains"),
        expect.get("test_contains"),
    ):
        for item in group or []:
            text = str(item)
            if text:
                needles.append(text)
    yax = expect.get("yaxunit") if isinstance(expect.get("yaxunit"), dict) else {}
    procedure = yax.get("procedure")
    if procedure:
        needles.append(str(procedure))
    seen: set[str] = set()
    unique: list[str] = []
    for needle in needles:
        if needle not in seen:
            seen.add(needle)
            unique.append(needle)
    return unique


def _manifest_apply_mode(out_dir: Path) -> str | None:
    path = out_dir / "manifest.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(_read_text(path))
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict):
        mode = data.get("apply_mode")
        return str(mode) if mode is not None else None
    return None


def score_task(
    *,
    expect: dict[str, Any],
    stage_homes: dict[str, Path],
    stage_outputs: dict[str, Any],
    cf_unchanged: bool,
) -> tuple[bool, list[str]]:
    failures: list[str] = []

    if not cf_unchanged:
        failures.append("CF dump was modified by the agent")

    # `goal_reached` is the CLI loop end (model set done=true), not task pass.
    # Incomplete loops fail; a finished loop still needs artifact/agreement checks.
    for stage_name, output in stage_outputs.items():
        stop = str(output.get("stop_reason") or "")
        if stop != "goal_reached":
            failures.append(
                f"{stage_name}: agent_stop={stop!r} "
                "(loop did not finish; goal_reached ≠ contract pass)"
            )

    analyst_home = stage_homes.get("analyst")
    yax_home = stage_homes.get("yaxunit")
    coder_home = stage_homes.get("coder")
    impl_home = stage_homes.get("implementer")

    if analyst_home is not None:
        out = analyst_home / "out"
        for name in expect.get("plan_files") or []:
            if not (out / name).is_file():
                failures.append(f"analyst missing out/{name}")
        if not (out / "agreements.md").is_file():
            failures.append("analyst missing out/agreements.md")
        agreements_text = _read_text(out / "agreements.md")
        for needle in _contains_all(agreements_text, _agreement_needles(expect)):
            failures.append(f"analyst agreements.md missing {needle!r}")
        plan_text = _collect_texts(out, ("*.md", "*.json"))
        for needle in _contains_all(plan_text, expect.get("plan_contains")):
            failures.append(f"analyst plan missing {needle!r}")
        mode = _manifest_apply_mode(out)
        if mode is not None and mode != "none":
            failures.append(f"analyst manifest.apply_mode={mode!r} expected 'none'")

    if yax_home is not None:
        out = yax_home / "out"
        if not (out / "test-report.md").is_file():
            failures.append("yaxunit missing out/test-report.md")
        tests_dir = out / "tests"
        cfe_tests = out / "cfe-tests"
        tests_bsl = list(tests_dir.rglob("*.bsl")) if tests_dir.is_dir() else []
        cfe_bsl = list(cfe_tests.rglob("*.bsl")) if cfe_tests.is_dir() else []
        if not tests_bsl and not cfe_bsl:
            failures.append("yaxunit missing BSL under out/tests or out/cfe-tests")
        test_text = _collect_texts(tests_dir, ("*.bsl",)) + "\n" + _collect_texts(
            cfe_tests, ("*.bsl",)
        )
        for needle in _contains_all(test_text, expect.get("test_contains")):
            failures.append(f"yaxunit tests missing {needle!r}")
        yax_expect = expect.get("yaxunit") if isinstance(expect.get("yaxunit"), dict) else {}
        procedure = yax_expect.get("procedure")
        if procedure and str(procedure) not in test_text:
            failures.append(f"yaxunit tests missing procedure {procedure!r}")
        if test_text.strip() and "ЮТТесты" not in test_text and "ЮТест" not in test_text:
            failures.append("yaxunit BSL missing ЮТТесты/ЮТест")
        mode = _manifest_apply_mode(out)
        if mode is not None and mode != "none":
            failures.append(f"yaxunit manifest.apply_mode={mode!r} expected 'none'")

    if coder_home is not None:
        out = coder_home / "out"
        src = out / "src"
        if not src.is_dir() or not any(src.rglob("*")):
            failures.append("coder out/src is empty")
        if not (out / "code-report.md").is_file():
            failures.append("coder missing code-report.md")
        src_text = _collect_texts(src)
        for needle in _contains_all(src_text, expect.get("src_contains")):
            failures.append(f"coder src missing {needle!r}")
        if expect.get("src_contains_any") and not _contains_any(
            src_text, expect.get("src_contains_any")
        ):
            failures.append(
                f"coder src missing any of {expect.get('src_contains_any')!r}"
            )
        mode = _manifest_apply_mode(out)
        if mode is not None and mode != "none":
            failures.append(f"coder manifest.apply_mode={mode!r} expected 'none'")

    if impl_home is not None:
        out = impl_home / "out"
        cfe = out / "cfe"
        if not (cfe / "Configuration.xml").is_file():
            # Accept Configuration.xml at any depth under out/cfe
            configs = list(cfe.rglob("Configuration.xml")) if cfe.is_dir() else []
            if not configs:
                failures.append("implementer missing out/cfe/Configuration.xml")
        cfe_text = _collect_texts(cfe)
        for obj in expect.get("cfe_objects") or []:
            # Object path may appear as folder or XML name fragment.
            needle = str(obj).replace("\\", "/")
            leaf = needle.split("/")[-1]
            if needle not in cfe_text and leaf not in cfe_text:
                # Also check filesystem paths
                if not list(cfe.rglob(leaf)) and not list(cfe.rglob(f"{leaf}.xml")):
                    failures.append(f"implementer CFE missing object {obj!r}")
        if expect.get("cfe_contains"):
            for needle in _contains_all(cfe_text, expect.get("cfe_contains")):
                failures.append(f"implementer CFE missing {needle!r}")
        if expect.get("cfe_contains_any") and not _contains_any(
            cfe_text, expect.get("cfe_contains_any")
        ):
            failures.append(
                f"implementer CFE missing any of {expect.get('cfe_contains_any')!r}"
            )
        mode = _manifest_apply_mode(out)
        if mode is not None and mode != "copy_out":
            failures.append(
                f"implementer manifest.apply_mode={mode!r} expected 'copy_out'"
            )
        if not (out / "implement-report.md").is_file() and not (
            out / "checklist.md"
        ).is_file():
            failures.append("implementer missing implement-report.md/checklist.md")

    return not failures, failures
