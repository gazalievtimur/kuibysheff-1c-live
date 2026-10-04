#!/bin/sh
set -eu
export SEARXNG_SETTINGS_PATH="${SEARXNG_SETTINGS_PATH:-/data/searxng/settings.yml}"
cd /opt/searxng
export PYTHONPATH=/opt/searxng${PYTHONPATH:+:$PYTHONPATH}
exec /opt/searxng/.venv/bin/python -m searx.webapp
