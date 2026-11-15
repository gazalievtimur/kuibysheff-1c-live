# 1c-implementer rules

- Read `in/agreements-protocol.md` first. Identifiers are literals.
- Missing `in/agreements.md` → `blocked`. Copy literals from that file. An empty `expect.json` is not `blocked`.
- Package only; do not invent business logic.
- Trivial XML/path fixups allowed; feature gaps → report and stop expanding.
- Read `in/artifact.json`. For `cfe`, copy `in/cfe-tests/` to `out/cfe-tests/` as-is. For `epf` / `erf`, package `out/epf` or `out/erf` and do not copy test extensions. Do not invent, rewrite, or rename tests.
- Do not rewrite identifiers in feature BSL/XML.
- Write only under `out/` / `notes/`.
- code-index MCP: call only tools in `Available MCP tools`. Arguments come from `agent.describe_tool`. Follow `in/code-index-contract.md`. Do not call `code-index.search` or `code-index.get_file`.
- bsl-language-server: **required** after packing BSL — `analyze` with absolute `srcDir` of this home’s packed tree; ignore stale `in/bsl-lint.json` from another home. See `bsl-ls-contract.md` beside this profile.
- `manifest.apply_mode` must be `copy_out`.
- Do not run BuildCfe or load IB inside the agent loop. Check the packed tree with profile skills `cfe-validate` and `form-validate` via `home.run` program `python`. Do not invent attributes that are absent from coder sources.
- `done=true` only after a verification table in `implement-report.md`.

# Deliverables

- `out/cfe/**` for `kind=cfe`, or `out/epf/**` / `out/erf/**` for an external object (`<Name>.xml` plus `<Name>/Ext/`)
- `out/cfe-tests/**` only for `cfe`, when incoming test CFE is present
- `out/implement-report.md` (includes verification table)
- `out/checklist.md`
- `out/manifest.json` (`apply_mode: copy_out`)

# Response protocol

- Exactly one JSON object per reply.
- Short and medium files go in `arguments.content`. Use a `<<<FILE` body only when the JSON string cannot hold the file.
- `done=true` only after deliverables exist and the verification table is written.
