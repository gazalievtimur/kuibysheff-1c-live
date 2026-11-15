# Установка контейнера kuibysheff-1c-live (для агента)

Цель: один контейнер `linux/amd64` с `kbshff`, code-index, sntx-sem, conf-doc, SearXNG, BSL Language Server и веб-порталом. Хостовые `scripts/install.sh` и `scripts/install.ps1` для этого пути не запускать: OneScript, Java, Node и бинарники уже внутри образа.

Человеческое описание тех же портов и ограничений: [docker.md](docker.md).

## Что нужно на машине

- Docker Engine с Compose v2 и BuildKit. Образ только `linux/amd64` (на Apple Silicon сборка идёт через эмуляцию amd64).
- Доступ в интернет на время сборки: GitHub Releases, clone `1c-sntx-sem`, `1c-conf-doc`, SearXNG, NodeSource.
- `GITHUB_TOKEN` или `gh auth token`. Compose передаёт его как BuildKit secret (`secrets.github_token`). Токен в слои образа не записывается. Без токена GitHub API часто отвечает 403, и сборка обрывается на скачивании OneScript.
- Свободные порты хоста `8080`, `8050`, `8051`, `8888`. Если заняты, меняется только левая часть проброса в [docker-compose.yml](../docker-compose.yml). Порты внутри контейнера не менять.

Платформа 1С в образ не входит. Для ingest справки и `--require-platform` её каталог монтируется с хоста в `/opt/1cv8` (строка в compose закомментирована).

## Сборка и запуск

Рабочий каталог — корень репозитория.

```bash
export GITHUB_TOKEN="$(gh auth token)"
docker compose build
export WEB_USER=admin
export WEB_PASSWORD='choose-a-password'
docker compose up -d
```

```powershell
$env:GITHUB_TOKEN = (gh auth token).Trim()
docker compose build
$env:WEB_USER = 'admin'
$env:WEB_PASSWORD = 'choose-a-password'
docker compose up -d
```

`WEB_PASSWORD` пустой: Caddy не спрашивает пароль и пишет предупреждение в лог. Для машины, доступной не только с localhost, пароль задавать.

Переменные `LLM_BASE_URL`, `OPENAI_API_KEY`, `EMBEDDINGS_*` в compose необязательны. Их можно задать до первого `up`, тогда портал возьмёт их как начальные значения. Дальше источник истины — форма **Настройки**, том `/data`. Ключ в git не коммитить.

## Проверка, что контейнер жив

```bash
docker compose ps
docker compose exec kuibysheff-1c-live kbshff --version
docker compose exec kuibysheff-1c-live oscript -version
docker compose exec kuibysheff-1c-live bsl-indexer daemon status
curl -fsS -u "$WEB_USER:$WEB_PASSWORD" -o /dev/null -w "portal %{http_code}\n" http://127.0.0.1:8080/
curl -fsS -u "$WEB_USER:$WEB_PASSWORD" -o /dev/null -w "conf-doc %{http_code}\n" http://127.0.0.1:8050/health
curl -fsS -u "$WEB_USER:$WEB_PASSWORD" -o /dev/null -w "sntx %{http_code}\n" http://127.0.0.1:8051/
curl -fsS -u "$WEB_USER:$WEB_PASSWORD" -o /dev/null -w "searx %{http_code}\n" "http://127.0.0.1:8888/search?q=test&format=json"
```

Ожидание: `kbshff` печатает версию, демон code-index в статусе `running`, четыре URL отвечают `200`. Запрос без `-u` при заданном пароле отвечает `401`.

В окружениях `sntx-sem` и `conf-doc` не должно быть `torch` и `sentence_transformers`. Эмбеддинги только внешние.

Логи сервисов: `docker compose logs -f kuibysheff-1c-live` и файлы в томе `/data/logs/`.

## Первый запуск задачи через портал

1. Открыть `http://127.0.0.1:8080/` (логин `WEB_USER` / `WEB_PASSWORD`).
2. **Настройки.** `base_url` OpenAI-compatible API, имя переменной ключа, сам ключ, модель для каждой из четырёх стадий (`1c-analyst`, `1c-yaxunit`, `1c-coder`, `1c-implementer`). Кнопка «Проверить /models».
3. Там же **Эмбеддинги**: `base_url`, ключ, модель (по умолчанию `text-embedding-3-small`). «Проверить /embeddings». Сохранение перезаписывает `/data/sntx-sem/config.yaml` и `/data/conf-doc/config.yaml` и перезапускает оба сервиса. У conf-doc ключ лежит в `config.yaml` на томе `/data`. У sntx-sem ключ читается из `EMBEDDINGS_API_KEY`.
4. **Конфигурации.** Учебный «Склад» индексируется сам. Своя XML-выгрузка — zip с `Configuration.xml`. Портал регистрирует путь в code-index и индексирует conf-doc. Пока ключа эмбеддингов нет, индексируются только метаданные.
5. **Задача.** Конфигурация, заголовок, текст брифа. «Веб-поиск» включает SearXNG на analyst и yaxunit. Одновременно выполняется один прогон, остальные ждут в очереди.
6. **Прогоны.** `report.json`, файлы `out/` стадий, zip `out/cfe` и `out/cfe-tests`.

Родные UI, та же Basic Auth: conf-doc `:8050`, sntx-sem `:8051/admin`, SearXNG `:8888`.

## Платформа 1С

Раскомментировать в `docker-compose.yml`:

```yaml
- /opt/1cv8:/opt/1cv8:ro
```

На Windows путь хоста — каталог установки, например `C:\Program Files\1cv8:/opt/1cv8:ro`. Затем `docker compose up -d`.

Ingest справки (без него семантический поиск sntx-sem пустой):

```bash
docker compose exec kuibysheff-1c-live sntx-sem ingest --platform-path /opt/1cv8/<версия>/bin
```

Флаг «Прогон YAxUnit на платформе» в форме задачи активен, только если внутри контейнера найден `ibcmd`.

## Сбои

| Симптом | Что сделать |
| --- | --- |
| `HTTP Error 403: rate limit exceeded` на `fetch.sh` | Задать `GITHUB_TOKEN` в окружении процесса, который запускает `docker compose build`, и собрать снова. |
| `Bind for 0.0.0.0:8080 failed: port is already allocated` | Узнать, кто слушает порт (`docker ps`). Поменять левую часть проброса, не правую. |
| `GLIBC_2.39 not found` у `kbshff` | Образ должен быть на Debian 13 (`debian:trixie-slim`). Не менять базу на bookworm. |
| `oscript: Permission denied` | Бинарник OneScript в слое должен быть `chmod +x`. Пересобрать образ с текущим Dockerfile. |
| SearXNG не ставится (`msgspec` / `yaml` при `pip install -e`) | Ставить зависимости из `requirements.txt` и запускать `python -m searx.webapp` с `PYTHONPATH=/opt/searxng`, как в Dockerfile. |
| Портал открылся, прогон сразу `missing provider API key env` | В **Настройках** не сохранены `base_url`, имя env и значение ключа. |
| conf-doc без семантического поиска | Нет ключа эмбеддингов или индексация шла с `skip_embeddings`. Сохранить эмбеддинги и нажать «Переиндексировать». |
| sntx-sem ищет пусто | Нет ingest с монтированной платформы. Команда ingest выше; пересборка индекса после смены модели — в `:8051/admin`. |

Повторный `docker compose up -d` сохраняет том `kbshff-data` (настройки, выгрузки, прогоны, индексы). Сброс данных: `docker compose down` и удаление этого тома.
