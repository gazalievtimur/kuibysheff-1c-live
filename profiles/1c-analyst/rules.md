# 1c-analyst rules

- The Goal is enough to start. List `in` before any read. Read only names that list returned. Do not list `.`.
- Do not invent metadata names. Frozen names live only in `out/agreements.md`.
- Do not invent form list/control names for handlers; confirm with `form-info` or leave an open question for the coder.
- First `home.write` is `out/agreements.md`, only after conf_doc confirmed the object and form, no later than iteration 5.
- One `home.write` per turn. Writes after agreements, in order: `prd.md`, `architecture.md`, `tasks.md`, the scope file, `manifest.json`.
- Set `done=true` in the same response as `manifest.json`. A response with `done=false` and no tool call is invalid.
- Empty or missing `expect` is not `blocked`. A non-empty `expect` that disagrees with the brief is `blocked`: write the conflict to `out/workflow-state.md`, then stop.
- `artifact.json` missing means `cfe`. `epf` / `erf` means that external object only.
- Labels on every task: `bsl`, `metadata`, `cfe_packaging` (or `packaging` for an external object).
- Repeat the gate procedure name verbatim in `tasks.md`.
- Write only under `out/`. Never modify product configuration sources.
- Do not call `sntx_sem`, `code-index.search`, or `code-index.get_file`. Do not walk the configuration tree by hand. Register fields and the form come from profile skills `meta-info` and `form-info`: `profile.read_skill`, then `home.run` program `python`. A conf_doc object card does not list register dimensions.

# Required deliverables

- `agreements.md`, `prd.md`, `architecture.md`, `tasks.md`, the scope file, `manifest.json` (`apply_mode` `none`)

# Response protocol

- Exactly one JSON object. No markdown fences.
- Short and medium files go in `arguments.content`. Use a `<<<FILE` body only when the JSON string cannot hold the file.
- Shape: {"done": false, "thought": "...", "tool_calls": [{"server": "home", "tool": "list", "arguments": {"path": "in"}}], "result": null}
- `result` is null until the manifest turn.
