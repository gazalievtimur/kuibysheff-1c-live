# cfe-qty-check-01 — 20260825-170404

- pass: `False`
- agent_stop (CLI loop end, not pass): see stages below
- platform (run-yaxunit.ps1): `skipped`
- error: `None`
- failures: ["yaxunit: agent_stop='limit_reached' (loop did not finish; goal_reached ≠ contract pass)", "coder: agent_stop='limit_reached' (loop did not finish; goal_reached ≠ contract pass)", "implementer: agent_stop='limit_reached' (loop did not finish; goal_reached ≠ contract pass)", "yaxunit missing out/test-report.md", "yaxunit missing BSL under out/tests or out/cfe-tests", "yaxunit tests missing 'РасходТовара'", "yaxunit tests missing 'Тест_КоличествоНоль_НеЗаписывается'", "yaxunit tests missing procedure 'Тест_КоличествоНоль_НеЗаписывается'", "coder out/src is empty", "coder missing code-report.md", "coder src missing 'Количество'", "implementer missing out/cfe/Configuration.xml", "implementer CFE missing object 'Documents/РасходТовара'", "implementer CFE missing any of ['&Вместо', '&ИзменениеИКонтроль']", "implementer missing implement-report.md/checklist.md"]

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

- agent_stop: `goal_reached` (goal_reached = done=true, not contract pass)
- usage: iterations=13, prompt_tokens=96783, completion_tokens=6344, total_tokens=103127, elapsed_ms=235583
- home: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-170404\cfe-qty-check-01\project\.kuibysheff\homes\cfe-qty-check-01\analyst`
- result: Plan complete. All artifacts under out/. Gate: approve_plan.

out/:
- `adr.md`
- `agreements.md`
- `architecture.md`
- `cfe-scope.md`
- `codebase-findings.md`
- `manifest.json`
- `phase0-complexity.md`
- `prd.md`
- `requirements.md`
- `tasks.md`
- `workflow-state.md`

### yaxunit

- agent_stop: `limit_reached` (goal_reached = done=true, not contract pass)
- usage: iterations=12, prompt_tokens=134052, completion_tokens=3141, total_tokens=137193, elapsed_ms=77967
- home: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-170404\cfe-qty-check-01\project\.kuibysheff\homes\cfe-qty-check-01\yaxunit`
- result: Execution stopped due to limit: max_tokens

### coder

- agent_stop: `limit_reached` (goal_reached = done=true, not contract pass)
- usage: iterations=16, prompt_tokens=121714, completion_tokens=5929, total_tokens=127643, elapsed_ms=109032
- home: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-170404\cfe-qty-check-01\project\.kuibysheff\homes\cfe-qty-check-01\coder`
- result: Execution stopped due to limit: max_tokens

### implementer

- agent_stop: `limit_reached` (goal_reached = done=true, not contract pass)
- usage: iterations=19, prompt_tokens=114262, completion_tokens=5942, total_tokens=120204, elapsed_ms=109268
- home: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-170404\cfe-qty-check-01\project\.kuibysheff\homes\cfe-qty-check-01\implementer`
- result: Execution stopped due to limit: max_tokens

## where to look

- task dir: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-170404\cfe-qty-check-01`
- logs: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-170404\cfe-qty-check-01\logs`
- platform work: `C:\Git\kuibysheff-1c-live\harness\runs\20260825-170404\cfe-qty-check-01\yaxunit`

