# Правила вызова code-index (1c-live)

Имена инструментов и их аргументы — это `Available MCP tools` текущего прогона и `agent.describe_tool`. Этот файл их не перечисляет.

Сервер: **`code-index`**. Алиас репозитория: **`cf`**. Каждый вызов передаёт `"repo":"cf"`. Алиас `default` не существует (`unknown_repo`).

Повтор того же `find_symbol` запрещён. У попадания есть `file_path`, `line_start`, `line_end`. Это номера строк, не смещение `local_tools.read_file` (`offset` там в символах). Метаданные XML постранично не читать.

`daemon_offline` — индекса нет, заканчивать по `conf_doc`. `denied` — такого инструмента нет; тот же вызов не повторять. Это не офлайн индекса и не повод читать дерево конфигурации через `local_tools`. Инструментов `search` и `get_file` нет.

`-ConfigPath` для скриптов навыков — поле `cf_root` из `in/product.json`.
