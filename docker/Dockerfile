# kuibysheff-1c-live: agent, MCP stack, native UIs, portal.
# linux/amd64. Embeddings are external (no torch / sentence-transformers).

# syntax=docker/dockerfile:1
# trixie: kbshff release needs glibc >= 2.39 (bookworm has 2.36).
FROM debian:trixie-slim

ARG KBSHFF_REPO=gazalievtimur/Agent-Kuibysheff
ARG ONESCRIPT_REPO=EvilBeaver/OneScript
ARG CODE_INDEX_REPO=Regsorm/code-index-mcp
ARG BSL_LS_REPO=1c-syntax/bsl-language-server
ARG CADDY_REPO=caddyserver/caddy
ARG SNTX_SEM_GIT_REF=main
ARG CONF_DOC_GIT_REF=main
ARG SEARXNG_GIT_REF=master

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    CODE_INDEX_HOME=/data/code-index \
    SNTX_SEM_CONFIG=/data/sntx-sem/config.yaml \
    SNTX_SEM_API_URL=http://127.0.0.1:18051 \
    CONF_DOC_API_URL=http://127.0.0.1:18050 \
    CONF_DOC_CONFIG_PATH=/data/conf-doc/config.yaml \
    SEARXNG_MCP_URL=http://127.0.0.1:3000/mcp \
    SEARXNG_SETTINGS_PATH=/data/searxng/settings.yml \
    KUIBYSHEFF_ALLOW_UNSANDBOXED_MCP=1 \
    DATA_DIR=/data \
    REPO_ROOT=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl unzip tar xz-utils git \
        python3 python3-venv python3-dev python3-pip \
        build-essential pkg-config \
        libxml2-dev libxslt1-dev libffi-dev libssl-dev zlib1g-dev \
        openjdk-21-jre-headless libicu76 \
        supervisor tini ripgrep \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -c "import sys; assert sys.version_info >= (3, 11)" \
    && ln -sfn "$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")" /opt/java-home

COPY docker/fetch_github_asset.py docker/fetch.sh /tmp/

# OneScript
RUN --mount=type=secret,id=github_token,required=false \
    sh /tmp/fetch.sh "$ONESCRIPT_REPO" "*linux-x64*" /tmp/oscript.pkg \
    && mkdir -p /opt/oscript \
    && (tar -xzf /tmp/oscript.pkg -C /opt/oscript || tar -xf /tmp/oscript.pkg -C /opt/oscript || unzip -qo /tmp/oscript.pkg -d /opt/oscript) \
    && OSCRIPT_BIN="$(find /opt/oscript -type f -name oscript | head -n 1)" \
    && test -n "$OSCRIPT_BIN" \
    && chmod +x "$OSCRIPT_BIN" \
    && ln -sf "$OSCRIPT_BIN" /usr/local/bin/oscript \
    && rm -f /tmp/oscript.pkg

# kbshff
RUN --mount=type=secret,id=github_token,required=false \
    sh /tmp/fetch.sh "$KBSHFF_REPO" "agent_Kuibysheff-*-x86_64-unknown-linux-gnu.zip" /tmp/kbshff.zip \
    && (sh /tmp/fetch.sh "$KBSHFF_REPO" "agent_Kuibysheff-*-x86_64-unknown-linux-gnu.zip.sha256" /tmp/kbshff.zip.sha256 \
        && echo "$(awk '{print $1}' /tmp/kbshff.zip.sha256)  /tmp/kbshff.zip" | sha256sum -c - \
        || echo "kbshff checksum skipped or mismatched; continuing if the zip exists") \
    && test -s /tmp/kbshff.zip \
    && mkdir -p /tmp/kbshff-extract /opt/tools \
    && unzip -qo /tmp/kbshff.zip -d /tmp/kbshff-extract \
    && KB="$(find /tmp/kbshff-extract -type f -name kbshff | head -n 1)" \
    && test -n "$KB" \
    && cp "$KB" /opt/tools/kbshff \
    && chmod +x /opt/tools/kbshff \
    && ln -sf /opt/tools/kbshff /usr/local/bin/kbshff \
    && rm -rf /tmp/kbshff.zip /tmp/kbshff.zip.sha256 /tmp/kbshff-extract

# code-index (bsl-indexer)
RUN --mount=type=secret,id=github_token,required=false \
    sh /tmp/fetch.sh "$CODE_INDEX_REPO" "bsl-indexer-linux-x64.tar.gz" /tmp/bsl-indexer.tar.gz \
    && mkdir -p /tmp/code-index /opt/tools \
    && tar -xzf /tmp/bsl-indexer.tar.gz -C /tmp/code-index \
    && IDX="$(find /tmp/code-index -type f -name bsl-indexer | head -n 1)" \
    && test -n "$IDX" \
    && cp "$IDX" /opt/tools/bsl-indexer \
    && chmod +x /opt/tools/bsl-indexer \
    && ln -sf /opt/tools/bsl-indexer /usr/local/bin/bsl-indexer \
    && rm -rf /tmp/bsl-indexer.tar.gz /tmp/code-index

