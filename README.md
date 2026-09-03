# kuibysheff-1c-live

Четырёхстадийный live-eval для [Agent Kuibysheff](https://github.com/gazalievtimur/Agent-Kuibysheff) (`kbshff`) на учебной конфигурации склада 1С:

`analyst → yaxunit → coder → implementer`

Отдельный example-репозиторий: можно изучать оркестрацию CLI с MCP-инструментами 1С или использовать как opt-in gate при разработке агента.

**Как провести задачу по цепочке** (установка, CLI-конфиг, стадии, свой JSON в банке): [docs/howto-pipeline.md](docs/howto-pipeline.md).

## Требования

- [OneScript](https://oscript.io/) 2.0 (`oscript` в `PATH`). Канон оркестратора: `oscript -encoding=utf-8 harness/run.os`. OPM-пакеты не нужны.
- `kbshff` в `PATH`, либо `KBSHFF_BIN`, либо install скачает release в `tools/` (Windows/Linux x86_64). `cargo` — только fallback, если release недоступен
- API-ключ провайдера в env (имя по умолчанию — плейсхолдер `OPENAI_API_KEY`). Параметры модели — через CLI `kbshff config … provider set`, не правкой protected YAML. Справка: `kbshff help config`
- `SNTX_SEM_CONFIG` — путь к `config.yaml` из [`1c-sntx-sem`](https://github.com/gybson63/1c-sntx-sem)
- `BSL_INDEXER` или `CODE_INDEX_BIN` — путь к `bsl-indexer` из [`code-index-mcp`](https://github.com/Regsorm/code-index-mcp)
- `BSL_LS_MCP` + `BSL_LS_JAR` (+ `JAVA_HOME`) — MCP [BSL Language Server](https://github.com/1c-syntax/bsl-language-server) (`tools/bsl-ls-mcp` или layout `~\.claude\bsl-ls-mcp`)
- Node + Java — runtime MCP `bsl-language-server` (не harness)
- Python — **только** runtime MCP `sntx_sem`: явный `SNTX_SEM_PYTHON`, либо `1c-sntx-sem/.venv/.../python`, либо бинарь `sntx-sem` в `PATH`. Интерпретатор harness сюда не подставляется.
- Опционально: платформа 1С / `ibcmd` (`--require-platform`)

Лаунчер выставляет `KUIBYSHEFF_ALLOW_UNSANDBOXED_MCP=1` (stdio MCP + venv).

## Быстрый старт

Install — машинный bootstrap: хост-проверки, MCP в `tools/`, секреты в `.env`, профили `kbshff`. Пути `SNTX_SEM_*` / `BSL_*` из раздела «Требования» руками заполнять не нужно: скрипт скачает или переиспользует соседние clone. Подробности и флаги: [docs/howto-pipeline.md](docs/howto-pipeline.md).

### Что подготовить

В `PATH` уже должны быть [OneScript](https://oscript.io/) 2.0 (`oscript`), Git, Node.js, Java 17+, Python 3. На Linux для распаковки `kbshff` нужен ещё `unzip`.

CLI агента: install сам найдёт `kbshff` в `PATH` / `KBSHFF_BIN` / соседнем checkout или **скачает** готовый бинарь из [GitHub Releases](https://github.com/gazalievtimur/Agent-Kuibysheff/releases) в `tools/` (Windows и Linux x86_64; без системных прав). `cargo` нужен только если release недоступен.

Провайдер модели — любой OpenAI-compatible API. Скрипт подробно объяснит каждое поле и спросит четыре вещи (**ключ в argv не попадает**):

| Вопрос | Зачем | Плейсхолдер формата |
| --- | --- | --- |
| `base_url` | эндпоинт `/v1` | `https://api.openai.com/v1` |
| `model` | id модели у вашего провайдера | `gpt-4o` |
| имя env ключа | `provider set --api-key-env` | `OPENAI_API_KEY` |
| значение ключа | только в `.env` / окружение | вводится скрыто, либо уже задано в env |

Нужен доступ в сеть (GitHub: `kbshff`, `bsl-indexer`, JAR BSL LS, при необходимости clone `1c-sntx-sem`).

Опционально — каталог `bin` лицензионной платформы 1С. Install ищет установленные `8.3.*\bin` и предлагает выбрать / ввести путь / пропустить ingest. Без ingest семантический поиск справки на live-прогоне не работает; HBK в репозиторий не кладётся. Пропустить целиком: `-SkipIngest` / `--skip-ingest`.

Windows: не меняйте ExecutionPolicy машины. Запускайте `.\scripts\install.cmd` (внутри `Bypass` только для этого файла). То же вручную: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1`.

### Что делает скрипт

1. Проверяет хост-инструменты.
2. Спрашивает провайдера (с пояснениями) и пишет `.env` (ключ и абсолютные пути к MCP; Windows-пути в кавычках для dotenvy).
3. Ставит или находит `kbshff` (release → `tools/`), `bsl-indexer`, JAR `bsl-language-server`, Node-мост `tools/bsl-ls-mcp`, Python-venv `1c-sntx-sem`. Долгие загрузки — с progress bar (`curl`).
4. Для **всех четырёх** профилей (`1c-analyst`, `1c-yaxunit`, `1c-coder`, `1c-implementer`), счётчик `[n/4]`: `kbshff init`, `config import` (`master_prompt.md` + `skills.dsl` + `rules.md`), `provider set`, `skill list`, `check`. Профили — в `.kuibysheff/` корня репозитория.
5. Гоняет `oscript … harness/run.os --dry-run` (офлайн: банк, фикстура CF, без LLM).

Скрипт **не** стартует daemon `bsl-indexer` и **не** поднимает SearXNG / `ibcmd`. Для live-eval демон должен быть запущен в том же `CODE_INDEX_HOME`, что в `.env` (каталог `bsl-indexer`): `bsl-indexer daemon run`. Если в окружении уже задан чужой `CODE_INDEX_HOME`, harness его не перебьёт из `.env`.

### Запуск

```powershell
.\scripts\install.cmd
# флаги: -SkipIngest -NonInteractive -ToolsDir D:\tools -PlatformPath "C:\Program Files\1cv8\8.3.xx\bin"
.\harness\run.cmd -DryRun
.\harness\run.cmd
```

```bash
chmod +x scripts/install.sh
./scripts/install.sh
# --skip-ingest --non-interactive --tools-dir /opt/kbshff-tools --platform-path /opt/1cv8/bin
oscript -encoding=utf-8 harness/run.os --dry-run
# канон оркестратора без обёртки; install.sh уже гоняет это в конце
./harness/run.sh
```

`run.cmd` / `run.sh` — live-eval gate `cfe-qty-check-01` (нужен ключ из `.env`). Весь банк: `-All` / `--all`. Канон без обёртки: `oscript -encoding=utf-8 harness/run.os`.

Без install: скопируйте `.env.example` → `.env`, задайте ключ и пути, затем:

```text
kbshff config --project-root <DIR> --agent 1c-analyst provider set \
  --base-url "$KBSHFF_PROVIDER_BASE_URL" \
  --model "$KBSHFF_PROVIDER_MODEL" \
  --api-key-env "$KBSHFF_PROVIDER_API_KEY_ENV"
```

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
