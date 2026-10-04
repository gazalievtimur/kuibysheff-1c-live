#!/bin/sh
set -eu
export CONF_DOC_CONFIG_PATH="${CONF_DOC_CONFIG_PATH:-/data/conf-doc/config.yaml}"
cd /data/conf-doc
exec /opt/tools/conf-doc/.venv/bin/conf-doc serve --host 127.0.0.1 --port 18050
