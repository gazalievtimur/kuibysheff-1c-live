# Контракт вызовов bsl-language-server (1c-live)

Upstream: [`1c-syntax/bsl-language-server`](https://github.com/1c-syntax/bsl-language-server).
Тот же MCP, что в Cursor-проекте ЗУП: Node-bridge → `bsl-language-server.jar` → `analyze`.

Имя сервера: **`bsl-language-server`**. Tool: **`analyze`**.

## Когда (обязательно)

На стадиях **yaxunit**, **coder** и **implementer** (тестовый и прикладной BSL — оба BSL):

1. Записать BSL под `out/…`.
2. Прочитать абсолютные каталоги из `in/bsl-lint.json` → `src_dirs`.
3. Вызвать `analyze` по каждому записанному дереву (или один раз по основному).
4. Исправить ошибки / важные предупреждения и при изменениях вызвать `analyze` снова.
5. Кратко отметить результат в `test-report.md` / `code-report.md` / `implement-report.md`.

**Не** пропускать lint со словами «тесты — не прод» — модули YAxUnit тоже BSL.

## Форма вызова

```json
{
  "server": "bsl-language-server",
  "tool": "analyze",
  "arguments": {
    "srcDir": "C:/absolute/path/from/in/bsl-lint.json"
  }
}
```

Опционально: `configFile` → путь к `.bsl-language-server.json`.

## Env (harness)

| Переменная | Смысл |
| --- | --- |
| `BSL_LS_MCP` / `BSL_LS_SERVER` | Абсолютный путь к `bsl-ls-mcp/server.js` |
| `BSL_LS_JAR` | Абсолютный путь к `bsl-language-server-*-exec.jar` |
| `JAVA_HOME` | Java 17+ (часто JRE из VS Code `redhat.java`) |
| `BSL_LS_NODE` | Опциональный override для `node` |

Значения по умолчанию совпадают с layout ЗУП: `%USERPROFILE%\.claude\bsl-ls-mcp\` и `bsl-ls\`.
