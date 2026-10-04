#!/bin/sh
set -eu
export SNTX_SEM_CONFIG="${SNTX_SEM_CONFIG:-/data/sntx-sem/config.yaml}"
export EMBEDDINGS_API_KEY="$(/opt/web-venv/bin/python -c 'from web.filesetup import embeddings_api_key; print(embeddings_api_key())')"
exec /opt/tools/1c-sntx-sem/.venv/bin/sntx-sem serve --host 127.0.0.1 --port 18051
