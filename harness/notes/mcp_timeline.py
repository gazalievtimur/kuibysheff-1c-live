#!/usr/bin/env python3
"""Rebuild tool timeline from stderr policy lines + chat thoughts where available."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from mcp_run_common import STAGES, parse_run_args

ROOT: Path


def parse_stderr(stage: str) -> dict:
    run = json.loads((ROOT / "logs" / f"{stage}.run.json").read_text(encoding="utf-8"))
    stderr = run.get("stderr") or ""
    allows = []
    fails = []
    for line in stderr.splitlines():
        if "tool call allowed" in line:
            m = re.search(r"capability=([^\s\"]+)", line)
            if m:
                allows.append(m.group(1).strip('"'))
        if "tool call failed" in line:
            tm = re.search(r"tool=([^\s]+)", line)
            em = re.search(r"error=(.*)$", line)
            fails.append(
                {
                    "tool": tm.group(1) if tm else "?",
                    "error": (em.group(1) if em else line)[:220],
                }
            )
    te = re.search(r"tools_executed=(\d+)", stderr)
    mcp_n = re.search(r"mcp_servers=(\d+)", stderr)
    return {
        "allows": allows,
        "allow_counts": Counter(allows),
        "fails": fails,
        "fail_counts": Counter(f["tool"] for f in fails),
        "tools_executed": int(te.group(1)) if te else None,
        "mcp_servers": int(mcp_n.group(1)) if mcp_n else None,
    }


def classify(cap: str) -> str:
    if cap.startswith("home."):
        return "home"
    if cap.startswith("code-index"):
        return "mcp:code-index"
    if cap.startswith("sntx_sem") or cap.startswith("sntx-sem"):
        return "mcp:sntx_sem"
    if cap.startswith("bsl-language-server"):
        return "mcp:bsl-ls"
    if cap.startswith("local_tools"):
        return "local_tools"
    return "other"


def main() -> None:
    global ROOT
    ROOT, run_id, _pass = parse_run_args()
    hist_notes = {}
    for stage in STAGES:
        hist = json.loads((ROOT / "logs" / stage / "chat_history.json").read_text(encoding="utf-8"))
        # extract any MCP/local tool args from assistant messages
        mcpish = []
        for msg in hist["messages"]:
            if msg.get("role") != "assistant":
                continue
            try:
                parsed = json.loads(msg["content"])
            except Exception:
                continue
            for tc in parsed.get("tool_calls") or []:
                server = tc.get("server")
                if server in {"home", None}:
                    continue
                mcpish.append(
                    {
                        "server": server,
                        "tool": tc.get("tool"),
                        "args": {
                            k: (str(v)[:100] if not isinstance(v, (dict, list)) else type(v).__name__)
                            for k, v in (tc.get("arguments") or {}).items()
                        },
                        "thought": (parsed.get("thought") or "")[:180],
                    }
                )
        avail = []
        for msg in hist["messages"]:
            if msg.get("role") == "user" and "Available tools:" in (msg.get("content") or ""):
                m = re.search(r"Available tools:\s*([^\n]+)", msg["content"])
                if m:
                    avail = [t.strip() for t in m.group(1).split(",") if t.strip()]
        hist_notes[stage] = {
            "available": avail,
            "mcpish_in_chat": mcpish,
            "stop": hist.get("stop_reason"),
            "usage": hist.get("usage"),
            "result": (hist.get("result") or "")[:160],
        }

    print("=== AUTHORITATIVE (stderr policy) ===\n")
    grand = Counter()
    grand_class = Counter()
    grand_fail = Counter()
    for stage in STAGES:
        s = parse_stderr(stage)
        hn = hist_notes[stage]
        print(f"## {stage}  stop={hn['stop']} iters={(hn['usage'] or {}).get('iterations')} tools_executed={s['tools_executed']} mcp_servers={s['mcp_servers']}")
        print(f"   available: {hn['available']}")
        print(f"   executed: {dict(s['allow_counts'])}")
        byc = Counter(classify(c) for c in s["allows"])
        print(f"   by_class: {dict(byc)}")
        print(f"   fails: {dict(s['fail_counts'])}")
        for f in s["fails"]:
            print(f"      FAIL {f['tool']}: {f['error'][:160]}")
        if hn["mcpish_in_chat"]:
            print("   mcp/local args preserved in chat_history:")
            for x in hn["mcpish_in_chat"]:
                print(f"      {x['server']}.{x['tool']} args={x['args']}")
                print(f"         thought: {x['thought']}")
        else:
            print("   mcp/local args in chat_history: (none / compacted away)")
        # sntx used?
        sntx_used = any(c.startswith("sntx") for c in s["allows"])
        print(f"   sntx_sem used: {sntx_used}")
        print()
        grand.update(s["allow_counts"])
        grand_class.update(byc)
        grand_fail.update(s["fail_counts"])

    print("=== TOTALS ===")
    print("executed:", dict(grand))
    print("by_class:", dict(grand_class))
    print("fails:", dict(grand_fail))
    ok = sum(grand.values()) - sum(grand_fail.values())
    print(f"success_est={ok} fail={sum(grand_fail.values())} success_rate={ok/max(1,sum(grand.values())):.1%}")

    # effectiveness narrative helpers
    mcp_exec = sum(v for k, v in grand.items() if k.startswith("code-index") or k.startswith("sntx") or k.startswith("local_tools"))
    mcp_fail = sum(v for k, v in grand_fail.items() if k.startswith("code-index") or k.startswith("sntx") or k.startswith("local_tools"))
    print(f"non-home tool attempts={mcp_exec} fails={mcp_fail}")

    out = {
        "run": run_id,
        "totals_executed": dict(grand),
        "by_class": dict(grand_class),
        "fails": dict(grand_fail),
        "stages": {st: {"stderr": parse_stderr(st), "chat": hist_notes[st]} for st in STAGES},
    }
    # make counters serializable
    for st, data in out["stages"].items():
        data["stderr"]["allow_counts"] = dict(data["stderr"]["allow_counts"])
        data["stderr"]["fail_counts"] = dict(data["stderr"]["fail_counts"])
        data["stderr"].pop("allows", None)

    path = ROOT / "logs" / "mcp_analysis_v2.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", path)


if __name__ == "__main__":
    main()
