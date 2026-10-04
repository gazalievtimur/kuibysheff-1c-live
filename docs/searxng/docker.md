# SearXNG в контейнере kuibysheff-1c-live

Образ из [docs/docker.md](../docker.md) сам поднимает SearXNG (`127.0.0.1:18888`, наружу порт 8888) и `mcp-searxng` (`127.0.0.1:3000/mcp`). JSON-формат поиска включён. В портале чекбокс «Веб-поиск» передаёт харнесу `--with-searxng`.

Отдельный `docker run isokoliuk/mcp-searxng` для этого контейнера не нужен.
