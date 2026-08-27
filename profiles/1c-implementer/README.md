# 1c-implementer

1c-live stage 4: coder sources → apply-ready `out/cfe/` using agreements identifiers; copy `in/cfe-tests/` → `out/cfe-tests/` without rewriting tests. Orchestrator copies via `adapters/default/apply-out.ps1` (or `adapters/<product>/`) and optionally runs BuildCfe.

## Dependencies

- [`code-index`](https://github.com/Regsorm/code-index-mcp) / [`sntx_sem`](https://github.com/gybson63/1c-sntx-sem) as needed
- [`bsl-language-server`](https://github.com/1c-syntax/bsl-language-server) MCP (`analyze` on packed `out/cfe`)
