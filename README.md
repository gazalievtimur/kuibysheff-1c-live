# kuibysheff-1c-live

Четырёхстадийный live-eval для [Agent Kuibysheff](https://github.com/gazalievtimur/Agent-Kuibysheff) (`kbshff`) на учебной конфигурации склада 1С:

`analyst → yaxunit → coder → implementer`

Отдельный example-репозиторий: можно изучать оркестрацию CLI с MCP-инструментами 1С или использовать как opt-in gate при разработке агента.

**Как провести задачу по цепочке** (установка, CLI-конфиг, стадии, свой JSON в банке): [docs/howto-pipeline.md](docs/howto-pipeline.md).

## Требования

- [OneScript](https://oscript.io/) 2.0 (`oscript` в `PATH`). Канон оркестратора: `oscript -encoding=utf-8 harness/run.os`. OPM-пакеты не нужны.
- `kbshff` в `PATH`, либо `KBSHFF_BIN`, либо `KUIBYSHEFF_SRC` / соседний checkout
- API-ключ провайдера в env (по умолчанию `OPENAI_API_KEY`). Параметры модели — через CLI `kbshff config … provider set`, не правкой protected YAML. Справка: `kbshff help config`
- `SNTX_SEM_CONFIG` — путь к `config.yaml` из [`1c-sntx-sem`](https://github.com/gybson63/1c-sntx-sem)
- `BSL_INDEXER` или `CODE_INDEX_BIN` — путь к `bsl-indexer` из [`code-index-mcp`](https://github.com/Regsorm/code-index-mcp)
- `BSL_LS_MCP` + `BSL_LS_JAR` (+ `JAVA_HOME`) — MCP [BSL Language Server](https://github.com/1c-syntax/bsl-language-server) (`tools/bsl-ls-mcp` или layout `~\.claude\bsl-ls-mcp`)
- Node + Java — runtime MCP `bsl-language-server` (не harness)
- Python — **только** runtime MCP `sntx_sem`: явный `SNTX_SEM_PYTHON`, либо `1c-sntx-sem/.venv/.../python`, либо бинарь `sntx-sem` в `PATH`. Интерпретатор harness сюда не подставляется.
- Опционально: платформа 1С / `ibcmd` (`--require-platform`)

Лаунчер выставляет `KUIBYSHEFF_ALLOW_UNSANDBOXED_MCP=1` (stdio MCP + venv).

## Быстрый старт

```powershell
.\scripts\install.ps1
# спросит base_url / model / api_key_env и ключ; поставит MCP в tools\;
# применит провайдера: kbshff config … provider set
.\harness\run.ps1 -DryRun
.\harness\run.ps1
```

```bash
./scripts/install.sh
oscript -encoding=utf-8 harness/run.os --dry-run
./harness/run.sh
```

Без install: скопируйте `.env.example` → `.env`, задайте ключ и пути, затем:

```text
kbshff config --project-root <DIR> --agent 1c-analyst provider set \
  --base-url "$KBSHFF_PROVIDER_BASE_URL" \
  --model "$KBSHFF_PROVIDER_MODEL" \
  --api-key-env "$KBSHFF_PROVIDER_API_KEY_ENV"
```

Gate-задача: `cfe-qty-check-01` (по умолчанию). Полный банк: `-All` / `--all`.

## Структура

```text
profiles/1c-analyst|yaxunit|coder|implementer|1c-shared
harness/          OneScript eval, bank, CF-фикстура, docs YAxUnit
scripts/          install, resolve-kbshff, регрессия
tools/bsl-ls-mcp  Node-мост analyze(srcDir) → JAR
docs/howto-pipeline.md
docs/searxng/     опциональные заметки по SearXNG
```

## Контракт агента

CLI `init` / `config import` / `config provider set` / `run` на каждой стадии — см. [CONTRACT.md](https://github.com/gazalievtimur/Agent-Kuibysheff/blob/main/CONTRACT.md) и `kbshff help config`.

Продуктовый конвейер / VS Code (`1c-dev`) остаётся в репозитории агента; здесь только live CF/CFE eval.

## Связанные проекты

Примерные оркестраторы:

- [kuibysheff-aoc](https://github.com/gazalievtimur/kuibysheff-aoc)
- [kuibysheff-swebench](https://github.com/gazalievtimur/kuibysheff-swebench)

MCP-инструменты этого gate:

- [1c-sntx-sem](https://github.com/gybson63/1c-sntx-sem) — справка платформы (`sntx_sem`)
- [code-index-mcp](https://github.com/Regsorm/code-index-mcp) — `bsl-indexer` / `code-index` по CF
- [bsl-language-server](https://github.com/1c-syntax/bsl-language-server) — BSL `analyze` (JAR; Node-мост `tools/bsl-ls-mcp`)
- [1c-conf-doc](https://github.com/gybson63/1c-conf-doc) — опциональный MCP по документации конфигурации
