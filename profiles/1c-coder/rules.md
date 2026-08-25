# 1c-coder rules

- Read `in/agreements-protocol.md` first. Identifiers are literals.
- Missing `in/agreements.json` or `in/agreements.md` → `blocked`.
- Write only `out/` and `notes/`. Never write into product `src/cf`.
- Follow approved `tasks.md` only. No scope expansion.
- Read `in/tests/`; code to those YAxUnit cases, do not rewrite or rename the tests.
- code-index MCP: pass `"repo":"cf"` on every call (`find_symbol` needs `name`; `list_files` uses `path_prefix`/`pattern`).
- sntx_sem: **required** before writing BSL or `&Вместо` / `&ИзменениеИКонтроль` — at least one `search_bsl_syntax` or `search_help`, then `get_topic` if needed. See `profiles/1c-shared/sntx-sem-contract.md`.
- bsl-language-server: **required** after writing `out/src` — `analyze` with absolute `srcDir` from `in/bsl-lint.json`. See `profiles/1c-shared/bsl-ls-contract.md`.
- Skip `cfe_packaging` steps; leave them for 1c-implementer.
- Use extension directives (`&ИзменениеИКонтроль`, `&Вместо`) when patching borrowed methods (explicit OR in the contract).
- No git commit/push via `home.run`.
- `done=true` only after a verification table in `code-report.md`.

# Deliverables

- `out/src/**`
- `out/code-report.md` (includes verification table)
- `out/files-index.md`
- `out/manifest.json` (`apply_mode: none`)

# Response protocol

- Exactly one JSON object per reply.
- **At most one `home.write` per turn** — one file or one source module per iteration. Do not batch many files in one response.
- Write `code-report.md` last, after `out/src/**` is complete.
- `done=true` only after deliverables exist (or blocked report with empty src).
