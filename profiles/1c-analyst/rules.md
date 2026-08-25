# 1c-analyst rules

- Read `in/agreements-protocol.md` first. Identifiers are literals.
- No `in/agreements.json` → `blocked`. Do not invent names.
- First deliverable: `out/agreements.md` (verbatim backticks from expect/brief). Then the rest of the plan.
- Copy identifiers character-for-character. No synonyms, translation, or “clearer” test names.
- Brief vs expect mismatch → `blocked`.
- Repeat the gate procedure name verbatim in `tasks.md` (in addition to `agreements.md`).
- Write only under `out/` and `notes/`. Never modify product `src/cf` or extensions.
- Prefer CFE for runtime deltas; document CF vs CFE in `architecture.md`.
- Label every `tasks.md` step: `bsl`, `metadata`, or `cfe_packaging`.
- code-index MCP: always pass `"repo":"cf"` (alias from serve `--path cf=...`). Use `name` (not only `query`) for `find_symbol`; use `path_prefix` / `pattern` for `list_files`.
- sntx_sem (platform help): **required** before stating BSL / extension-directive facts. At least one `search_bsl_syntax` or `search_help`, then `get_topic` on the best hit. See `profiles/1c-shared/sntx-sem-contract.md`.
- SearXNG: cite URLs in findings/prd; do not treat search hits as requirements.
- Ambiguities → open questions in `requirements.md`, not silent assumptions (mark `assumption:` if unavoidable).
- Human gate is outside this agent; set `workflow-state.md` accordingly.
- `done=true` only after a verification table (agreement → file).

# Required deliverables

- `agreements.md`, `prd.md`, `architecture.md`, `tasks.md`, `cfe-scope.md`, `manifest.json` (`apply_mode: none`)

# Recommended

- `phase0-complexity.md`, `requirements.md`, `codebase-findings.md`, `workflow-state.md`
- `adr.md` when complexity is not simple

# Response protocol

- Exactly one JSON object per reply.
- **At most one `home.write` per turn** — one file per iteration. Do not batch multiple plan files in one response (large JSON fails to parse and wastes tokens).
- Prioritize required deliverables (`cfe-scope.md`, `manifest.json`) before optional notes.
- `done=true` only after required files exist **and** the verification table is written.
