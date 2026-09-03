# Предустановка

Перед `scripts/install` поставьте обязательные хост-инструменты. **Node.js** и **Java 17+** нужны для штатного MCP [bsl-language-server](https://github.com/1c-syntax/bsl-language-server) (`tools/bsl-ls-mcp` + JAR); каталог `bin` платформы 1С — для ingest `sntx_sem`.

Если чего-то из рекомендуемого нет, install покажет **предупреждение** со ссылками и спросит, продолжать ли без них (`[y/N]`, по умолчанию — остановиться). В `-NonInteractive` / `--non-interactive` только предупреждение в лог, install идёт дальше. Свой MCP без Node/Java можно подключить позже.

После установки инструментов: [howto-pipeline.md](howto-pipeline.md) §1 или [README](../README.md) «Быстрый старт».

## Обязательно

| Инструмент | Зачем | Куда смотреть |
| --- | --- | --- |
| **OneScript 2.0** | оркестратор `harness/run.os` (`oscript` в `PATH`) | [oscript.io](https://oscript.io/) — скачайте дистрибутив 2.x, добавьте в `PATH`, проверьте `oscript -version` |
| **Git** | clone зависимостей при необходимости | [git-scm.com](https://git-scm.com/downloads) |
| **Python 3** | runtime MCP `1c-sntx-sem` (venv при install) | [python.org](https://www.python.org/downloads/) — на Windows удобен `py -3`; проверьте `python --version` / `python3 --version` |
| **curl** | загрузки GitHub Releases (Linux/macOS обычно уже есть; на Windows часто есть `curl.exe`) | входит в ОС или [curl.se](https://curl.se/download.html) |
| **unzip** (Linux) | распаковка zip `kbshff` из Releases | пакет менеджера ОС, напр. `sudo apt install unzip` |

API-ключ OpenAI-compatible провайдера задаётся при install (или в `.env`) — отдельный бинарь не нужен.

## Опционально (штатный BSL lint MCP)

| Инструмент | Зачем | Куда смотреть |
| --- | --- | --- |
| **Node.js** (LTS) + `npm` | мост `tools/bsl-ls-mcp` → JAR | [nodejs.org](https://nodejs.org/) — после установки: `node -v`, `npm -v` |
| **JDK 17+** | запуск `bsl-language-server-*-exec.jar` | [Adoptium Temurin](https://adoptium.net/) или другой JDK 17+; при желании задайте `JAVA_HOME` |

Без них install не падает: стадии yaxunit/coder/implementer просто не получат блок `bsl-language-server` в конфиге (можно подключить свой MCP через CLI/`profiles`).

## Опционально (live / ingest)

| Что | Зачем |
| --- | --- |
| Платформа 1С, каталог `bin` (`1cv8` / `ibcmd`) | ingest справки `sntx_sem`; флаг `--require-platform` у harness |
| `cargo` + Rust | только если нет готового `kbshff` в Releases и нужна сборка из исходников ([Agent-Kuibysheff](https://github.com/gazalievtimur/Agent-Kuibysheff)) |

## Быстрая проверка

```text
oscript -version
git --version
python --version   # или: py -3 --version / python3 --version
curl --version
node -v            # опционально
java -version      # опционально, 17+
```

Затем: `.\scripts\install.cmd` или `./scripts/install.sh`.
