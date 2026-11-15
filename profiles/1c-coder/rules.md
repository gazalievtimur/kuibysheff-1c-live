# 1c-coder rules

- Read `in/agreements-protocol.md` first on the first pass. Identifiers are literals.
- Missing `in/agreements.md` → `blocked`. Copy literals from that file. An empty `expect.json` is not `blocked`.
- Keep working memory in `out/coder_memory.md`. If the file is absent, do not `home.read` it: read `in/agreements-protocol.md`, `in/code-index-contract.md`, `in/agreements.md`, `in/tasks.md`, `in/artifact.json`, and `in/tests/` once, then `home.write` `out/coder_memory.md`. If one of those inputs is absent, record that once and do not read that path again.
- If `out/coder_memory.md` exists but its text is not in this turn, the only tool call is `home.read` of `out/coder_memory.md`. Do not open the plan `in/` files again. When the pinned copy of that file is already in the turn, do not re-read it.
- Write `out/coder_memory.md` before iteration 3. Sections: Status, Contract, Facts, Next, Stopped. Set `inputs_read: yes`. Facts holds the last code-index hit (`file_path`, `line_start`, `line_end`, procedure name). Next is not another `find_symbol`.
- While `inputs_read: yes`, do not read those plan `in/` files again. A memory update is the one `home.write` of that turn. Do not call code-index until `inputs_read: yes`. Record Facts before the first `out/src` write.
- Write the first file under `out/src/` by iteration 12. One `home.write` per turn: either `out/coder_memory.md` or one file under `out/`.
- Write `out/` only. Never write `coder_memory.md` at the home root, never write `notes/`, and never write into product `src/cf`.
- Follow approved `tasks.md` only. No scope expansion.
- Copy the test's called module and method into Contract verbatim and implement that call. Do not rewrite or rename tests. Query existing balances. Do not post documents or write registers to fabricate stock.
- If the test requires an effect that is neither in `tasks.md` nor produced by the test's own data, set phase `blocked`, leave `out/src` empty, and write the blocked report.
- code-index MCP: call only tools in `Available MCP tools`. Arguments come from `agent.describe_tool`. Follow `in/code-index-contract.md`. Skill `code-index` via `profile.read_skill` if needed. Empty hits → treat as failure; do not start `out/scan*.py`. Do not call `code-index.search` or `code-index.get_file`. Do not page metadata XML via ad-hoc python. Write the hit into Facts before the next lookup.
- If code-index/form-info contradicts agreements (missing form element, only a suffixed real name, wrong handler target): write corrected `out/agreements.md` in that turn, update Facts, then implement. Do not proceed on known-wrong literals.
- `home.read` stays inside the task home (`in`/`out` only). Read skill instructions with `profile.read_skill` (skill name only — never `path` to `scripts/*`). Run the script with `home.run` program `python` at the absolute path named in the skill; pass `-ConfigPath` from the contract. Do not hand-write a borrowed form. Do not git commit or push.
- **Forbidden** `home.run` `python -c` / one-liners that open `Form.xml` or `Configuration.xml`. Use `form-info` / `form-validate` / code-index only.
- sntx_sem: **required** before writing BSL or `&Вместо` / `&ИзменениеИКонтроль` — at least one successful `search_bsl_syntax` or `search_help`, then `get_topic` with `topic_id` if needed. After two timeouts → stop; see `sntx-sem-contract.md` beside this profile.
- bsl-language-server: **required** after writing `out/src` — `analyze` with absolute `srcDir` = this home’s `out/src` (no `\\?\`). Use `in/bsl-lint.json` only if its `srcDir` is under this same home and ends with `out/src`; otherwise ignore stale paths from other tasks. See `bsl-ls-contract.md` beside this profile (also skill `bsl-language-server`).
- Skip `cfe_packaging` steps; leave them for 1c-implementer.
- `in/artifact.json` `kind` `cfe`: use extension directives (`&ИзменениеИКонтроль`, `&Вместо`) when patching borrowed methods (explicit OR in the contract). `epf` / `erf`: do not use those directives.
- CFE form tasks: `form-edit` JSON should add UI **and** `elementEvents` (e.g. `OnActivateRow` + `callType`) together when agreements require handlers; then write full `Module.bsl` (handlers + fill). Table/query without wired handlers is not done.
- No git commit/push via `home.run`.
- `done=true` only after the CFE form behavior gate (if applicable), lint, verification table in `code-report.md`, and non-stale `coder_memory` `Next`.

# Deliverables

- `out/coder_memory.md` (working memory)
- `out/src/**`
- `out/code-report.md` (includes verification table)
- `out/files-index.md`
- `out/manifest.json` (`apply_mode: none`)

# Response protocol

- Exactly one JSON object per reply. A raw file body may follow it; nothing else may. **Never DSML** or other tool-call markup. Never invent tools. Never `home.list` path `.`.
- **At most one `home.write` per turn** — `out/coder_memory.md`, one source module, or one report. Short and medium files go in `arguments.content`. Use a `<<<FILE` body only when the JSON string cannot hold the file. Do not batch many files in one response.
- Write `code-report.md` last, after `out/src/**` is complete (including wired handlers). Do not leave `out/scan*` or `out/grep_form.py`.
- `done=true` only after deliverables exist (or blocked report with empty src) and `coder_memory` `Next` is not stale.
- Confirm open-question / corrected names into `out/agreements.md` before first `out/src` use of those names.
- `profile.read_skill`: skill name only (no `path` to `scripts/*`). Run scripts via `home.run` + absolute path from the skill text; pass `-ConfigPath` from `in/product.json` `cf_root`, as `in/code-index-contract.md` says.
- `sntx_sem`: one successful lookup is enough; after two timeouts in the run → `sntx_sem_degraded`, stop retrying.
- JSON protocol: escape backslashes in strings (`C:\\\\path`); never emit DSML/`invoke` markup.
