# kuibysheff-1c-live

Четырёхстадийный live-eval для [Agent Kuibysheff](https://github.com/gazalievtimur/Agent-Kuibysheff) (`kbshff`) на учебной конфигурации склада 1С:

`analyst → yaxunit → coder → implementer`

Отдельный example-репозиторий: можно изучать оркестрацию CLI с MCP-инструментами 1С или использовать как opt-in gate при разработке агента.

## Требования

- `kbshff` в `PATH`, либо `KBSHFF_BIN`, либо `KUIBYSHEFF_SRC` / соседний checkout
- Python 3
- API-ключ провайдера (по умолчанию `OPENAI_API_KEY`)
- `SNTX_SEM_CONFIG` — путь к `config.yaml` из [`1c-sntx-sem`](https://github.com/gybson63/1c-sntx-sem)
- `BSL_INDEXER` или `CODE_INDEX_BIN` — путь к `bsl-indexer` из [`code-index-mcp`](https://github.com/Regsorm/code-index-mcp)
- `BSL_LS_MCP` + `BSL_LS_JAR` (+ `JAVA_HOME`) — MCP [BSL Language Server](https://github.com/1c-syntax/bsl-language-server) в стиле ЗУП (нужно для yaxunit/coder/implementer)
- Опционально: `SNTX_SEM_PYTHON`, платформа 1С / `ibcmd` (`-RequirePlatform`)

Лаунчер выставляет `KUIBYSHEFF_ALLOW_UNSANDBOXED_MCP=1` (stdio MCP + venv).

## Быстрый старт

```powershell
Copy-Item .\.env.example .\.env
# задайте OPENAI_API_KEY, SNTX_SEM_CONFIG, BSL_INDEXER, BSL_LS_MCP, BSL_LS_JAR

.\harness\run.ps1 -DryRun
.\scripts\1c-live-regression.ps1
```

```bash
cp .env.example .env
./harness/run.sh --dry-run
./scripts/1c-live-regression.sh
```

## Структура

```text
profiles/1c-analyst|yaxunit|coder|implementer|1c-shared
harness/          eval, bank, CF-фикстура, docs YAxUnit
scripts/          resolve-kbshff + тонкая обёртка регрессии
docs/searxng/     опциональные заметки по SearXNG
```

Gate-задача: `cfe-qty-check-01` (по умолчанию). Полный банк: `-All` / `--all`.

## Контракт агента

CLI `init` / `config import` / `run` на каждой стадии — см. [CONTRACT.md](https://github.com/gazalievtimur/Agent-Kuibysheff/blob/main/CONTRACT.md).

Продуктовый конвейер / VS Code (`1c-dev`) остаётся в репозитории агента; здесь только live CF/CFE eval.

## Связанные проекты

Примерные оркестраторы:

- [kuibysheff-aoc](https://github.com/gazalievtimur/kuibysheff-aoc)
- [kuibysheff-swebench](https://github.com/gazalievtimur/kuibysheff-swebench)

MCP-инструменты этого gate:

- [1c-sntx-sem](https://github.com/gybson63/1c-sntx-sem) — справка платформы (`sntx_sem`)
- [code-index-mcp](https://github.com/Regsorm/code-index-mcp) — `bsl-indexer` / `code-index` по CF
- [bsl-language-server](https://github.com/1c-syntax/bsl-language-server) — BSL `analyze` (JAR; Node-bridge как в ЗУП)
- [1c-conf-doc](https://github.com/gybson63/1c-conf-doc) — опциональный MCP по документации конфигурации
