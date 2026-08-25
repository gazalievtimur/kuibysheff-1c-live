# cfe-qty-check-01 — 20260825-170542

- pass: `False`
- agent_stop (CLI loop end, not pass): see stages below
- platform (run-yaxunit.ps1): `skipped`
- error: `None`
- failures: ["analyst: agent_stop='limit_reached' (loop did not finish; goal_reached ≠ contract pass)", "yaxunit: agent_stop='limit_reached' (loop did not finish; goal_reached ≠ contract pass)", "analyst missing out/agreements.md", "analyst missing out/prd.md", "analyst missing out/architecture.md", "analyst missing out/tasks.md", "analyst missing out/cfe-scope.md", "analyst missing out/agreements.md", "analyst agreements.md missing 'РасходТовара'", "analyst agreements.md missing 'ПередЗаписью'", "analyst agreements.md missing 'Тест_КоличествоНоль_НеЗаписывается'", "analyst plan missing 'РасходТовара'", "analyst plan missing 'ПередЗаписью'", "yaxunit missing out/test-report.md", "yaxunit missing BSL under out/tests or out/cfe-tests", "yaxunit tests missing 'РасходТовара'", "yaxunit tests missing 'Тест_КоличествоНоль_НеЗаписывается'", "yaxunit tests missing procedure 'Тест_КоличествоНоль_НеЗаписывается'", "coder out/src is empty", "coder src missing 'Количество'", "implementer missing out/cfe/Configuration.xml", "implementer CFE missing object 'Documents/РасходТовара'", "implementer CFE missing any of ['&Вместо', '&ИзменениеИКонтроль']"]

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
- usage: iterations=11, prompt_tokens=129622, completion_tokens=3089, total_tokens=132711, elapsed_ms=182957
- home: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-170542\cfe-qty-check-01\project\.kuibysheff\homes\cfe-qty-check-01\analyst`
- result: Execution stopped due to limit: max_tokens

### yaxunit

- agent_stop: `limit_reached` (goal_reached = done=true, not contract pass)
- usage: iterations=13, prompt_tokens=126337, completion_tokens=4425, total_tokens=130762, elapsed_ms=186045
- home: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-170542\cfe-qty-check-01\project\.kuibysheff\homes\cfe-qty-check-01\yaxunit`
- result: Execution stopped due to limit: max_tokens

### coder

- agent_stop: `goal_reached` (goal_reached = done=true, not contract pass)
- usage: iterations=9, prompt_tokens=35060, completion_tokens=3881, total_tokens=38941, elapsed_ms=70228
- home: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-170542\cfe-qty-check-01\project\.kuibysheff\homes\cfe-qty-check-01\coder`
- result: BLOCKED: missing plan files (agreements.md, tasks.md, architecture.md, prd.md, cfe-scope.md). Deliverables: code-report.md, files-index.md, manifest.json written.

out/:
- `code-report.md`
- `files-index.md`
- `manifest.json`

### implementer

- agent_stop: `goal_reached` (goal_reached = done=true, not contract pass)
- usage: iterations=9, prompt_tokens=33784, completion_tokens=3105, total_tokens=36889, elapsed_ms=56654
- home: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-170542\cfe-qty-check-01\project\.kuibysheff\homes\cfe-qty-check-01\implementer`
- result: BLOCKED — missing in/agreements.md. Cannot package coder sources without analyst's frozen identifiers. out/implement-report.md, out/checklist.md, out/manifest.json written with blocked status.

out/:
- `checklist.md`
- `implement-report.md`
- `manifest.json`

## where to look

- task dir: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-170542\cfe-qty-check-01`
- logs: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-170542\cfe-qty-check-01\logs`
- platform work: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-170542\cfe-qty-check-01\yaxunit`

