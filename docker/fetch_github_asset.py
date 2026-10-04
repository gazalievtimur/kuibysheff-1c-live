#!/usr/bin/env python3
"""Download one asset from the latest GitHub release. Prints the saved path."""

import fnmatch
import json
import os
import sys
import urllib.request

UA = "kuibysheff-1c-live-docker"


def _headers() -> dict:
    headers = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    if token.strip():
        headers["Authorization"] = f"Bearer {token.strip()}"
    return headers


def latest(repo: str) -> dict:
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/releases/latest",
        headers=_headers(),
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)


def download(url: str, dest: str) -> None:
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=600) as resp, open(dest, "wb") as out:
        while True:
            chunk = resp.read(1024 * 256)
            if not chunk:
                break
            out.write(chunk)


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: fetch_github_asset.py OWNER/REPO GLOB DEST")
    repo, pattern, dest = sys.argv[1:]
    data = latest(repo)
    for asset in data.get("assets", []):
        name = asset.get("name") or ""
        if fnmatch.fnmatch(name, pattern):
            print(f"GET {asset['browser_download_url']}", flush=True)
            download(asset["browser_download_url"], dest)
            print(dest)
            return
    names = ", ".join(a.get("name", "") for a in data.get("assets", []))
    raise SystemExit(f"No asset matching {pattern!r} in {repo}. Assets: {names}")


if __name__ == "__main__":
    main()
