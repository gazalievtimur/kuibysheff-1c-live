# 1c-analyst

Стадия 1 конвейера 1c-live: бриф + исследование CF → зафиксированный `out/agreements.md` + план на утверждение. Опциональный веб-поиск через SearXNG.

Идентификаторы из `in/agreements.json` — литералы (см. [`../1c-shared/agreements-protocol.md`](../1c-shared/agreements-protocol.md)).

## Зависимости

- MCP [`1c-sntx-sem`](https://github.com/gybson63/1c-sntx-sem) (`python -m sntx_sem.mcp_server`)
- [`code-index`](https://github.com/Regsorm/code-index-mcp) / `bsl-indexer` на продуктовую CF
- SearXNG MCP по `mcp.searxngUrl` (по умолчанию `http://127.0.0.1:3000/mcp`)
- Опционально: MCP [`1c-conf-doc`](https://github.com/gybson63/1c-conf-doc)

Оркестратор предупреждает и продолжает, если SearXNG недоступен, если не указан `-RequireSearx`.
