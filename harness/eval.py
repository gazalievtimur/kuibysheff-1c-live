#!/usr/bin/env python3
"""Live LLM 1C «Склад» eval: analyst → yaxunit → coder → implementer."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from score import score_task  # noqa: E402

STAGES = (
    ("analyst", "1c-analyst"),
    ("yaxunit", "1c-yaxunit"),
    ("coder", "1c-coder"),
    ("implementer", "1c-implementer"),
)
DEFAULT_STAGES = [name for name, _ in STAGES]
KNOWN_STAGES = set(DEFAULT_STAGES)
YAXUNIT_DOCS = (
    "first-test.md",
    "registration.md",
    "assertions.md",
    "features.md",
    "transactions.md",
)
AGREEMENTS_HEADING = "Договорённости (идентификаторы)"
PROTOCOL_REL = Path("profiles") / "1c-shared" / "agreements-protocol.md"

DEFAULT_GATE_TASK = "cfe-qty-check-01"


def _repo_root_default() -> Path:
    return Path(__file__).resolve().parents[1]


def _escape_yaml_dq(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _yaml_scalar(text: str, key: str, default: str = "") -> str:
    for pattern in (
        rf'(?m)^\s*{re.escape(key)}:\s*"([^"]*)"',
        rf"(?m)^\s*{re.escape(key)}:\s*'([^']*)'",
        rf"(?m)^\s*{re.escape(key)}:\s*([^#\r\n]+)",
    ):
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return default


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        if name and not os.environ.get(name):
            os.environ[name] = value


def _extract_json_object(text: str) -> dict[str, Any]:
    start = text.find("{")
    if start < 0:
        raise ValueError("no JSON object in agent stdout")
    depth = 0
    end = -1
    for i, ch in enumerate(text[start:], start=start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end < start:
        raise ValueError("unterminated JSON object in agent stdout")
    return json.loads(text[start : end + 1])


def _agent_bin(repo_root: Path, override: Optional[str]) -> Path:
    if override:
        path = Path(override).expanduser().resolve()
        if not path.is_file():
            raise SystemExit(f"missing agent binary: {path}")
        return path

    env_bin = os.environ.get("KBSHFF_BIN", "").strip()
    if env_bin:
        path = Path(env_bin).expanduser().resolve()
        if not path.is_file():
            raise SystemExit(f"KBSHFF_BIN not found: {path}")
        return path

    for name in ("kbshff.exe", "kbshff"):
        found = shutil.which(name)
        if found:
            return Path(found).resolve()

    search_roots: list[Path] = [repo_root]
    env_src = os.environ.get("KUIBYSHEFF_SRC", "").strip()
    if env_src:
        search_roots.insert(0, Path(env_src))
    parent = repo_root.parent
    for sibling in ("Agent-Kuibysheff", "Agent Kuibyshev"):
        search_roots.append(parent / sibling)

    for root in search_roots:
        root = root.resolve()
        if not (root / "Cargo.toml").is_file():
            continue
        for name in ("kbshff.exe", "kbshff"):
            candidate = root / "target" / "release" / name
            if candidate.is_file():
                return candidate.resolve()

    raise SystemExit(
        "kbshff not found (set KBSHFF_BIN, install on PATH, or KUIBYSHEFF_SRC + cargo build)"
    )


def _tree_fingerprint(root: Path) -> str:
    """Hash CF tree; ignore indexer caches written beside the dump."""
    h = hashlib.sha256()
    if not root.is_dir():
        return h.hexdigest()
    skip_dir_names = {".code-index", "__pycache__", ".git"}
    for path in sorted(root.rglob("*")):
        if any(part in skip_dir_names for part in path.parts):
            continue
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            h.update(rel.encode("utf-8"))
            h.update(b"\0")
            h.update(path.read_bytes())
            h.update(b"\0")
    return h.hexdigest()


def _ensure_profile(
    agent_bin: Path,
    project_root: Path,
    agent_id: str,
    settings_dir: Path,
) -> None:
    """Init profile and import prompts/skills/rules without example YAML.

    profiles/*/agent-config.example.yaml points at ../../../src/cf which does
    not exist in this eval layout; we write a real config after import.
    """
    project_root.mkdir(parents=True, exist_ok=True)
    init = subprocess.run(
        [str(agent_bin), "init", agent_id, "--project-root", str(project_root), "--force"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if init.returncode != 0:
        raise RuntimeError(
            f"init {agent_id} failed (exit {init.returncode}): "
            f"{(init.stderr or init.stdout or '').strip()}"
        )
    staging = project_root / ".kuibysheff" / ".1c-live-import" / agent_id
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    for name in ("master_prompt.md", "skills.dsl", "rules.md"):
        src = settings_dir / name
        if src.is_file():
            shutil.copy2(src, staging / name)
    proc = subprocess.run(
        [
            str(agent_bin),
            "config",
            "--project-root",
            str(project_root),
            "--agent",
            agent_id,
            "import",
            "--from",
            str(staging),
            "--force",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"config import {agent_id} failed (exit {proc.returncode}): "
            f"{(proc.stderr or proc.stdout or '').strip()}"
        )


def _resolve_mcp_paths(repo_root: Path) -> tuple[str, str, str]:
    """Return (sntx_config, indexer, sntx_python)."""
    sntx = os.environ.get("SNTX_SEM_CONFIG", "").strip()
    indexer = (
        os.environ.get("BSL_INDEXER", "").strip()
        or os.environ.get("CODE_INDEX_BIN", "").strip()
        or os.environ.get("BSL_INDEXER_EXE", "").strip()
    )
    if not sntx:
        raise SystemExit(
            "SNTX_SEM_CONFIG is required (path to 1c-sntx-sem config.yaml)."
        )
    if not indexer:
        for candidate in (
            repo_root / "tools" / "bsl-indexer.exe",
            repo_root / "tools" / "bsl-indexer",
        ):
            if candidate.is_file():
                indexer = str(candidate)
                break
    if not indexer:
        raise SystemExit(
            "BSL_INDEXER / CODE_INDEX_BIN is required (path to bsl-indexer)."
        )
    if not Path(sntx).is_file():
        raise SystemExit(f"SNTX_SEM_CONFIG file not found: {sntx}")
    if not Path(indexer).is_file():
        raise SystemExit(f"bsl-indexer not found: {indexer}")

    sntx_py = os.environ.get("SNTX_SEM_PYTHON", "").strip()
    if not sntx_py:
        sntx_root = Path(sntx).resolve().parent
        for candidate in (
            sntx_root / ".venv" / "Scripts" / "python.exe",
            sntx_root / ".venv" / "bin" / "python",
        ):
            if candidate.is_file():
                sntx_py = str(candidate)
                break
    if not sntx_py:
        # Last resort: host python (needs APPDATA user site for `mcp` package).
        sntx_py = sys.executable
    if not Path(sntx_py).is_file():
        raise SystemExit(
            "SNTX_SEM_PYTHON not found (set it or create 1c-sntx-sem/.venv)."
        )
    return sntx, indexer, sntx_py


def _write_stage_config(
    path: Path,
    *,
    base_text: str,
    log_dir: Path,
    cf_root: Path,
    sntx_config: str,
    indexer: str,
    sntx_python: str,
    include_searxng: bool,
) -> None:
    provider_base_url = _yaml_scalar(base_text, "base_url", "https://api.openai.com/v1")
    provider_model = _yaml_scalar(base_text, "model", "gpt-4o")
    provider_api_key_env = _yaml_scalar(base_text, "api_key_env", "OPENAI_API_KEY")
    provider_timeout_ms = _yaml_scalar(base_text, "timeout_ms", "180000")
    max_iterations = _yaml_scalar(base_text, "max_iterations", "40")
    max_tokens = _yaml_scalar(base_text, "max_tokens", "120000")
    max_duration_sec = _yaml_scalar(base_text, "max_duration_sec", "1200")

    cf_s = _escape_yaml_dq(str(cf_root.resolve()).replace("\\", "/"))
    log_s = _escape_yaml_dq(str(log_dir.resolve()).replace("\\", "/"))
    sntx_s = _escape_yaml_dq(sntx_config.replace("\\", "/"))
    idx_s = _escape_yaml_dq(indexer.replace("\\", "/"))
    py_s = _escape_yaml_dq(str(Path(sntx_python).resolve()).replace("\\", "/"))
    sntx_src = _escape_yaml_dq(
        str((Path(sntx_config).resolve().parent / "src").as_posix())
    )

    # kbshff clears the child env; pass Windows user-profile keys so site-packages
    # and embedding API keys remain reachable when not using a dedicated venv.
    extra_env_lines: list[str] = []
    for key in ("APPDATA", "LOCALAPPDATA", "USERPROFILE", "USERNAME"):
        val = os.environ.get(key)
        if val:
            extra_env_lines.append(
                f'      {key}: "{_escape_yaml_dq(val.replace(chr(92), "/"))}"'
            )
    # Forward provider key used by sntx embedding config when present.
    for key in ("OPENAI_API_KEY", "POLZA_API_KEY", "DEEPSEEK_API_KEY"):
        val = os.environ.get(key)
        if val:
            extra_env_lines.append(f'      {key}: "{_escape_yaml_dq(val)}"')
    extra_env = ("\n" + "\n".join(extra_env_lines)) if extra_env_lines else ""

    searx = ""
    if include_searxng:
        searx = """
  - name: "searxng"
    transport: http
    url: "http://127.0.0.1:3000/mcp"
    timeout_ms: 60000
"""

    program_lines: list[str] = []
    for name in ("rg", "git"):
        found = shutil.which(name)
        if found and Path(found).is_file():
            exe = _escape_yaml_dq(str(Path(found).resolve()).replace("\\", "/"))
            program_lines.append(f'      - name: {name}\n        executable: "{exe}"')
    if program_lines:
        programs_block = "    programs:\n" + "\n".join(program_lines)
    else:
        programs_block = "    programs: []"

    content = f"""provider:
  base_url: "{_escape_yaml_dq(provider_base_url)}"
  model: "{_escape_yaml_dq(provider_model)}"
  api_key_env: "{_escape_yaml_dq(provider_api_key_env)}"
  timeout_ms: {provider_timeout_ms}
  max_retries: 3
  retry_base_delay_ms: 500

mcp:
  - name: "sntx_sem"
    command: "{py_s}"
    args: ["-m", "sntx_sem.mcp_server"]
    env:
      SNTX_SEM_CONFIG: "{sntx_s}"
      SNTX_SEM_MCP_LOG_LEVEL: "INFO"
      PYTHONPATH: "{sntx_src}"{extra_env}
    timeout_ms: 60000

  - name: "code-index"
    command: "{idx_s}"
    args: ["serve", "--path", "{cf_s}"]
    timeout_ms: 60000
{searx}
limits:
  max_iterations: {max_iterations}
  max_tokens: {max_tokens}
  max_duration_sec: {max_duration_sec}

logging:
  enable_ai_log: true
  enable_mcp_log: true
  enable_chat_history: true
  output_dir: "{log_s}"

access:
  mode: strict
  tools:
    builtins:
      - home.list
      - home.read
      - home.write
      - home.run
      - local_tools.search_docs
      - local_tools.read_file
  filesystem:
    home:
      read: ["."]
      write: ["out/", "notes/"]
    workspace:
      root: "{cf_s}"
      read: ["."]
    input_roots:
      - "."
  run:
{programs_block}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _copy_dir_contents(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    if not src.is_dir():
        return
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def _protocol_src(repo_root: Path) -> Path:
    return repo_root / PROTOCOL_REL


def _seed_stage_agreements(
    home_dir: Path,
    *,
    task_id: str,
    expect: dict[str, Any],
    protocol_src: Path,
    analyst_agreements: Path | None = None,
) -> None:
    dest = home_dir / "in"
    dest.mkdir(parents=True, exist_ok=True)
    if protocol_src.is_file():
        shutil.copy2(protocol_src, dest / "agreements-protocol.md")
    payload = {"id": task_id, "expect": expect}
    (dest / "agreements.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (dest / "expect.json").write_text(
        json.dumps(expect, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if analyst_agreements is not None and analyst_agreements.is_file():
        shutil.copy2(analyst_agreements, dest / "agreements.md")


def _cfe_tree_ready(path: Path) -> bool:
    if not path.is_dir():
        return False
    if (path / "Configuration.xml").is_file():
        return True
    return any(path.rglob("Configuration.xml"))


def _generated_yaxunit_dir(stage_homes: dict[str, Path], fallback: Path) -> Path:
    """Prefer generated test CFE; fall back to the stub fixture."""
    for key in ("implementer", "yaxunit"):
        home = stage_homes.get(key)
        if home is None:
            continue
        candidate = home / "out" / "cfe-tests"
        if _cfe_tree_ready(candidate):
            return candidate
    return fallback


def _copy_tests_for_coder(yax_home: Path, dest: Path) -> None:
    tests_src = yax_home / "out" / "tests"
    if tests_src.is_dir() and any(p.is_file() for p in tests_src.rglob("*")):
        _copy_tree(tests_src, dest)
        return
    cfe_tests = yax_home / "out" / "cfe-tests"
    if not cfe_tests.is_dir():
        return
    dest.mkdir(parents=True, exist_ok=True)
    for bsl in cfe_tests.rglob("*.bsl"):
        shutil.copy2(bsl, dest / bsl.name)


def _invoke_run_yaxunit(
    *,
    yax_script: Path,
    cf_copy: Path,
    yax_unit_dir: Path,
    agent_cfe: Path,
    work_dir: Path,
    require_platform: bool,
) -> subprocess.CompletedProcess[str]:
    ps = shutil.which("pwsh") or shutil.which("powershell")
    if not ps:
        raise FileNotFoundError("PowerShell not found")
    cmd = [
        ps,
        "-NoProfile",
        "-File",
        str(yax_script),
        "-CfDir",
        str(cf_copy),
        "-YaxUnitDir",
        str(yax_unit_dir),
        "-AgentCfeDir",
        str(agent_cfe),
        "-WorkDir",
        str(work_dir),
    ]
    if require_platform:
        cmd.append("-RequirePlatform")
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _usage_line(usage: Any) -> str:
    if not isinstance(usage, dict):
        return "n/a"
    parts: list[str] = []
    for key in ("iterations", "prompt_tokens", "completion_tokens", "total_tokens", "elapsed_ms"):
        if usage.get(key) is not None:
            parts.append(f"{key}={usage[key]}")
    return ", ".join(parts) if parts else "n/a"


def _list_out_files(home: Path | None, limit: int = 40) -> list[str]:
    if home is None:
        return []
    out = home / "out"
    if not out.is_dir():
        return []
    rows: list[str] = []
    for path in sorted(out.rglob("*")):
        if path.is_file():
            rows.append(path.relative_to(out).as_posix())
            if len(rows) >= limit:
                rows.append("…")
                break
    return rows


def _write_task_notes(
    *,
    notes_dir: Path,
    task_dir: Path,
    run_id: str,
    row: dict[str, Any],
    expect: dict[str, Any],
    stage_homes: dict[str, Path],
) -> None:
    """Write a durable NOTES.md for later write-ups of how the conveyor ran."""
    task_id = str(row.get("id") or task_dir.name)
    lines: list[str] = [
        f"# {task_id} — {run_id}",
        "",
        f"- pass: `{row.get('pass')}`",
        f"- agent_stop (CLI loop end, not pass): see stages below",
        f"- platform (run-yaxunit.ps1): `{row.get('yaxunit')}`",
        f"- error: `{row.get('error')}`",
        f"- failures: {json.dumps(row.get('failures') or [], ensure_ascii=False)}",
        "",
        "## expect (bank)",
        "",
        "```json",
        json.dumps(expect, ensure_ascii=False, indent=2),
        "```",
        "",
        "## stages",
        "",
    ]
    stages = row.get("stages") if isinstance(row.get("stages"), dict) else {}
    for name, _agent in STAGES:
        stage = stages.get(name) if isinstance(stages, dict) else None
        if not isinstance(stage, dict):
            continue
        home = stage_homes.get(name)
        home_s = str(home) if home else ""
        lines.extend(
            [
                f"### {name}",
                "",
                f"- agent_stop: `{stage.get('stop_reason')}` (goal_reached = done=true, not contract pass)",
                f"- usage: {_usage_line(stage.get('usage'))}",
                f"- home: `{home_s}`",
                f"- result: {stage.get('result')}",
                "",
            ]
        )
        files = _list_out_files(home)
        if files:
            lines.append("out/:")
            for rel in files:
                lines.append(f"- `{rel}`")
            lines.append("")
    lines.extend(
        [
            "## where to look",
            "",
            f"- task dir: `{task_dir}`",
            f"- logs: `{task_dir / 'logs'}`",
            f"- platform work: `{task_dir / 'yaxunit'}`",
            "",
        ]
    )
    text = "\n".join(lines) + "\n"
    (task_dir / "NOTES.md").write_text(text, encoding="utf-8")
    dest_dir = notes_dir / "runs" / run_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / f"{task_id}.md").write_text(text, encoding="utf-8")


def _write_run_notes(run_dir: Path, notes_dir: Path, report: dict[str, Any]) -> None:
    run_id = str(report.get("run_id") or run_dir.name)
    lines = [
        f"# Run {run_id}",
        "",
        f"- product: `{report.get('product')}`",
        f"- passed: {report.get('passed')}  failed: {report.get('failed')}  total: {report.get('total')}",
        f"- report: `{run_dir / 'report.json'}`",
        "",
        "## tasks",
        "",
    ]
    for task in report.get("tasks") or []:
        if not isinstance(task, dict):
            continue
        tid = task.get("id")
        lines.append(
            f"- `{tid}`: pass={task.get('pass')} platform={task.get('yaxunit')!r} "
            f"failures={json.dumps(task.get('failures') or [], ensure_ascii=False)}"
        )
        lines.append(f"  notes: `notes/runs/{run_id}/{tid}.md`")
    lines.append("")
    text = "\n".join(lines) + "\n"
    (run_dir / "NOTES.md").write_text(text, encoding="utf-8")
    dest_dir = notes_dir / "runs" / run_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / "NOTES.md").write_text(text, encoding="utf-8")


def _stage_prompt(stage: str, product_id: str, expect: dict[str, Any] | None = None) -> str:
    expect = expect or {}
    yax = expect.get("yaxunit") if isinstance(expect.get("yaxunit"), dict) else {}
    procedure = str(yax.get("procedure") or "").strip()
    needles = [str(n) for n in (expect.get("test_contains") or []) if n]
    preamble = (
        "Read in/agreements-protocol.md and in/agreements.json first. "
        "Identifiers are literals (no synonyms, no renaming).\n"
    )
    gate_line = ""
    if procedure or needles:
        bits = []
        if procedure:
            bits.append(f"required procedure name (exact spelling): {procedure}")
        if needles:
            bits.append("BSL must contain: " + ", ".join(needles))
        gate_line = "Also read in/agreements.md and in/expect.json. " + "; ".join(bits) + ".\n"

    if stage == "analyst":
        extra = (
            "Write out/agreements.md first (verbatim identifiers from "
            "in/agreements.json). Repeat the gate procedure in tasks.md.\n"
        )
        if procedure:
            extra += f" Gate procedure: {procedure}.\n"
        return (
            preamble
            + f"Подготовь утверждаемый план доработки в расширении для product={product_id}.\n"
            "Read in/task_brief.md and in/product.json. Research CF via code-index and sntx_sem.\n"
            f"{extra}"
            "Write prd.md, architecture.md, tasks.md (labels bsl|metadata|cfe_packaging), "
            "cfe-scope.md, workflow-state.md (verification table), "
            "manifest.json (apply_mode=none).\n"
            "Return JSON only on every turn."
        )
    if stage == "yaxunit":
        return (
            preamble
            + "Write YAxUnit tests for the approved plan. Read in/docs/ first "
            "(public YAxUnit snapshot). Read in/prd.md, in/tasks.md, in/cfe-scope.md. "
            "Do not implement the feature. Tests must fail on the baseline CF.\n"
            f"{gate_line}"
            "Write out/tests/, out/cfe-tests/, test-report.md (cite docs URLs + verification table), "
            "manifest.json (apply_mode=none). Return JSON only on every turn."
        )
    if stage == "coder":
        return (
            preamble
            + "Implement approved bsl/metadata steps from in/tasks.md into out/src/.\n"
            "Read in/agreements.md and in/tests/ so the change satisfies the YAxUnit tests. "
            "Do not rename tests. Skip cfe_packaging. Write code-report.md "
            "(verification table), files-index.md, "
            "manifest.json (apply_mode=none). Return JSON only on every turn."
        )
    return (
        preamble
        + "Package coder sources from in/coder/ into out/cfe/ per in/cfe-scope.md.\n"
        "Read in/agreements.md. Copy in/cfe-tests/ to out/cfe-tests/ without rewriting tests. "
        "Write implement-report.md (verification table), checklist.md, "
        "manifest.json (apply_mode=copy_out).\n"
        "Return JSON only on every turn."
    )


def _run_agent(
    *,
    agent_bin: Path,
    project_root: Path,
    agent_id: str,
    home_rel: str,
    prompt: str,
    log_path: Path,
) -> dict[str, Any]:
    cmd = [
        str(agent_bin),
        "run",
        "--project-root",
        str(project_root),
        "--agent",
        agent_id,
        "--home",
        home_rel,
        "--prompt",
        prompt,
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        json.dumps(
            {
                "cmd": cmd,
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    if not (proc.stdout or "").strip():
        raise RuntimeError(
            f"empty stdout from {agent_id} (exit {proc.returncode}): "
            f"{(proc.stderr or '')[:500]}"
        )
    return _extract_json_object(proc.stdout)


def _load_tasks(bank_dir: Path, task_ids: list[str], run_all: bool) -> list[Path]:
    tasks = sorted(bank_dir.glob("*.json"))
    if run_all:
        return tasks
    wanted = set(task_ids) if task_ids else {DEFAULT_GATE_TASK}
    selected = [t for t in tasks if t.stem in wanted]
    missing = wanted - {t.stem for t in selected}
    if missing:
        raise SystemExit(f"task(s) not found in bank: {', '.join(sorted(missing))}")
    return selected


def _validate_bank_task(task: dict[str, Any], path: Path) -> list[str]:
    errors: list[str] = []
    if not task.get("id"):
        errors.append(f"{path.name}: missing id")
    if not task.get("brief"):
        errors.append(f"{path.name}: missing brief")
    stages = task.get("stages")
    if stages is not None:
        if not isinstance(stages, list) or not stages:
            errors.append(f"{path.name}: stages must be a non-empty list")
        else:
            unknown = [s for s in stages if s not in KNOWN_STAGES]
            if unknown:
                errors.append(f"{path.name}: unknown stages {unknown!r}")
    expect = task.get("expect")
    if not isinstance(expect, dict):
        errors.append(f"{path.name}: expect must be object")
        return errors
    if not expect.get("plan_files"):
        errors.append(f"{path.name}: expect.plan_files required")
    brief = str(task.get("brief") or "")
    if AGREEMENTS_HEADING not in brief:
        errors.append(f"{path.name}: brief missing heading {AGREEMENTS_HEADING!r}")
    effective_stages = stages if isinstance(stages, list) else DEFAULT_STAGES
    if "analyst" in effective_stages:
        plan_files = expect.get("plan_files") or []
        if "agreements.md" not in plan_files:
            errors.append(f"{path.name}: expect.plan_files must include agreements.md")
    if "yaxunit" in effective_stages:
        yax = expect.get("yaxunit") if isinstance(expect.get("yaxunit"), dict) else {}
        if not expect.get("test_contains") and not yax.get("procedure"):
            errors.append(
                f"{path.name}: yaxunit stage needs expect.test_contains "
                "or expect.yaxunit.procedure"
            )
    return errors


def dry_run(bank_dir: Path, cf_dir: Path, cfe_dir: Path) -> int:
    errors: list[str] = []
    if not (cf_dir / "Configuration.xml").is_file():
        errors.append(f"missing CF Configuration.xml under {cf_dir}")
    if not (cfe_dir / "Configuration.xml").is_file():
        errors.append(f"missing YAxUnit Configuration.xml under {cfe_dir}")
    # Well-formed XML check
    import xml.etree.ElementTree as ET

    for xml_path in list(cf_dir.rglob("*.xml")) + list(cfe_dir.rglob("*.xml")):
        try:
            ET.parse(xml_path)
        except ET.ParseError as exc:
            errors.append(f"XML parse error {xml_path}: {exc}")
    tasks = sorted(bank_dir.glob("*.json"))
    if not tasks:
        errors.append(f"empty bank: {bank_dir}")
    for task_path in tasks:
        try:
            task = json.loads(task_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            errors.append(f"{task_path.name}: {exc}")
            continue
        errors.extend(_validate_bank_task(task, task_path))
    # Planted defect markers present
    rashod = cf_dir / "Documents" / "РасходТовара" / "Ext" / "ObjectModule.bsl"
    http = cf_dir / "HTTPServices" / "ОбменСкладом" / "Ext" / "Module.bsl"
    if rashod.is_file():
        text = rashod.read_text(encoding="utf-8")
        if "ПередЗаписью" not in text or "ОстаткиТоваров" not in text:
            errors.append("РасходТовара ObjectModule missing expected symbols")
    else:
        errors.append(f"missing {rashod}")
    if http.is_file():
        if "ОстаткиGET" not in http.read_text(encoding="utf-8"):
            errors.append("ОбменСкладом missing ОстаткиGET")
    else:
        errors.append(f"missing {http}")

    docs_dir = _HERE / "docs" / "yaxunit"
    if not docs_dir.is_dir():
        errors.append(f"missing YAxUnit docs pack: {docs_dir}")
    else:
        for name in YAXUNIT_DOCS:
            doc = docs_dir / name
            if not doc.is_file():
                errors.append(f"missing YAxUnit docs file: {doc.name}")
                continue
            header = doc.read_text(encoding="utf-8-sig")[:400]
            if "Source:" not in header:
                errors.append(f"{doc.name}: missing Source: URL header")

    protocol = _HERE.parent / PROTOCOL_REL
    if not protocol.is_file():
        errors.append(f"missing agreements protocol: {protocol}")

    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1
    print(
        f"OK: dry-run passed ({len(tasks)} bank tasks, CF+CFE XML ok, "
        "YAxUnit docs pack present, agreements protocol present)"
    )
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--bank-dir", type=Path, default=_HERE / "bank")
    parser.add_argument("--cf-dir", type=Path, default=_HERE / "cf")
    parser.add_argument(
        "--yaxunit-dir", type=Path, default=_HERE / "cfe" / "YAxUnit_Tests_Sklad"
    )
    parser.add_argument("--runs-root", type=Path, default=_HERE / "runs")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--agent-bin", default="")
    parser.add_argument("--task-id", action="append", default=[])
    parser.add_argument("--all", action="store_true", help="Run entire bank")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--require-platform",
        action="store_true",
        help="Fail if YAxUnit / ibcmd platform step cannot run",
    )
    parser.add_argument(
        "--with-searxng",
        action="store_true",
        help="Allow SearXNG MCP on analyst and yaxunit (optional)",
    )
    args = parser.parse_args(argv)

    repo_root = (args.repo_root or _repo_root_default()).resolve()
    _load_dotenv(repo_root / ".env")

    bank_dir = args.bank_dir.resolve()
    cf_dir = args.cf_dir.resolve()
    yax_dir = args.yaxunit_dir.resolve()
    runs_root = args.runs_root.resolve()

    if args.dry_run:
        return dry_run(bank_dir, cf_dir, yax_dir)

    config_path = args.config
    if config_path is None:
        local = repo_root / "agent-config.local.yaml"
        example = repo_root / "profiles" / "1c-analyst" / "agent-config.example.yaml"
        config_path = local if local.is_file() else example
    config_path = config_path.resolve()
    if not config_path.is_file():
        print(f"config not found: {config_path}", file=sys.stderr)
        return 1

    docs_src = _HERE / "docs" / "yaxunit"
    missing_docs = [name for name in YAXUNIT_DOCS if not (docs_src / name).is_file()]
    if missing_docs:
        print(
            f"missing YAxUnit docs pack under {docs_src}: {', '.join(missing_docs)}",
            file=sys.stderr,
        )
        return 1
    protocol_src = _protocol_src(repo_root)
    if not protocol_src.is_file():
        print(f"missing agreements protocol: {protocol_src}", file=sys.stderr)
        return 1

    base_text = config_path.read_text(encoding="utf-8-sig")
    api_key_env = _yaml_scalar(base_text, "api_key_env", "OPENAI_API_KEY")
    if not os.environ.get(api_key_env):
        print(f"missing provider API key env: {api_key_env}", file=sys.stderr)
        return 1

    sntx_config, indexer, sntx_python = _resolve_mcp_paths(repo_root)
    agent_bin = _agent_bin(repo_root, args.agent_bin or None)

    try:
        task_paths = _load_tasks(bank_dir, args.task_id, args.all)
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 1

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_dir = runs_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (runs_root / "LATEST").write_text(str(run_dir), encoding="utf-8")

    results: list[dict[str, Any]] = []
    passed = 0
    failed = 0

    for task_path in task_paths:
        task = json.loads(task_path.read_text(encoding="utf-8-sig"))
        task_id = str(task.get("id") or task_path.stem)
        expect = task.get("expect") if isinstance(task.get("expect"), dict) else {}
        stages_wanted = task.get("stages") or DEFAULT_STAGES

        task_dir = run_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        project_root = task_dir / "project"
        cf_copy = task_dir / "cf"
        _copy_tree(cf_dir, cf_copy)
        cf_fp_before = _tree_fingerprint(cf_copy)

        stage_outputs: dict[str, Any] = {}
        stage_homes: dict[str, Path] = {}
        failures: list[str] = []
        error: Optional[str] = None

        try:
            for stage_name, agent_id in STAGES:
                if stage_name not in stages_wanted:
                    continue
                settings = repo_root / "profiles" / agent_id
                if not settings.is_dir():
                    raise RuntimeError(f"missing settings: {settings}")
                _ensure_profile(agent_bin, project_root, agent_id, settings)

            for stage_name, agent_id in STAGES:
                if stage_name not in stages_wanted:
                    continue

                home_rel = f"homes/{task_id}/{stage_name}"
                home_dir = project_root / ".kuibysheff" / home_rel
                if home_dir.exists():
                    shutil.rmtree(home_dir)
                (home_dir / "in").mkdir(parents=True)
                (home_dir / "out").mkdir(parents=True)
                (home_dir / "notes").mkdir(parents=True)
                stage_homes[stage_name] = home_dir

                log_dir = task_dir / "logs" / stage_name
                cfg_out = (
                    project_root
                    / ".kuibysheff"
                    / "protected"
                    / "agents"
                    / agent_id
                    / "agent-config.yaml"
                )
                _write_stage_config(
                    cfg_out,
                    base_text=base_text,
                    log_dir=log_dir,
                    cf_root=cf_copy,
                    sntx_config=sntx_config,
                    indexer=indexer,
                    sntx_python=sntx_python,
                    include_searxng=bool(
                        args.with_searxng and stage_name in ("analyst", "yaxunit")
                    ),
                )

                if stage_name == "analyst":
                    (home_dir / "in" / "task_brief.md").write_text(
                        str(task.get("brief") or ""), encoding="utf-8"
                    )
                    product = {
                        "id": "sklad",
                        "name": "Склад",
                        "cf_root": str(cf_copy),
                        "task_id": task_id,
                    }
                    (home_dir / "in" / "product.json").write_text(
                        json.dumps(product, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                elif stage_name == "yaxunit":
                    analyst_out = stage_homes["analyst"] / "out"
                    _copy_dir_contents(analyst_out, home_dir / "in")
                    (home_dir / "in" / "APPROVED").write_text("approved\n", encoding="utf-8")
                    docs_src = _HERE / "docs" / "yaxunit"
                    if docs_src.is_dir():
                        _copy_tree(docs_src, home_dir / "in" / "docs")
                    brief = str(task.get("brief") or "")
                    if brief:
                        (home_dir / "in" / "task_brief.md").write_text(
                            brief, encoding="utf-8"
                        )
                elif stage_name == "coder":
                    analyst_out = stage_homes["analyst"] / "out"
                    _copy_dir_contents(analyst_out, home_dir / "in")
                    (home_dir / "in" / "APPROVED").write_text("approved\n", encoding="utf-8")
                    yax_home = stage_homes.get("yaxunit")
                    if yax_home is not None:
                        _copy_tests_for_coder(yax_home, home_dir / "in" / "tests")
                elif stage_name == "implementer":
                    analyst_out = stage_homes["analyst"] / "out"
                    coder_out = stage_homes["coder"] / "out"
                    for name in (
                        "cfe-scope.md",
                        "architecture.md",
                        "tasks.md",
                        "prd.md",
                        "agreements.md",
                    ):
                        src = analyst_out / name
                        if src.is_file():
                            shutil.copy2(src, home_dir / "in" / name)
                    coder_in = home_dir / "in" / "coder"
                    _copy_dir_contents(coder_out, coder_in)
                    yax_home = stage_homes.get("yaxunit")
                    if yax_home is not None:
                        cfe_tests = yax_home / "out" / "cfe-tests"
                        if cfe_tests.is_dir():
                            _copy_tree(cfe_tests, home_dir / "in" / "cfe-tests")

                analyst_agreements = None
                if stage_name != "analyst":
                    ah = stage_homes.get("analyst")
                    if ah is not None:
                        analyst_agreements = ah / "out" / "agreements.md"
                _seed_stage_agreements(
                    home_dir,
                    task_id=task_id,
                    expect=expect,
                    protocol_src=_protocol_src(repo_root),
                    analyst_agreements=analyst_agreements,
                )

                output = _run_agent(
                    agent_bin=agent_bin,
                    project_root=project_root,
                    agent_id=agent_id,
                    home_rel=home_rel,
                    prompt=_stage_prompt(stage_name, "sklad", expect),
                    log_path=task_dir / "logs" / f"{stage_name}.run.json",
                )
                stage_outputs[stage_name] = output

            cf_fp_after = _tree_fingerprint(cf_copy)
            ok, score_failures = score_task(
                expect=expect,
                stage_homes=stage_homes,
                stage_outputs=stage_outputs,
                cf_unchanged=(cf_fp_before == cf_fp_after),
            )
            failures.extend(score_failures)

            yax_status = "skipped"
            yax_script = _HERE / "run-yaxunit.ps1"
            generated_yax = _generated_yaxunit_dir(stage_homes, yax_dir)
            impl_home = stage_homes.get("implementer")
            cfe_out = (impl_home / "out" / "cfe") if impl_home is not None else Path()
            if args.require_platform:
                try:
                    proc = _invoke_run_yaxunit(
                        yax_script=yax_script,
                        cf_copy=cf_copy,
                        yax_unit_dir=generated_yax,
                        agent_cfe=cfe_out,
                        work_dir=task_dir / "yaxunit",
                        require_platform=True,
                    )
                except FileNotFoundError:
                    failures.append("RequirePlatform: PowerShell not found")
                    ok = False
                    yax_status = "error"
                else:
                    (task_dir / "logs" / "yaxunit.txt").write_text(
                        (proc.stdout or "") + "\n" + (proc.stderr or ""),
                        encoding="utf-8",
                    )
                    if proc.returncode != 0:
                        failures.append(
                            f"YAxUnit failed (exit {proc.returncode}): "
                            f"{(proc.stderr or proc.stdout or '')[:400]}"
                        )
                        ok = False
                        yax_status = "failed"
                    else:
                        yax_status = "passed"
            elif yax_script.is_file():
                # Best-effort optional run; ignore missing platform.
                try:
                    proc = _invoke_run_yaxunit(
                        yax_script=yax_script,
                        cf_copy=cf_copy,
                        yax_unit_dir=generated_yax,
                        agent_cfe=cfe_out,
                        work_dir=task_dir / "yaxunit",
                        require_platform=False,
                    )
                except FileNotFoundError:
                    yax_status = "skipped"
                else:
                    (task_dir / "logs" / "yaxunit.txt").write_text(
                        (proc.stdout or "") + "\n" + (proc.stderr or ""),
                        encoding="utf-8",
                    )
                    if "SKIP:" in (proc.stdout or ""):
                        yax_status = "skipped"
                    elif proc.returncode == 0:
                        yax_status = "passed"
                    else:
                        yax_status = "skipped"

            if not ok:
                failures = failures or ["scoring failed"]
        except Exception as exc:  # noqa: BLE001 — per-task isolation
            ok = False
            error = str(exc)
            failures.append(error)
            yax_status = "skipped"

        row = {
            "id": task_id,
            "pass": ok,
            "failures": failures,
            "error": error,
            "yaxunit": yax_status,
            "stages": {
                name: {
                    "stop_reason": (stage_outputs.get(name) or {}).get("stop_reason"),
                    "result": (stage_outputs.get(name) or {}).get("result"),
                    "usage": (stage_outputs.get(name) or {}).get("usage"),
                }
                for name, _ in STAGES
                if name in stage_outputs
            },
        }
        results.append(row)
        _write_task_notes(
            notes_dir=_HERE / "notes",
            task_dir=task_dir,
            run_id=run_id,
            row=row,
            expect=expect,
            stage_homes=stage_homes,
        )
        if ok:
            passed += 1
            print(f"PASS {task_id}")
        else:
            failed += 1
            safe_failures = json.dumps(failures, ensure_ascii=True)
            print(f"FAIL {task_id}: {safe_failures}")

    report = {
        "run_id": run_id,
        "product": "sklad",
        "bank_dir": str(bank_dir),
        "passed": passed,
        "failed": failed,
        "total": len(results),
        "tasks": results,
    }
    report_path = run_dir / "report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _write_run_notes(run_dir, _HERE / "notes", report)
    print(f"report: {report_path}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
