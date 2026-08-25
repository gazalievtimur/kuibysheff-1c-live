# 1c-live — Склад (outside the agent product)

Live eval copy-unit for honing `kbshff` + `test-agents/1c-*` on a **toy warehouse CF**.
This directory is gitignored with the rest of `/workflows/` and is intended as a
future sibling project in the same repository — **not** part of the agent product tree.

Do **not** add `-1c` to the agent `check.ps1` gate. Run this workflow from here.

Pipeline: **analyst → yaxunit → coder → implementer**. YAxUnit writes TDD tests
(fail on baseline CF) from the approved plan plus a public docs snapshot; coder
implements against those tests; implementer packages the feature CFE and copies
the generated test CFE.

## Layout

```text
workflows/1c-live/
  cf/                         Designer dump «Склад» (+ planted defects)
  cfe/YAxUnit_Tests_Sklad/    Fallback stub tests (if the agent produced none)
  docs/yaxunit/               Public YAxUnit snapshot (copied to in/docs/)
  bank/*.json                 Live tasks (default gate: cfe-qty-check-01)
  products/sklad.yaml
  eval.py                     four-stage harness
  score.py / assert_regression.py
  run-yaxunit.ps1             Optional ibcmd / platform step
  run.ps1 / run.sh            Entry points
  test_smoke_offline.py       Offline dry-run
  notes/                      Разбор прогонов и описание, как идёт работа
  runs/                       Per-run homes + report.json + NOTES.md
```

## Requirements

| Need | Notes |
| --- | --- |
| Release `kbshff` | `cargo build --release` (done by `run.ps1` unless `-SkipBuild`) |
| Provider API key | From `agent-config.local.yaml` or `test-agents/1c-analyst/agent-config.example.yaml` |
| `SNTX_SEM_CONFIG` | Path to `1c-sntx-sem` `config.yaml` |
| `SNTX_SEM_PYTHON` | Optional; defaults to `1c-sntx-sem/.venv/.../python` |
| `BSL_INDEXER` / `CODE_INDEX_BIN` | Path to `bsl-indexer` |
| `CODE_INDEX_HOME` | Optional; defaults to the directory of `bsl-indexer` (holds `daemon.toml`) |
| `BSL_LS_MCP` / `BSL_LS_SERVER` | Path to `bsl-ls-mcp/server.js` (ЗУП-style Node MCP) |
| `BSL_LS_JAR` | Path to `bsl-language-server-*-exec.jar` |
| `JAVA_HOME` | Java 17+ for BSL-LS (optional if `java` is on PATH) |
| Optional platform | `IBCMD_PATH` or install under `Program Files\1cv8` for `-RequirePlatform` |

`run.ps1` / `run.sh` set `KUIBYSHEFF_ALLOW_UNSANDBOXED_MCP=1` by default so stdio MCP
(`sntx_sem`, `code-index`, `bsl-language-server`) can start under the worker’s cleared child environment.

**code-index:** MCP `serve` is a transport over the running `bsl-indexer` daemon.
Eval registers `harness/cf` in `daemon.toml` (alias `cf`) and reloads the daemon.
Every `code-index.*` tool call must pass `"repo":"cf"` (kbshff also auto-fills
`repo` when the server has a single `--path` alias).

**bsl-language-server:** Wired on yaxunit / coder / implementer (tests are BSL too).
After writing sources, agents must call `analyze` with absolute `srcDir` from
`in/bsl-lint.json` (same Node+JAR layout as the ЗУП Cursor MCP).

Profiles are imported from the sibling agent project:

- `test-agents/1c-analyst`
- `test-agents/1c-yaxunit`
- `test-agents/1c-coder`
- `test-agents/1c-implementer`

## YAxUnit docs

The yaxunit stage must not invent API. Eval copies `docs/yaxunit/` →
`homes/.../yaxunit/in/docs/` before `kbshff run`.

Canonical public sources (OSS BIA Technologies, not ITS):

- https://bia-technologies.github.io/yaxunit/
- https://github.com/bia-technologies/yaxunit
- first test: https://bia-technologies.github.io/yaxunit/docs/getting-started/first-test/

