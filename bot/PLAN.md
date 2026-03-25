# Bot Development Plan

## Overview

This Telegram bot serves as a conversational interface to the LMS backend. It follows a
testable-handler architecture where command logic is fully decoupled from the Telegram
transport layer. Every handler is a plain Python function that accepts a string argument
and returns a string response. This makes offline testing trivial via a `--test` CLI mode
and keeps the Telegram-specific code minimal.

## Task 1 — Scaffold

Create the `bot/` directory with:

- **`bot.py`** — entry point that supports two modes: Telegram polling (default) and
  `--test` CLI mode. In test mode it parses the user input, routes to the correct handler,
  prints the response to stdout, and exits with code 0.
- **`handlers/`** — one module per command group (`start`, `help`, `health`, `scores`,
  `labs`). Each exports a function `handle(args: str) -> str`.
- **`services/`** — thin wrappers for the LMS backend API and (later) the LLM provider.
- **`config.py`** — loads environment variables from `.env.bot.secret` using
  `python-dotenv`.
- **`pyproject.toml`** — declares dependencies (`python-telegram-bot`, `httpx`,
  `python-dotenv`) and requires Python ≥ 3.11.

## Task 2 — Backend Integration

Replace placeholder responses in `/health`, `/scores`, and `/labs` handlers with real
HTTP calls to the LMS backend via the `services/api_client.py` module. The API client
reads `LMS_API_URL` and `LMS_API_KEY` from config and uses `httpx` for requests.

## Task 3 — Intent Routing

Add a natural-language intent router so free-text messages like "what labs are available"
are mapped to the appropriate handler. This uses the LLM service (`services/llm_client.py`)
configured via `LLM_API_KEY`.

## Task 4 — Deployment

Containerise the bot with a `Dockerfile`, add it to `docker-compose.yml`, and configure
`.env.bot.secret` on the VM. The bot runs as a long-lived polling process alongside the
existing backend and frontend services.
