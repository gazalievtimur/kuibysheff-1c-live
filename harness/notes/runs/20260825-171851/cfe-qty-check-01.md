# cfe-qty-check-01 — 20260825-171851

- pass: `False`
- agent_stop (CLI loop end, not pass): see stages below
- platform (run-yaxunit.ps1): `skipped`
- error: `None`
- failures: ["analyst: agent_stop='limit_reached' (loop did not finish; goal_reached ≠ contract pass)", "yaxunit: agent_stop='limit_reached' (loop did not finish; goal_reached ≠ contract pass)", "coder: agent_stop='limit_reached' (loop did not finish; goal_reached ≠ contract pass)", "implementer: agent_stop='limit_reached' (loop did not finish; goal_reached ≠ contract pass)", "analyst missing out/prd.md", "analyst missing out/architecture.md", "analyst missing out/tasks.md", "analyst missing out/cfe-scope.md", "yaxunit missing out/test-report.md", "coder out/src is empty", "coder missing code-report.md", "coder src missing 'Количество'", "implementer missing out/cfe/Configuration.xml", "implementer CFE missing object 'Documents/РасходТовара'", "implementer CFE missing any of ['&Вместо', '&ИзменениеИКонтроль']", "implementer missing implement-report.md/checklist.md"]

## expect (bank)

```json
{
  "plan_files": [
    "agreements.md",
    "prd.md",
    "architecture.md",
    "tasks.md",
    "cfe-scope.md"
  ],
  "plan_contains": [
    "РасходТовара",
    "ПередЗаписью"
  ],
  "test_contains": [
    "РасходТовара",
    "Тест_КоличествоНоль_НеЗаписывается"
  ],
  "src_contains": [
    "Количество"
  ],
  "cfe_objects": [
    "Documents/РасходТовара"
  ],
  "cfe_contains_any": [
    "&Вместо",
    "&ИзменениеИКонтроль"
  ],
  "yaxunit": {
    "suite": "СкладТест_РасходТовара",
    "procedure": "Тест_КоличествоНоль_НеЗаписывается"
  }
}
```

## stages

### analyst

- agent_stop: `limit_reached` (goal_reached = done=true, not contract pass)
- usage: iterations=8, prompt_tokens=142550, completion_tokens=2139, total_tokens=144689, elapsed_ms=73026
- home: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-171851\cfe-qty-check-01\project\.kuibysheff\homes\cfe-qty-check-01\analyst`
- result: Execution stopped due to limit: max_tokens

out/:
- `agreements.md`

### yaxunit

- agent_stop: `limit_reached` (goal_reached = done=true, not contract pass)
- usage: iterations=10, prompt_tokens=129578, completion_tokens=6798, total_tokens=136376, elapsed_ms=179514
- home: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-171851\cfe-qty-check-01\project\.kuibysheff\homes\cfe-qty-check-01\yaxunit`
- result: Execution stopped due to limit: max_tokens

out/:
- `cfe-tests/CommonModules/СкладТест_РасходТовара/Ext/Module.bsl`
- `cfe-tests/CommonModules/СкладТест_РасходТовара.xml`
- `cfe-tests/Configuration.xml`
- `manifest.json`
- `tests/СкладТест_РасходТовара.bsl`

### coder

- agent_stop: `limit_reached` (goal_reached = done=true, not contract pass)
- usage: iterations=20, prompt_tokens=119975, completion_tokens=10297, total_tokens=130272, elapsed_ms=355749
- home: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-171851\cfe-qty-check-01\project\.kuibysheff\homes\cfe-qty-check-01\coder`
- result: Execution stopped due to limit: max_tokens

### implementer

- agent_stop: `limit_reached` (goal_reached = done=true, not contract pass)
- usage: iterations=20, prompt_tokens=115441, completion_tokens=8865, total_tokens=124306, elapsed_ms=151946
- home: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-171851\cfe-qty-check-01\project\.kuibysheff\homes\cfe-qty-check-01\implementer`
- result: Execution stopped due to limit: max_tokens

## where to look

- task dir: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-171851\cfe-qty-check-01`
- logs: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-171851\cfe-qty-check-01\logs`
- platform work: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-171851\cfe-qty-check-01\yaxunit`

