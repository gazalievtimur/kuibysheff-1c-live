# 1c-yaxunit

Стадия 2 конвейера 1c-live: утверждённый план + зафиксированные договорённости → тесты YAxUnit (TDD, падают на baseline CF). Имена gate-процедур — литералы из `in/agreements.md`.

Снимок публичной документации поставляет harness 1c-live как `in/docs/`
(сайт YAxUnit + GitHub, BIA Technologies). SearXNG — опциональное дополнение.

## Зависимости

- MCP [`1c-sntx-sem`](https://github.com/gybson63/1c-sntx-sem)
- [`code-index`](https://github.com/Regsorm/code-index-mcp) по продуктовой CF
- MCP [`bsl-language-server`](https://github.com/1c-syntax/bsl-language-server) (`analyze` по написанному тестовому BSL)
- пакет `in/docs/` (обязателен на eval)
- Опционально SearXNG
