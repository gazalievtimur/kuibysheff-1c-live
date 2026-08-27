# sntx_sem call contract (1c-live)

Source: [`gybson63/1c-sntx-sem`](https://github.com/gybson63/1c-sntx-sem).

Use MCP server name **`sntx_sem`** (not `1c-syntax-sem`). Tools are listed in each profile `skills.dsl` under `platform_help`.

## When (required)

Before writing BSL, extension directives (`&Вместо`, `&ИзменениеИКонтроль`), or platform API claims in plan/code:

1. Call **at least one** of `search_bsl_syntax` or `search_help`.
2. Open the best hit with `get_topic` when the snippet is not enough.
3. Optionally `find_examples` for local-config patterns.

Do **not** invent platform syntax from memory when these tools are in `Available tools`.

## Tool shapes

```json
{"server":"sntx_sem","tool":"search_bsl_syntax","arguments":{"query":"ПередЗаписью","limit":5}}
```

```json
{"server":"sntx_sem","tool":"search_help","arguments":{"query":"&Вместо расширение","domain":"all","limit":5}}
```

```json
{"server":"sntx_sem","tool":"get_topic","arguments":{"topic_id":"<id from search hit>","include_examples":true}}
```

```json
{"server":"sntx_sem","tool":"find_examples","arguments":{"query":"ПередЗаписью Отказ","limit":5}}
```

```json
{"server":"sntx_sem","tool":"search_query_language","arguments":{"query":"ВЫБРАТЬ ПЕРВЫЕ","limit":5}}
```

Domains for `search_help`: `all`, `bsl`, `query`, `bsp`, `platform_api`, …

## Workflow

`search_help` / `search_bsl_syntax` → `get_topic` → (optional) `find_examples`.

Cite what you used briefly in `architecture.md`, `code-report.md`, or `test-report.md` (tool + query).
