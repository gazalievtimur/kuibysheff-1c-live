#!/bin/sh
# Loads an optional BuildKit secret and downloads one GitHub release asset.
if [ -f /run/secrets/github_token ]; then
  GITHUB_TOKEN="$(cat /run/secrets/github_token)"
  export GITHUB_TOKEN
fi
exec python3 /tmp/fetch_github_asset.py "$@"
