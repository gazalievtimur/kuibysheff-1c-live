# 1c-implementer

Стадия 4 конвейера 1c-live: исходники coder → готовое к применению `out/cfe/` с идентификаторами из договорённостей; копия `in/cfe-tests/` → `out/cfe-tests/` без переписывания тестов. Оркестратор копирует через `adapters/default/apply-out.ps1` (или `adapters/<product>/`) и при необходимости запускает BuildCfe.

## Зависимости

- [`code-index`](https://github.com/Regsorm/code-index-mcp) / [`sntx_sem`](https://github.com/gybson63/1c-sntx-sem) по необходимости
- MCP [`bsl-language-server`](https://github.com/1c-syntax/bsl-language-server) (`analyze` по упакованному `out/cfe`)