# BSL Language Server JAR
RUN --mount=type=secret,id=github_token,required=false \
    sh /tmp/fetch.sh "$BSL_LS_REPO" "*-exec.jar" /opt/tools/bsl-language-server.jar \
    && mkdir -p /opt/tools/bsl-ls \
    && mv /opt/tools/bsl-language-server.jar /opt/tools/bsl-ls/bsl-language-server.jar

# Caddy
RUN --mount=type=secret,id=github_token,required=false \
    sh /tmp/fetch.sh "$CADDY_REPO" "caddy_*_linux_amd64.tar.gz" /tmp/caddy.tar.gz \
    && mkdir -p /tmp/caddy \
    && tar -xzf /tmp/caddy.tar.gz -C /tmp/caddy \
    && cp "$(find /tmp/caddy -type f -name caddy | head -n 1)" /usr/local/bin/caddy \
    && chmod +x /usr/local/bin/caddy \
    && rm -rf /tmp/caddy.tar.gz /tmp/caddy

# 1c-sntx-sem — external embeddings only
RUN git clone --depth 1 --branch "$SNTX_SEM_GIT_REF" https://github.com/gybson63/1c-sntx-sem.git /opt/tools/1c-sntx-sem \
    && python3 -m venv /opt/tools/1c-sntx-sem/.venv \
    && /opt/tools/1c-sntx-sem/.venv/bin/pip install -U pip \
    && /opt/tools/1c-sntx-sem/.venv/bin/pip install -e /opt/tools/1c-sntx-sem \
    && /opt/tools/1c-sntx-sem/.venv/bin/python -c "import importlib.util as u; assert u.find_spec('torch') is None; assert u.find_spec('sentence_transformers') is None" \
    && ln -sf /opt/tools/1c-sntx-sem/.venv/bin/sntx-sem /usr/local/bin/sntx-sem

# 1c-conf-doc — openai + mcp extras, no local embeddings
RUN git clone --depth 1 --branch "$CONF_DOC_GIT_REF" https://github.com/gybson63/1c-conf-doc.git /opt/tools/conf-doc \
    && python3 -m venv /opt/tools/conf-doc/.venv \
    && /opt/tools/conf-doc/.venv/bin/pip install -U pip \
    && /opt/tools/conf-doc/.venv/bin/pip install -e "/opt/tools/conf-doc[openai,mcp]" \
    && /opt/tools/conf-doc/.venv/bin/python -c "import importlib.util as u; assert u.find_spec('torch') is None; assert u.find_spec('sentence_transformers') is None" \
    && ln -sf /opt/tools/conf-doc/.venv/bin/conf-doc /usr/local/bin/conf-doc

# SearXNG
RUN git clone --depth 1 --branch "$SEARXNG_GIT_REF" https://github.com/searxng/searxng.git /opt/searxng \
    && python3 -m venv /opt/searxng/.venv \
    && /opt/searxng/.venv/bin/pip install -U pip \
    && /opt/searxng/.venv/bin/pip install -r /opt/searxng/requirements.txt

RUN npm install -g mcp-searxng

ENV OSCRIPT_BIN=/usr/local/bin/oscript \
    KBSHFF_BIN=/opt/tools/kbshff \
    BSL_INDEXER=/opt/tools/bsl-indexer \
    SNTX_SEM_BIN=/opt/tools/1c-sntx-sem/.venv/bin/sntx-sem \
    SNTX_SEM_PYTHON=/opt/tools/1c-sntx-sem/.venv/bin/python \
    CONF_DOC_MCP=/opt/tools/conf-doc/.venv/bin/conf-doc \
    BSL_LS_JAR=/opt/tools/bsl-ls/bsl-language-server.jar \
    JAVA_HOME=/opt/java-home \
    PATH="/opt/tools:/usr/local/bin:${PATH}"

WORKDIR /app
COPY . /app
RUN npm install --omit=dev --prefix /app/tools/bsl-ls-mcp \
    && python3 -m venv /opt/web-venv \
    && /opt/web-venv/bin/pip install -U pip \
    && /opt/web-venv/bin/pip install -r /app/web/requirements.txt \
    && chmod +x /app/docker/entrypoint.sh /app/docker/bin/*.sh \
    && oscript -encoding=utf-8 /app/harness/run.os --repo-root /app --dry-run

ENV BSL_LS_MCP=/app/tools/bsl-ls-mcp/server.js

EXPOSE 8080 8050 8051 8888
VOLUME ["/data"]
ENTRYPOINT ["/usr/bin/tini", "--", "/app/docker/entrypoint.sh"]
