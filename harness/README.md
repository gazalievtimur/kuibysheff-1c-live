# 1c-live — Склад

Live-eval для оттачивания `kbshff` + профилей `profiles/1c-*` на **учебной CF склада**.
Этот каталог — оркестратор standalone-репозитория `kuibysheff-1c-live`, не часть продуктового дерева агента.

Не включайте этот gate в `check.ps1` агента с флагом вроде `-1c`. Запускайте отсюда.

Конвейер: **analyst → yaxunit → coder → implementer**. YAxUnit пишет TDD-тесты
(падают на baseline CF) по утверждённому плану и снимку публичной документации;
coder реализует против этих тестов; implementer упаковывает feature-CFE и копирует
сгенерированное тестовое CFE.

## Структура

```text
harness/
  cf/                         выгрузка «Склад» (+ заложенные дефекты)
  cfe/YAxUnit_Tests_Sklad/    запасные stub-тесты (если агент ничего не дал)
  docs/yaxunit/               снимок публичных docs YAxUnit → in/docs/
  bank/*.json                 live-задачи (gate по умолчанию: cfe-qty-check-01)
  products/sklad.yaml
  oscript/Модули/             eval, score, fixture, platform (OneScript)
  run.os / eval.os            четырёхстадийный harness
  assert-regression.os        проверка report.json
  run-yaxunit.os              опциональный шаг ibcmd / платформы
  gen-fixture.os              XML фикстуры (BSL не перезаписывается)
  test-smoke-offline.os       офлайн dry-run
  run.ps1 / run.sh            тонкие обёртки oscript
  notes/                      разбор прогонов и описание работы
  runs/                       homes прогонов + report.json + NOTES.md
```

Профили импортируются из `../profiles/1c-*`.

## Требования

