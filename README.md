# kuibysheff-1c-live

Four-stage live eval for [Agent Kuibysheff](https://github.com/gazalievtimur/Agent-Kuibysheff) (`kbshff`) on a toy 1C warehouse CF:

`analyst → yaxunit → coder → implementer`

Independent example repo — use it to learn CLI orchestration with 1C MCP tooling, or as an opt-in honing gate when developing the agent.

## Requirements

- `kbshff` on `PATH`, or `KBSHFF_BIN`, or `KUIBYSHEFF_SRC` / sibling checkout
- Python 3
- Provider API key (`OPENAI_API_KEY` by default)
- `SNTX_SEM_CONFIG` — path to [`1c-sntx-sem`](https://github.com/gybson63/1c-sntx-sem) `config.yaml`
- `BSL_INDEXER` or `CODE_INDEX_BIN` — path to `bsl-indexer` from [`code-index-mcp`](https://github.com/Regsorm/code-index-mcp)
- `BSL_LS_MCP` + `BSL_LS_JAR` (+ `JAVA_HOME`) — [BSL Language Server](https://github.com/1c-syntax/bsl-language-server) MCP as in ЗУП (required for yaxunit/coder/implementer)
- Optional: `SNTX_SEM_PYTHON`, 1C platform/`ibcmd` (`-RequirePlatform`)

`KUIBYSHEFF_ALLOW_UNSANDBOXED_MCP=1` is set by the launcher (stdio MCP + venv).

## Quick start

```powershell
Copy-Item .\.env.example .\.env
# set OPENAI_API_KEY, SNTX_SEM_CONFIG, BSL_INDEXER, BSL_LS_MCP, BSL_LS_JAR

.\harness\run.ps1 -DryRun
.\scripts\1c-live-regression.ps1
```

```bash
cp .env.example .env
./harness/run.sh --dry-run
./scripts/1c-live-regression.sh
```

## Layout

```text
profiles/1c-analyst|yaxunit|coder|implementer|1c-shared
harness/          eval, bank, CF fixture, YAxUnit docs
scripts/          resolve-kbshff + thin regression wrapper
docs/searxng/     optional SearXNG notes
```

Gate task: `cfe-qty-check-01` (default). Use `-All` / `--all` for the full bank.

## Agent contract

CLI `init` / `config import` / `run` per stage — see [CONTRACT.md](https://github.com/gazalievtimur/Agent-Kuibysheff/blob/main/CONTRACT.md).

Product conveyor / VS Code (`1c-dev`) stays in the agent repo; this repo is the live CF/CFE eval only.

## Related

Example orchestrators:

- [kuibysheff-aoc](https://github.com/gazalievtimur/kuibysheff-aoc)
- [kuibysheff-swebench](https://github.com/gazalievtimur/kuibysheff-swebench)

MCP tooling used by this gate:

- [1c-sntx-sem](https://github.com/gybson63/1c-sntx-sem) — platform help (`sntx_sem`)
- [code-index-mcp](https://github.com/Regsorm/code-index-mcp) — `bsl-indexer` / `code-index` over CF
- [bsl-language-server](https://github.com/1c-syntax/bsl-language-server) — BSL `analyze` (JAR; ЗУП-style Node bridge)
- [1c-conf-doc](https://github.com/gybson63/1c-conf-doc) — optional configuration-doc MCP
