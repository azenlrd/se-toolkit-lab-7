"""Environment configuration for the bot."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env.bot.secret from the bot directory
_env_path = Path(__file__).resolve().parent / ".env.bot.secret"
load_dotenv(_env_path)

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
LMS_API_URL: str = os.getenv("LMS_API_URL", "http://localhost:42002")
LMS_API_KEY: str = os.getenv("LMS_API_KEY", "")
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
LLM_API_BASE_URL: str = os.getenv("LLM_API_BASE_URL", "http://localhost:42005/v1")
LLM_API_MODEL: str = os.getenv("LLM_API_MODEL", "coder-model")