| Нужно | Заметки |
| --- | --- |
| OneScript 2.0 | `oscript` в PATH; канон: `oscript -encoding=utf-8 harness/run.os` |
| Release `kbshff` | `cargo build --release` (делает `run.os` / `run.ps1`, если нет `--skip-build`) |
| API-ключ провайдера | Из `agent-config.local.yaml` или `profiles/1c-analyst/agent-config.example.yaml` |
| `SNTX_SEM_CONFIG` | Путь к `config.yaml` [`1c-sntx-sem`](https://github.com/gybson63/1c-sntx-sem) |
| `SNTX_SEM_PYTHON` / `sntx-sem` | Runtime **MCP** `sntx_sem` (не harness). Либо явный интерпретатор, либо `1c-sntx-sem/.venv/.../python`, либо `sntx-sem` в PATH |
| `BSL_INDEXER` / `CODE_INDEX_BIN` | Путь к `bsl-indexer` из [`code-index-mcp`](https://github.com/Regsorm/code-index-mcp) (Releases или `cargo build -p bsl-indexer`) |
| `CODE_INDEX_HOME` | Опционально; по умолчанию каталог `bsl-indexer` (там `daemon.toml`) |
| `BSL_LS_MCP` / `BSL_LS_SERVER` | Путь к `bsl-ls-mcp/server.js` (Node MCP поверх JAR, стиль ЗУП) |
| `BSL_LS_JAR` | Путь к `bsl-language-server-*-exec.jar` из [`bsl-language-server`](https://github.com/1c-syntax/bsl-language-server) |
| `JAVA_HOME` | Java 17+ для BSL-LS (необязательно, если `java` в PATH) |
| Опционально платформа | `IBCMD_PATH` или установка в `Program Files\1cv8` для `--require-platform` |

`run.ps1` / `run.sh` по умолчанию ставят `KUIBYSHEFF_ALLOW_UNSANDBOXED_MCP=1`, чтобы stdio MCP
(`sntx_sem`, `code-index`, `bsl-language-server`) стартовали в очищенном окружении worker'а.

**code-index:** MCP `serve` — транспорт поверх daemon `bsl-indexer`
([Regsorm/code-index-mcp](https://github.com/Regsorm/code-index-mcp)).
Eval регистрирует `harness/cf` в `daemon.toml` (alias `cf`) и перезагружает daemon.
Каждый вызов `code-index.*` должен передавать `"repo":"cf"` (kbshff также подставляет
`repo`, если у сервера один `--path`-alias).

**bsl-language-server:** подключён на yaxunit / coder / implementer (тесты тоже BSL).
После записи исходников агенты должны вызвать `analyze` с абсолютным `srcDir` из
`in/bsl-lint.json` (JAR из [1c-syntax/bsl-language-server](https://github.com/1c-syntax/bsl-language-server); тот же layout Node+JAR, что в Cursor MCP ЗУП).

## Документация YAxUnit

Стадия yaxunit не должна выдумывать API. Eval копирует `docs/yaxunit/` →
`homes/.../yaxunit/in/docs/` перед `kbshff run`.

Канонические публичные источники (OSS BIA Technologies, не ИТС):

- https://bia-technologies.github.io/yaxunit/
- https://github.com/bia-technologies/yaxunit
- первый тест: https://bia-technologies.github.io/yaxunit/docs/getting-started/first-test/

Опциональный `-WithSearxng` на analyst **и** yaxunit: только эти публичные хосты.
Снимок — источник истины; SearXNG — дополнение.

## Команды

Офлайн (без LLM):

```powershell
oscript -encoding=utf-8 .\harness\run.os --dry-run
# или:
.\harness\run.ps1 -DryRun
oscript -encoding=utf-8 .\harness\test-smoke-offline.os
```

```bash
oscript -encoding=utf-8 harness/run.os --dry-run
./harness/run.sh --dry-run
```

Live gate (задача по умолчанию `cfe-qty-check-01`):

```powershell
$env:SNTX_SEM_CONFIG = "C:\Git\1c-sntx-sem\config.yaml"
$env:BSL_INDEXER = "C:\mcp\code-index\bsl-indexer.exe"
$env:BSL_LS_MCP = "$env:USERPROFILE\.claude\bsl-ls-mcp\server.js"
$env:BSL_LS_JAR = "$env:USERPROFILE\.claude\bsl-ls\bsl-language-server.jar"
# JAVA_HOME уже задан на машине для JDK 17+
$env:OPENAI_API_KEY = "..."   # или api_key_env провайдера из конфига
.\harness\run.ps1
```

```powershell
.\harness\run.ps1 -TaskId cfe-negative-stock-01,cfe-http-filter-01
.\harness\run.ps1 -All
.\harness\run.ps1 -RequirePlatform
```

```bash
export SNTX_SEM_CONFIG=/path/to/1c-sntx-sem/config.yaml
export BSL_INDEXER=/path/to/bsl-indexer
export BSL_LS_MCP=$HOME/.claude/bsl-ls-mcp/server.js
export BSL_LS_JAR=$HOME/.claude/bsl-ls/bsl-language-server.jar
export JAVA_HOME=/path/to/jdk-17+
./harness/run.sh
./harness/run.sh --all
./harness/run.sh --require-platform
```

## Скоринг

Всегда (без платформы 1С):

1. Цикл завершён (`agent_stop=goal_reached` = модель `done=true`; **не** «задача сдана»). `error` / `limit_reached` валят стадию как незавершённую.
2. Fingerprint выгрузки CF не изменился (игнор кэшей `.code-index/` от `bsl-indexer`)
3. Analyst: `out/agreements.md` (литералы из expect) + файлы плана + `plan_contains`
4. YAxUnit: `out/test-report.md` + BSL (`ЮТТесты` / `ЮТест`) + `test_contains` / имя процедуры + `apply_mode=none`
5. Coder: `out/src` + needles + `code-report.md`
6. Implementer: `out/cfe` + проверки объектов/needles + `apply_mode=copy_out`

Опционально (`-RequirePlatform`): найти `ibcmd`, поднять CF + **сгенерированное** тестовое CFE
(`implementer/out/cfe-tests`, иначе `yaxunit/out/cfe-tests`, иначе фикстура
`cfe/YAxUnit_Tests_Sklad`) + feature-CFE агента под `runs/.../yaxunit/`.
Отсутствие платформы валит прогон только при установленном флаге.

## Notes (разбор работы)

После live-прогона смотрите `notes/` — карта конвейера и разборы run'ов.
Протокол договорённостей: `notes/agreements.md` и
`profiles/1c-shared/agreements-protocol.md`.
Смысл `goal_reached`: `notes/goal_reached.md`.
`eval.os` пишет `runs/<id>/NOTES.md` и копию в `notes/runs/<id>/`.

## Предметная область фикстуры

Оригинальная конфигурация **Склад** (не Union K7): справочники, документы `ПриходТовара` / `РасходТовара`, регистр `ОстаткиТоваров`, HTTP `ОбменСкладом`, заложенные дефекты под три задачи банка.

Перегенерация metadata XML (BSL-модули сохраняются):

```powershell
oscript -encoding=utf-8 .\harness\gen-fixture.os
```

## Задачи банка

| id | Фокус |
| --- | --- |
| `cfe-qty-check-01` | проверка количества в `ПередЗаписью` у `РасходТовара` (**gate**); процедура `Тест_КоличествоНоль_НеЗаписывается` |
| `cfe-negative-stock-01` | запрет проведения ниже нуля по `ОстаткиТоваров` |
| `cfe-http-filter-01` | фильтр склада на `ОбменСкладом` GET `/остатки` |
