# Предустановка

Перед `scripts/install` поставьте **Git**, **Python 3**, **curl** (`unzip` на Linux). **OneScript** install может поставить сам через [OVM](https://github.com/oscript-library/ovm) (`ovm install/use stable`), если `oscript` ещё нет в PATH.

**Node.js** и **Java 17+** нужны для штатного MCP [bsl-language-server](https://github.com/1c-syntax/bsl-language-server); каталог `bin` платформы 1С — для ingest `sntx_sem`. Если их нет, install покажет предупреждение и спросит, продолжать ли (`[y/N]`). В `-NonInteractive` — только лог.

После установки: [howto-pipeline.md](howto-pipeline.md) §1 или [README](../README.md) «Быстрый старт».

## Обязательно (вручную)

| Инструмент | Зачем | Куда смотреть |
| --- | --- | --- |
| **Git** | clone зависимостей при необходимости | [git-scm.com](https://git-scm.com/downloads) |
| **Python 3** | runtime MCP `1c-sntx-sem` (venv при install) | [python.org](https://www.python.org/downloads/) — на Windows удобен `py -3` |

Install клонирует [`1c-sntx-sem`](https://github.com/gybson63/1c-sntx-sem) на известный рабочий коммит (`-SntxSemGitRef` / `SNTX_SEM_GIT_REF`): на `main` сейчас отсутствует `src/sntx_sem/config.py`, из‑за чего `ingest` падает с `ModuleNotFoundError`. Уже скачанный сломанный clone в `tools/1c-sntx-sem` install поправит checkout’ом.
| **curl** | загрузки GitHub Releases | входит в ОС или [curl.se](https://curl.se/download.html) |
| **unzip** (Linux) | распаковка zip `kbshff` | напр. `sudo apt install unzip` |
| **.NET Framework 4.8+** (Windows) или **Mono 6+** (Linux/macOS) | только если install качает OVM (`ovm.exe`) | обычно уже есть на Win10+; Linux: пакеты Mono |

API-ключ OpenAI-compatible провайдера задаётся при install (или в `.env`).

## OneScript (ставит install через OVM)

| | |
| --- | --- |
| Зачем | оркестратор `harness/run.os` |
| Авто | если нет `oscript`, install скачает `ovm.exe` в `tools/ovm/`, выполнит `ovm install <ver>` и `ovm use <ver>` (по умолчанию `stable`). Флаг: `-OscriptVersion` / `--oscript-version` |
| Вручную | [OVM](https://github.com/oscript-library/ovm/releases) → `ovm install stable` → `ovm use stable`; либо дистрибутив с [oscript.io](https://oscript.io/learn/install) |
| PATH | после `ovm use` добавьте `…/ovm/current/bin` в PATH для новых оболочек (текущий install уже дописывает PATH процесса) |
| `OVM_INSTALL_PATH` | опционально — каталог версий OneScript |

## Опционально (штатный BSL lint MCP)

| Инструмент | Зачем | Куда смотреть |
| --- | --- | --- |
| **Node.js** (LTS) + `npm` | мост `tools/bsl-ls-mcp` → JAR | [nodejs.org](https://nodejs.org/) |
| **JDK 17+** | запуск `bsl-language-server-*-exec.jar` | [Adoptium Temurin](https://adoptium.net/) |

## Опционально (live / ingest)

| Что | Зачем |
| --- | --- |
| Платформа 1С, каталог `bin` (`1cv8` / `ibcmd`) | ingest справки `sntx_sem`; `--require-platform` у harness |
| `cargo` + Rust | только если нет готового `kbshff` в Releases |

## Быстрая проверка

```text
oscript -version
git --version
python --version   # или: py -3 --version / python3 --version
curl --version
node -v            # опционально
java -version      # опционально, 17+
```

Затем: `.\scripts\install.cmd` или `./scripts/install.sh`. Повторный запуск продолжит с checkpoint (`.install-state.json`); с нуля — `-Fresh` / `--fresh`.
