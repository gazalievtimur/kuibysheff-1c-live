# Notes — как читать 1c-live

Эта папка — сырьё для разбора прогонов и для последующего описания, **как
идёт работа** конвейера `analyst → yaxunit → coder → implementer`.

Харнес по-прежнему gitignored (`workflows/`). Сюда пишем только наблюдения,
карту артефактов и выводы. Код агентов живёт в `test-agents/1c-*`.

| Файл | Зачем |
| --- | --- |
| [pipeline.md](pipeline.md) | Как устроен конвейер: входы/выходы стадий, скоринг, платформа |
| [agreements.md](agreements.md) | Четыре сбоя коммуникации и чем закрыты |
| [goal_reached.md](goal_reached.md) | `goal_reached` = конец петли, не pass задачи |
| [runs/](runs/) | По каждому live-run: копия `NOTES.md` + разбор |
| `runs/<run_id>/NOTES.md` | Сводка прогона (пишет `eval.os`) |
| `runs/<run_id>/<task-id>.md` | Стадии, usage, список `out/` (пишет `eval.os`) |
| `runs/<run_id>/analysis.md` | Человеческий разбор (пишем вручную после прогона) |
| [backfill_notes.py](backfill_notes.py) | Восстановить NOTES из уже лежащего `report.json` (разбор, не gate) |

Полные логи и homes не копируем сюда — они в `runs/<run_id>/`.
После каждого live-eval `eval.os` дублирует краткие NOTES сюда автоматически.
