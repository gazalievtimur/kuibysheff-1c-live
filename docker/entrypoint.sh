#!/bin/sh
set -eu
export PYTHONPATH=/app
export DATA_DIR="${DATA_DIR:-/data}"
mkdir -p \
  "$DATA_DIR/logs" \
  "$DATA_DIR/code-index" \
  "$DATA_DIR/sntx-sem/hbk" \
  "$DATA_DIR/sntx-sem/data" \
  "$DATA_DIR/conf-doc/output" \
  "$DATA_DIR/searxng" \
  "$DATA_DIR/caddy" \
  "$DATA_DIR/configs" \
  "$DATA_DIR/tasks" \
  "$DATA_DIR/runs"
/opt/web-venv/bin/python -m web.filesetup
exec /usr/bin/supervisord -n -c /app/docker/supervisord.conf
