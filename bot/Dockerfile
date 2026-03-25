ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=bot/pyproject.toml,target=bot/pyproject.toml \
    --mount=type=bind,source=bot/uv.lock,target=bot/uv.lock \
    cd bot && uv sync --locked --no-install-project

COPY bot /app/bot

RUN --mount=type=cache,target=/root/.cache/uv \
    cd bot && uv sync --locked

# --- Stage 2 ---
ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

COPY --from=builder --chown=nonroot:nonroot /app /app

ENV PATH="/app/bot/.venv/bin:$PATH"

USER nonroot
WORKDIR /app/bot

CMD ["python", "bot.py"]
