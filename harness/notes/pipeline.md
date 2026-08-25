# Как идёт работа (1c-live, Склад)

Конвейер живого eval — не оркестратор продукта. `kbshff` на каждой стадии
один раз: `run --agent <id> --home homes/<task>/<stage> --prompt …`.
Склейку артефактов делает `eval.py`.

```text
task_brief  →  1c-analyst   →  out/{prd,tasks,cfe-scope,architecture,…}
                   ↓
              1c-yaxunit    →  out/tests + out/cfe-tests   (TDD, падают на baseline)
                   ↓
              1c-coder      →  out/src                     (код фичи под тесты)
                   ↓
              1c-implementer→  out/cfe + копия out/cfe-tests
```

Профили импортируются из `test-agents/1c-*` (без example YAML: в eval пишется
живой `agent-config.yaml` с CF-копией, sntx_sem, bsl-indexer).

## Что видит каждая стадия (`in/`)

| Стадия | Кладёт eval |
| --- | --- |
| analyst | `task_brief.md`, `product.json`, `agreements.json`, `expect.json`, `agreements-protocol.md` |
| yaxunit | план analyst + `APPROVED` + `docs/` + protocol + `agreements.json` + `agreements.md` + brief |
| coder | план + `APPROVED` + `tests/` + protocol + agreements |
| implementer | план/`agreements.md` + `coder/` + `cfe-tests/` + protocol + agreements |

CF для всех стадий одна и та же копия `runs/<id>/<task>/cf/` (workspace MCP).
Писать в CF агентам нельзя; скоринг падает, если дерево изменилось
(игнор `.code-index/`).

## Gate-имена тестов

Источник истины — литералы в `in/agreements.json` / `out/agreements.md`.
Протокол: [`test-agents/1c-shared/agreements-protocol.md`](../../../test-agents/1c-shared/agreements-protocol.md)
(копия на стадии: `in/agreements-protocol.md`). Разбор четырёх сбоев:
[agreements.md](agreements.md).

## Скоринг (без платформы 1С)

1. Цикл стадии завершился (`agent_stop=goal_reached` = `done=true`). Это **не** pass.
   `error` / `limit_reached` — стадия не дописана. См. [goal_reached.md](goal_reached.md).
2. CF fingerprint не изменился
3. analyst: `agreements.md` + `plan_files` + `plan_contains`, `apply_mode=none`
4. yaxunit: `test-report.md`, BSL с `ЮТТесты`/`ЮТест`, `test_contains` / procedure, `apply_mode=none`
5. coder: непустой `out/src`, needles, `code-report.md`, `apply_mode=none`
6. implementer: `out/cfe` + объекты/needles, `apply_mode=copy_out`

## Платформенный шаг

`run-yaxunit.ps1` копирует CF + сгенерированные тесты (`out/cfe-tests`) + CFE фичи
и ищет `ibcmd`. Сейчас это **подготовка деревьев + чеклист**, а не прогон юнитов
в ИБ. Статус `passed` в отчёте = ibcmd найден и каталоги собраны.

Порядок `-YaxUnitDir`: `implementer/out/cfe-tests` → `yaxunit/out/cfe-tests` →
фикстура `cfe/YAxUnit_Tests_Sklad`.

## Документация YAxUnit

Снимок: `docs/yaxunit/` → `homes/…/yaxunit/in/docs/`.
Канон: https://bia-technologies.github.io/yaxunit/ (BIA Technologies, OSS).
SearXNG (`-WithSearxng`) только на эти публичные URL; ITS запрещён.

## Где лежат артефакты прогона

```text
runs/<run_id>/
  NOTES.md
  report.json
  <task>/
    NOTES.md
    cf/                         копия фикстуры
    logs/<stage>/               ai_usage, mcp_usage, chat_history, trace
    logs/<stage>.run.json       stdout kbshff
    project/.kuibysheff/homes/<task>/<stage>/{in,out,notes}
    yaxunit/                    платформенный work dir
```

Дубли кратких NOTES: `notes/runs/<run_id>/`.
Человеческий разбор: `notes/runs/<run_id>/analysis.md`.
