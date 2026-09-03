# Как решить задачу на цепочке analyst → yaxunit → coder → implementer

Этот репозиторий — live-eval учебной конфигурации **Склад**. Оркестратор гоняет четыре профиля `kbshff` и склеивает артефакты. Продуктовый конвейер VS Code (`1c-dev`) живёт в [Agent-Kuibysheff](https://github.com/gazalievtimur/Agent-Kuibysheff); здесь тот же контракт CLI.

Параметры агента задаются **командами CLI**, не правкой `.kuibysheff/protected/`. Файлы `.env` и `profiles/*/agent-config.example.yaml` — секрет в окружении и шаблон для `config import`, не операторский редактор.

Справка: `kbshff help config`, `kbshff help config provider`, [CONTRACT.md](https://github.com/gazalievtimur/Agent-Kuibysheff/blob/main/CONTRACT.md).

## 1. Установка

Предустановка хост-инструментов (ссылки, что обязательно / что опционально): **[prerequisites.md](prerequisites.md)**.

В `PATH` для install: Git, Python 3, curl (`unzip` на Linux). **OneScript** install поставит через [OVM](https://github.com/oscript-library/ovm), если его ещё нет (`-OscriptVersion` / `--oscript-version`, по умолчанию `stable`). **Node.js**, **Java 17+** и **bin платформы 1С** рекомендуются для полного стека; если их нет — предупреждение и вопрос, продолжать ли ([prerequisites.md](prerequisites.md)). `kbshff` — из GitHub Releases в `tools/`; `cargo` — только fallback.

```powershell
.\scripts\install.cmd
# если ExecutionPolicy=Restricted: не меняйте политику машины, запускайте .cmd
# или: powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1
# флаги: -SkipIngest -NonInteractive -ToolsDir D:\tools -PlatformPath "C:\Program Files\1cv8\8.3.xx\bin" -OscriptVersion stable
```

```bash
chmod +x scripts/install.sh
./scripts/install.sh
# --skip-ingest --non-interactive --tools-dir /opt/kbshff-tools --platform-path /opt/1cv8/bin --oscript-version stable
```

Скрипт:

1. Спрашивает общий `base_url`, имя/значение ключа и **отдельную модель** для каждого из четырёх агентов (пояснения; ключ не в argv).
2. Ставит MCP-инструменты и при необходимости `kbshff` / OneScript (OVM) в `tools/` (progress bar на загрузках) или переиспользует уже заданные пути / соседние clone. Штатный BSL LS (Node + JAR) ставится только если доступны Node/npm (иначе пропуск).
3. Пишет `.env` (секреты и абсолютные пути).
4. Для **всех четырёх** профилей (`1c-analyst`, `1c-yaxunit`, `1c-coder`, `1c-implementer`), `[n/4]`: `init`, `config import` (`master_prompt.md` + **`skills.dsl`** + `rules.md`), `provider set` со своей моделью, проверка `skill list` и `check`. Профили пишутся в `.kuibysheff/` корня репозитория.
5. Гоняет `oscript … harness/run.os --dry-run`. После этого конвейер готов: `.\harness\run.cmd` / `./harness/run.sh`.

Ingest справки `1c-sntx-sem` опционален: install предложит найденные `8.3.*\bin` (или путь вручную / пропуск). Без индекса семантический поиск `sntx_sem` на live-прогоне не работает. HBK в репозиторий не кладётся.

## 2. Конфиг агента через CLI (предпочтительный путь)

Protected-профиль: `{project-root}/.kuibysheff/protected/agents/<id>/`. Пишет только процесс `kbshff`.

```text
kbshff init <id> --project-root <DIR> [--force]
kbshff config --project-root <DIR> --agent <ID> import --from <settings-dir> --force
kbshff config --project-root <DIR> --agent <ID> provider set \
  --base-url https://api.openai.com/v1 \
  --model gpt-4o \
  --api-key-env OPENAI_API_KEY
kbshff config --project-root <DIR> --agent <ID> limits set \
  --max-iterations 100 --max-tokens 800000 --max-duration-sec 2400
kbshff check --project-root <DIR> --agent <ID>
kbshff run --project-root <DIR> --agent <ID> --home homes/<task>/<stage> --prompt "…"
```

Ключ в команду не передаётся: только `--api-key-env`, значение — в окружении / `.env`.

Ручной мастер provider/limits: `kbshff init <id> --project-root <DIR> --interactive`.

Идентификаторы профилей этого gate: `1c-analyst`, `1c-yaxunit`, `1c-coder`, `1c-implementer`. Install импортирует скилы всех четырёх. Для ручного import копируйте в staging **`master_prompt.md`**, **`skills.dsl`**, **`rules.md`** из `profiles/<id>/` (так делает харнес; отсутствие любого файла — ошибка). Не импортируйте `agent-config.example.yaml` целиком: там заглушки `REQUIRED_*` для MCP.

Переменные `.env`, которые читает харнес:

| Переменная | Смысл |
| --- | --- |
| `KBSHFF_PROVIDER_BASE_URL` | общий `provider set --base-url` |
| `KBSHFF_PROVIDER_MODEL_1C_ANALYST` (и `_YAXUNIT` / `_CODER` / `_IMPLEMENTER`) | `--model` для соответствующего агента |
| `KBSHFF_PROVIDER_MODEL` | запасной `--model`, если per-agent не задан |
| `KBSHFF_PROVIDER_API_KEY_ENV` | `--api-key-env` |
| значение этой env | секрет |
| `SNTX_SEM_CONFIG`, `SNTX_SEM_PYTHON` | MCP справки |
| `BSL_INDEXER` | `bsl-indexer` |
| `BSL_LS_MCP`, `BSL_LS_JAR`, `JAVA_HOME` | мост + JAR анализа BSL |
| `KBSHFF_BIN` | явный путь к CLI |

На live-прогоне харнес собирает MCP-пути под копию CF (они меняются каждый run), затем снова вызывает `config provider set` из `.env` (своя модель на агента), чтобы YAML-шаблон не затёр операторский провайдер.

Полезные команды: `provider get`, `limits get`, `mcp list`, `tools effective`, `config show`.

## 3. Цепочка и поток артефактов

```text
task_brief  →  1c-analyst   →  out/{agreements.md,prd,tasks,cfe-scope,architecture,…}
                   ↓
              1c-yaxunit    →  out/tests + out/cfe-tests   (TDD, падают на baseline)
                   ↓
              1c-coder      →  out/src                     (код фичи под тесты)
                   ↓
              1c-implementer→  out/cfe + копия out/cfe-tests
```

CF для всех стадий — одна копия `harness/runs/<id>/<task>/cf/`. Агентам **нельзя** её менять: скоринг падает, если дерево изменилось (игнор `.code-index/`). Писать только в `out/` и `notes/` своего `--home`.

Eval-обёртка четырёх стадий:

```powershell
.\harness\run.ps1                          # gate cfe-qty-check-01
.\harness\run.ps1 -TaskId cfe-http-filter-01
.\harness\run.ps1 -All
```

```bash
./harness/run.sh
./harness/run.sh --task-id cfe-http-filter-01
./harness/run.sh --all
```

Одна стадия вручную — `kbshff run` с подготовленным `in/` (так делает [`Конвейер.os`](../harness/oscript/Модули/Конвейер.os)).

## 4. Договорённости (литералы)

Читать до тестов и кода: [`profiles/1c-shared/agreements-protocol.md`](../profiles/1c-shared/agreements-protocol.md).

Имена процедур, объектов, обработчиков — **посимвольно**. Синоним (`Тест_НулевоеКоличество_Отказ` вместо `Тест_КоличествоНоль_НеЗаписывается`) — срыв стадии. Смысл («запись должна быть отказана») реализуется; строку-идентификатор не подменяют.

Analyst первым файлом пишет `out/agreements.md`. Downstream без `in/agreements.md` → `blocked`, не догадка.

## 5. Стадии

MCP общие правила:

- `code-index.*` — всегда `"repo": "cf"`.
- Перед утверждениями про BSL/директивы: `sntx_sem.search_bsl_syntax` или `search_help`, затем `get_topic`.
- После записи BSL на yaxunit/coder/implementer: `bsl-language-server.analyze` с абсолютным `srcDir` из `in/bsl-lint.json`.

### 1c-analyst

Цель: утверждаемый план CFE. Входы: `task_brief.md`, `agreements.json`, протокол, `product.json`. Выходы: `agreements.md` (сначала), `prd.md`, `architecture.md`, `tasks.md` (`bsl` / `metadata` / `cfe_packaging`), `cfe-scope.md`, `manifest.json` (`apply_mode: none`). Не писать прикладной код и не править CF.

### 1c-yaxunit

Цель: тесты YAxUnit, которые **падают** на baseline. Входы: план analyst, `APPROVED`, снимок `in/docs/`, литерал процедуры из `expect.yaxunit.procedure`. Не реализовывать фичу. Проверять эффект `Записать`, не фиктивную локальную `Отказ`.

### 1c-coder

Цель: исходники `out/src/` под тесты. Шаги `cfe_packaging` пропустить (запишет implementer). Не переименовывать тесты и объекты из договорённостей.

### 1c-implementer

Цель: дерево `out/cfe/` по `cfe-scope.md`; `in/cfe-tests/` → `out/cfe-tests/` **без правок**. `manifest.json` с `apply_mode: copy_out`. Не выдумывать бизнес-логику.

`done=true` на каждой стадии — только после таблицы сверки (идентификатор → файл). Это не pass задачи.

## 6. Своя задача в банке

Скопируйте [`harness/bank/cfe-qty-check-01.json`](../harness/bank/cfe-qty-check-01.json):

- `id`, `title`, `brief` (литералы в backticks)
- `stages`: `["analyst","yaxunit","coder","implementer"]`
- `expect`: `plan_files`, `plan_contains`, `test_contains`, `src_contains`, `cfe_objects`, `cfe_contains_any`, `yaxunit.procedure` / `suite`

Имя gate-процедуры в `brief`, `expect.yaxunit.procedure` и будущем `agreements.md` должно совпадать посимвольно.

Запуск: `.\harness\run.ps1 -TaskId <id>`.

## 7. Скоринг и где смотреть результат

`stop_reason=goal_reached` значит: модель вернула `done=true`. Это **конец петли**, не приёмка. Разбор: [`harness/notes/goal_reached.md`](../harness/notes/goal_reached.md).

Харнес без платформы 1С проверяет: цикл завершён, CF не изменилась, файлы/needles стадий, `apply_mode`. Опционально `-RequirePlatform` / `--require-platform`.

Артефакты: `harness/runs/<run_id>/report.json`, `NOTES.md`, `logs/<stage>/`, homes в `project/.kuibysheff/homes/<task>/<stage>/{in,out}`. Кратко: `harness/notes/runs/<run_id>/`.

## 8. Типовые сбои

| Симптом | Что проверить |
| --- | --- |
| `missing provider API key env` | `.env` и имя из `KBSHFF_PROVIDER_API_KEY_ENV`; ключ не в YAML |
| `kbshff check` не проходит | `kbshff config … provider get`; `base_url` доступен; `help config` |
| `SNTX_SEM_CONFIG is required` | install / ingest; файл `config.yaml` существует |
| нет `analyze` / BSL LS | опционально: Node + `BSL_LS_MCP` + `BSL_LS_JAR` + Java ([prerequisites.md](prerequisites.md)); или свой MCP |
| CF fingerprint changed | агент писал в копию CF; чинить профиль, не «коммитить фикстуру» |
| FAIL при `goal_reached` | синоним имени теста / нет `agreements.md` |
| `limit_reached` | `kbshff config … limits set` или лимиты в шаблоне стадии |

SearXNG и прогон на `ibcmd` в install не входят. Live с платформой: `.\harness\run.ps1 -RequirePlatform`.
