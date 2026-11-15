# 1c-yaxunit rules

- Read `in/agreements-protocol.md` first. Identifiers are literals.
- Missing `in/agreements.md` → `blocked`. Do not invent names. Copy literals from that file.
- Read `in/docs/` before writing any BSL. Do not invent YAxUnit API.
- Gate procedure: `expect.yaxunit.procedure` when it is set, otherwise the test procedure name in `agreements.md`. `expect.test_contains`, when present, is an exact BSL identifier. Do not rename the gate procedure. Extra tests are allowed. Empty `expect` with `agreements.md` present is not `blocked`.
- No synonyms, translation, or “clearer” names.
- Assert the effect of `Записать`, not a disconnected local `Отказ`.
- Test server code and data only. YAxUnit is a poor fit for UI: do not call `ОткрытьФорму`, do not assert form items, the current row, decorations, or client handlers, and do not write smoke form-open tests (`ДымовыеТесты.ОткрытиеФорм`). For balances, call the server function from agreements and assert the value table (warehouse filled, free balance equals the expected quantity). On baseline the test fails because that method does not exist yet. Create data with `ЮТест.Данные()` or read existing balances; do not post documents only to fill a form.
- SearXNG: only `bia-technologies.github.io/yaxunit` and `github.com/bia-technologies/yaxunit`. Cite URLs in `test-report.md`. Never use ITS or closed Infostart as requirements.
- Write only under `out/` and `notes/`. Never modify product CF.
- code-index MCP: call only tools in `Available MCP tools`. Arguments come from `agent.describe_tool`. Follow `in/code-index-contract.md`. Do not call `code-index.search` or `code-index.get_file`. Do not page the module with `local_tools.read_file`.
- sntx_sem: **required** before BSL that touches platform write/refuse APIs — at least one `search_bsl_syntax` or `search_help`. See `sntx-sem-contract.md` beside this profile.
- bsl-language-server: **required** after writing tests — `analyze` with absolute `srcDir` of this home (ignore stale `in/bsl-lint.json` from another task). See `bsl-ls-contract.md` beside this profile.
- Do not implement the feature under test. Tests must describe expected behavior from the plan (fail on baseline).
- Registration only inside `ИсполняемыеСценарии`. Test data in test procedures (or `ЮТест.Данные()`), not in registration.
- Register with `ДобавитьСерверныйТест`. Prefer `ВТранзакции` when the test writes or posts. Do not use `ДобавитьКлиентскийТест` for form UI.
- `done=true` only after a verification table in `test-report.md`.

# Deliverables

- `out/tests/**/*.bsl`
- `out/cfe-tests/` (minimal CFE tree)
- `out/test-report.md` (docs sources + procedure list + verification table)
- `out/manifest.json` (`apply_mode: none`)

# Response protocol

- Exactly one JSON object per reply.
- Put each file in `arguments.content`. Use a `<<<FILE` body only after a `home.write` of that path was not executed because the JSON object was unterminated.
- `done=true` only after deliverables exist (or a blocked report).
