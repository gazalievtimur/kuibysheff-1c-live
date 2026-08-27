# Контракт вызовов sntx_sem (1c-live)

Источник: [`gybson63/1c-sntx-sem`](https://github.com/gybson63/1c-sntx-sem).

Имя MCP-сервера: **`sntx_sem`** (не `1c-syntax-sem`). Инструменты перечислены в `skills.dsl` каждого профиля в блоке `platform_help`.

## Когда (обязательно)

Перед написанием BSL, директив расширения (`&Вместо`, `&ИзменениеИКонтроль`) или утверждений про API платформы в плане/коде:

1. Вызвать **хотя бы один** из `search_bsl_syntax` или `search_help`.
2. Открыть лучший hit через `get_topic`, если сниппета недостаточно.
3. По желанию `find_examples` для паттернов из локальных конфигураций.

**Не** выдумывать синтаксис платформы из памяти, пока эти tools есть в `Available tools`.

## Формы вызовов

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

Домены для `search_help`: `all`, `bsl`, `query`, `bsp`, `platform_api`, …

## Workflow

`search_help` / `search_bsl_syntax` → `get_topic` → (опционально) `find_examples`.

Кратко укажите, чем пользовались, в `architecture.md`, `code-report.md` или `test-report.md` (tool + query).