Optional `-WithSearxng` on analyst **and** yaxunit: only those public hosts.
The snapshot is the source of truth; SearXNG is a supplement.

## Commands

Offline (no LLM):

```powershell
.\workflows\1c-live\run.ps1 -DryRun
# or:
python .\workflows\1c-live\test_smoke_offline.py
```

```bash
./workflows/1c-live/run.sh --dry-run
```

Live gate (default task `cfe-qty-check-01`):

```powershell
$env:SNTX_SEM_CONFIG = "C:\Git\1c-sntx-sem\config.yaml"
$env:BSL_INDEXER = "C:\mcp\code-index\bsl-indexer.exe"
$env:BSL_LS_MCP = "$env:USERPROFILE\.claude\bsl-ls-mcp\server.js"
$env:BSL_LS_JAR = "$env:USERPROFILE\.claude\bsl-ls\bsl-language-server.jar"
# JAVA_HOME already set on this machine for JDK 17+
$env:OPENAI_API_KEY = "..."   # or provider api_key_env from config
.\workflows\1c-live\run.ps1
```

```powershell
.\workflows\1c-live\run.ps1 -TaskId cfe-negative-stock-01,cfe-http-filter-01
.\workflows\1c-live\run.ps1 -All
.\workflows\1c-live\run.ps1 -RequirePlatform
```

```bash
export SNTX_SEM_CONFIG=/path/to/1c-sntx-sem/config.yaml
export BSL_INDEXER=/path/to/bsl-indexer
export BSL_LS_MCP=$HOME/.claude/bsl-ls-mcp/server.js
export BSL_LS_JAR=$HOME/.claude/bsl-ls/bsl-language-server.jar
export JAVA_HOME=/path/to/jdk-17+
./workflows/1c-live/run.sh
./workflows/1c-live/run.sh --all
./workflows/1c-live/run.sh --require-platform
```

## Scoring

Always (no 1C platform):

1. Loop finished (`agent_stop=goal_reached` = model `done=true`; **not** task pass). `error` / `limit_reached` fail the stage as incomplete.
2. CF dump fingerprint unchanged (ignores `.code-index/` caches written by `bsl-indexer`)
3. Analyst `out/agreements.md` (literals from expect) + plan files + `plan_contains`
4. YAxUnit `out/test-report.md` + BSL (`ЮТТесты` / `ЮТест`) + `test_contains` / procedure name + `apply_mode=none`
5. Coder `out/src` + needles + `code-report.md`
6. Implementer `out/cfe` + object/needle checks + `apply_mode=copy_out`

Optional (`-RequirePlatform`): discover `ibcmd`, stage CF + **generated** test CFE
(`implementer/out/cfe-tests`, else `yaxunit/out/cfe-tests`, else fixture
`cfe/YAxUnit_Tests_Sklad`) + agent feature CFE under `runs/.../yaxunit/`.
Missing platform fails only when the flag is set.

## Notes (разбор работы)

После live-прогона смотреть `notes/` — карта конвейера и разборы run'ов.
Протокол договорённостей: `notes/agreements.md` и
`test-agents/1c-shared/agreements-protocol.md`.
Смысл `goal_reached`: `notes/goal_reached.md`.
`eval.py` пишет `runs/<id>/NOTES.md` и копию в `notes/runs/<id>/`.
Человеческий разбор первого четырёхстадийного прогона:
`notes/runs/20260817-183746/analysis.md`.

## Fixture domain

Original **Склад** config (not Union K7): catalogs, documents `ПриходТовара` / `РасходТовара`, register `ОстаткиТоваров`, HTTP `ОбменСкладом`, planted defects for the three bank tasks.

Regenerate metadata XML (keeps BSL modules):

```powershell
python .\workflows\1c-live\_gen_fixture.py
```

## Bank tasks

| id | Focus |
| --- | --- |
| `cfe-qty-check-01` | `ПередЗаписью` qty check on `РасходТовара` (**gate**); procedure `Тест_КоличествоНоль_НеЗаписывается` |
| `cfe-negative-stock-01` | Block posting below zero on `ОстаткиТоваров` |
| `cfe-http-filter-01` | Warehouse filter on `ОбменСкладом` GET `/остатки` |
