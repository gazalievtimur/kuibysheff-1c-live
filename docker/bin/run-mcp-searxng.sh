#!/bin/sh
set -eu
export SEARXNG_URL="${SEARXNG_URL:-http://127.0.0.1:18888}"
export MCP_HTTP_HOST=127.0.0.1
export MCP_HTTP_PORT=3000
export MCP_HTTP_STATELESS=true
exec mcp-searxng
