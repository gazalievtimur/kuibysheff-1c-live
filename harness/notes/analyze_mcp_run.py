#!/usr/bin/env python3
"""Deep MCP / tool analysis for 1c-live gate run."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from mcp_run_common import STAGES, parse_run_args

ROOT: Path
OUT: Path


def parse_assistant_json(content: str) -> dict | None:
    if not content or not isinstance(content, str):
        return None
    text = content.strip()
    # sometimes wrapped
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        # try find first {...}
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except Exception:
            return None


def summarize_args(args: dict) -> str:
    if not isinstance(args, dict):
        return ""
    parts = []
    for k in ("path", "query", "pattern", "uri", "command", "topic", "file", "text", "prompt", "code"):
        if k in args and args[k] is not None:
            s = str(args[k]).replace("\n", " ")
            if len(s) > 90:
                s = s[:87] + "..."
            parts.append(f"{k}={s}")
    return "; ".join(parts[:3])


def classify_usefulness(server: str, tool: str, args: dict, thought: str) -> str:
    """Heuristic label for analysis."""
    st = f"{server}.{tool}"
    path = str((args or {}).get("path") or "")
    q = str((args or {}).get("query") or (args or {}).get("topic") or "")
    if server == "home":
        if tool == "write":
            if path.startswith("out/"):
                return "productive_write"
            return "other_write"
        if tool in {"list", "read"}:
            if path.startswith("in/") or path in {".", "in", "out"}:
                return "necessary_explore"
            if path.startswith("out/"):
                return "verify_read"
            return "explore"
        if tool == "run":
            return "shell_run"
    if server in {"sntx_sem", "sntx-sem"}:
        return "domain_mcp_help"
    if server in {"code-index", "code_index", "bsl"}:
        return "domain_mcp_index"
    if server == "local_tools":
        return "local_tools"
    if "search" in tool or "docs" in tool:
        return "docs_search"
    return "other"


def analyze_stage(stage: str) -> dict:
    hist_path = ROOT / "logs" / stage / "chat_history.json"
    usage_path = ROOT / "logs" / stage / "ai_usage.jsonl"
    run_path = ROOT / "logs" / f"{stage}.run.json"

    calls = []
    thoughts = []
    available_tools = []
    mcp_servers_log = None
    policy_allows = Counter()
    errors = []

    if run_path.exists():
        run = json.loads(run_path.read_text(encoding="utf-8"))
        stderr = run.get("stderr") or ""
        m = re.search(r"mcp_servers=(\d+)", stderr)
        if m:
            mcp_servers_log = int(m.group(1))
        for line in stderr.splitlines():
            if "tool call allowed" in line:
                mm = re.search(r"capability=([^\s]+)", line)
                if mm:
                    policy_allows[mm.group(1)] += 1
            if "ERROR" in line or "failed" in line.lower() or "WARN" in line:
                if "tool" in line.lower() or "mcp" in line.lower() or "sntx" in line.lower() or "code-index" in line.lower():
                    errors.append(line[:300])

    stop_reason = None
    result_text = None
    iterations = 0
    tokens = {"prompt": 0, "completion": 0, "total": 0, "elapsed_ms": None}

    if hist_path.exists():
        hist = json.loads(hist_path.read_text(encoding="utf-8"))
        stop_reason = hist.get("stop_reason")
        result_text = (hist.get("result") or "")[:200]
        usage = hist.get("usage") or {}
        if usage:
            iterations = int(usage.get("iterations") or 0)
            tokens["prompt"] = int(usage.get("prompt_tokens") or 0)
            tokens["completion"] = int(usage.get("completion_tokens") or 0)
            tokens["total"] = int(usage.get("total_tokens") or 0)
            tokens["elapsed_ms"] = usage.get("elapsed_ms")
        messages = hist.get("messages") if isinstance(hist, dict) else hist
        if not isinstance(messages, list):
            messages = []
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            role = msg.get("role")
            content = msg.get("content") or ""
            if role == "user" and "Available tools:" in content:
                m = re.search(r"Available tools:\s*([^\n]+)", content)
                if m:
                    available_tools = [t.strip() for t in m.group(1).split(",") if t.strip()]
            if role != "assistant":
                continue
            parsed = parse_assistant_json(content)
            if not parsed:
                continue
            thought = parsed.get("thought") or ""
            if thought:
                thoughts.append(thought[:200])
            for tc in parsed.get("tool_calls") or []:
                if not isinstance(tc, dict):
                    continue
                server = tc.get("server") or ""
                tool = tc.get("tool") or ""
                args = tc.get("arguments") or {}
                calls.append(
                    {
                        "server": server,
                        "tool": tool,
                        "full": f"{server}.{tool}",
                        "args_summary": summarize_args(args),
                        "path": (args or {}).get("path"),
                        "query": (args or {}).get("query") or (args or {}).get("topic"),
                        "usefulness": classify_usefulness(server, tool, args, thought),
                        "thought": thought[:160],
                    }
                )

    # fallback usage from ai_usage.jsonl if chat_history lacked it
    if iterations == 0 and usage_path.exists():
        for line in usage_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            payload = ev.get("payload") or {}
            iterations = max(iterations, int(payload.get("iteration") or 0))
            u = payload.get("usage") or {}
            tokens["prompt"] += int(u.get("prompt_tokens") or 0)
            tokens["completion"] += int(u.get("completion_tokens") or 0)
            tokens["total"] += int(u.get("total_tokens") or 0)

    by_full = Counter(c["full"] for c in calls)
    by_server = Counter(c["server"] for c in calls)
    by_use = Counter(c["usefulness"] for c in calls)

    # wasted explores: repeated list of same path
    path_reads = Counter()
    for c in calls:
        if c["tool"] in {"list", "read"} and c.get("path"):
            path_reads[f"{c['tool']}:{c['path']}"] += 1
    repeated = {k: v for k, v in path_reads.items() if v > 1}

    mcp_calls = [c for c in calls if c["server"] not in {"home", ""}]
    home_calls = [c for c in calls if c["server"] == "home"]

    return {
        "stage": stage,
        "stop_reason": stop_reason,
        "result": result_text,
        "available_tools": available_tools,
        "mcp_servers_started": mcp_servers_log,
        "iterations": iterations,
        "tokens": tokens,
        "total_tool_calls": len(calls),
        "home_calls": len(home_calls),
        "mcp_calls": len(mcp_calls),
        "by_tool": dict(by_full.most_common()),
        "by_server": dict(by_server.most_common()),
        "by_usefulness": dict(by_use.most_common()),
        "repeated_path_ops": repeated,
        "policy_allows": dict(policy_allows),
        "mcp_related_errors": errors[:20],
        "calls": calls,
        "mcp_call_details": [
            {
                "full": c["full"],
                "args": c["args_summary"],
                "thought": c["thought"],
                "usefulness": c["usefulness"],
            }
            for c in mcp_calls
        ],
    }


def main() -> None:
    global ROOT, OUT
    ROOT, run_id, pass_status = parse_run_args()
    OUT = ROOT / "logs" / "mcp_analysis.json"
    stages = [analyze_stage(s) for s in STAGES]

    # cross-stage MCP availability vs use
    summary = {
        "run_id": run_id,
        "task": "cfe-qty-check-01",
        "pass": pass_status,
        "stages": {},
        "totals": {
            "tool_calls": 0,
            "home": 0,
            "mcp": 0,
            "by_server": Counter(),
            "by_tool": Counter(),
            "by_usefulness": Counter(),
            "mcp_never_used_but_available": [],
        },
    }

    all_available = set()
    all_used_full = set()

    for st in stages:
        summary["stages"][st["stage"]] = {
            k: st[k]
            for k in (
                "stop_reason",
                "result",
                "available_tools",
                "mcp_servers_started",
                "iterations",
                "tokens",
                "total_tool_calls",
                "home_calls",
                "mcp_calls",
                "by_tool",
                "by_server",
                "by_usefulness",
                "repeated_path_ops",
                "mcp_related_errors",
                "mcp_call_details",
            )
        }
        summary["totals"]["tool_calls"] += st["total_tool_calls"]
        summary["totals"]["home"] += st["home_calls"]
        summary["totals"]["mcp"] += st["mcp_calls"]
        for k, v in st["by_server"].items():
            summary["totals"]["by_server"][k] += v
        for k, v in st["by_tool"].items():
            summary["totals"]["by_tool"][k] += v
        for k, v in st["by_usefulness"].items():
            summary["totals"]["by_usefulness"][k] += v
        for t in st["available_tools"]:
            all_available.add(t)
        for t in st["by_tool"]:
            all_used_full.add(t)

    used_prefixes = set()
    for t in all_used_full:
        used_prefixes.add(t)
        if "." in t:
            used_prefixes.add(t.split(".", 1)[0])

    never = []
    for avail in sorted(all_available):
        # avail is like code-index.list_files
        if avail not in all_used_full:
            # also check if any call used that exact
            never.append(avail)
    summary["totals"]["mcp_never_used_but_available"] = never
    summary["totals"]["by_server"] = dict(summary["totals"]["by_server"].most_common())
    summary["totals"]["by_tool"] = dict(summary["totals"]["by_tool"].most_common())
    summary["totals"]["by_usefulness"] = dict(summary["totals"]["by_usefulness"].most_common())

    # print report
    print(f"RUN {summary['run_id']} task={summary['task']} pass={summary['pass']}")
    print(
        f"TOTAL tool_calls={summary['totals']['tool_calls']} "
        f"home={summary['totals']['home']} mcp={summary['totals']['mcp']}"
    )
    print("BY SERVER:", summary["totals"]["by_server"])
    print("BY TOOL:", summary["totals"]["by_tool"])
    print("BY USE:", summary["totals"]["by_usefulness"])
    print("AVAILABLE BUT NEVER USED:", never)
    print()
    for st in stages:
        print(f"=== {st['stage']} ===")
        print(
            f"  stop={st['stop_reason']} iters={st['iterations']} tools={st['total_tool_calls']} "
            f"home={st['home_calls']} mcp={st['mcp_calls']} "
            f"mcp_servers_started={st['mcp_servers_started']}"
        )
        print(f"  available: {st['available_tools']}")
        print(f"  by_tool: {st['by_tool']}")
        print(f"  usefulness: {st['by_usefulness']}")
        if st["repeated_path_ops"]:
            print(f"  repeated: {st['repeated_path_ops']}")
        if st["mcp_call_details"]:
            print("  MCP calls:")
            for d in st["mcp_call_details"]:
                print(f"    - {d['full']} | {d['args']} | {d['thought'][:80]}")
        if st["mcp_related_errors"]:
            print("  mcp/tool warnings:")
            for e in st["mcp_related_errors"][:5]:
                print(f"    ! {e}")
        print()

    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
