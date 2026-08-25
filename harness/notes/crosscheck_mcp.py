#!/usr/bin/env python3
import json
import re
from collections import Counter
from pathlib import Path

from mcp_run_common import STAGES, parse_run_args

task_dir, run_id, pass_status = parse_run_args()
root = task_dir / "logs"
print(f"RUN {run_id} pass={pass_status}")
for stage in STAGES:
    hist = json.loads((root / stage / "chat_history.json").read_text(encoding="utf-8"))
    raw_counts = Counter()
    for msg in hist["messages"]:
        if msg.get("role") != "assistant":
            continue
        c = msg.get("content") or ""
        for m in re.finditer(
            r'"server"\s*:\s*"([^"]+)"\s*,\s*"tool"\s*:\s*"([^"]+)"', c
        ):
            raw_counts[f"{m.group(1)}.{m.group(2)}"] += 1
    tool_msgs = sum(1 for m in hist["messages"] if m.get("role") == "tool")
    print(stage, "assistant_tool_regex", dict(raw_counts), "tool_role_msgs", tool_msgs)
    run = json.loads((root / f"{stage}.run.json").read_text(encoding="utf-8"))
    fails = re.findall(r"tool call failed.*?tool=([^\s]+)", run.get("stderr", ""))
    print("  stderr_fails", dict(Counter(fails)))
    allows = re.findall(r"capability=([^\s]+)", run.get("stderr", ""))
    print("  policy", dict(Counter(allows)))
    m = re.search(r"tools_executed=(\d+)", run.get("stderr", ""))
    print(
        "  tools_executed",
        m.group(1) if m else None,
        "stop",
        hist.get("stop_reason"),
        "iters",
        (hist.get("usage") or {}).get("iterations"),
    )
    # sample failed error messages
    for line in (run.get("stderr") or "").splitlines():
        if "tool call failed" in line and ("code-index" in line or "sntx" in line or "local_tools" in line):
            # extract short error
            em = re.search(r"error=(.{0,180})", line)
            tm = re.search(r"tool=([^\s]+)", line)
            print("  FAIL", tm.group(1) if tm else "?", "->", em.group(1) if em else line[:180])
