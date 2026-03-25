"""LMS Telegram Bot — entry point.

Supports two modes:
  - Telegram polling (default): connects to Telegram and listens for messages.
  - Test mode: `uv run bot.py --test "/command args"` routes to handlers and prints output.
"""

import argparse
import sys

from handlers import start, help as help_cmd, health, scores, labs


# Map command names to handler modules
COMMANDS: dict[str, object] = {
    "/start": start,
    "/help": help_cmd,
    "/health": health,
    "/scores": scores,
    "/labs": labs,
}


def route(text: str) -> str:
    """Route user input to the appropriate handler and return the response."""
    text = text.strip()
    if not text:
        return "Empty input. Type /help to see available commands."

    # Check if it's a slash command
    parts = text.split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    handler_module = COMMANDS.get(command)
    if handler_module is not None:
        return handler_module.handle(args)

    return f"Unknown command: {command}. Type /help to see available commands."


def run_test(input_text: str) -> None:
    """Run a single command in test mode and print the result."""
    response = route(input_text)
    print(response)


def run_telegram() -> None:
    """Start the Telegram bot with long polling."""
    from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
    import config

    if not config.BOT_TOKEN:
        print("Error: BOT_TOKEN is not set. Check .env.bot.secret", file=sys.stderr)
        sys.exit(1)

    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # Register command handlers
    async def _make_handler(handler_module):
        async def _handler(update, context):
            args = " ".join(context.args) if context.args else ""
            response = handler_module.handle(args)
            await update.message.reply_text(response)
        return _handler

    async def _post_init(application) -> None:
        """Register handlers after the application is built."""
        for cmd, mod in COMMANDS.items():
            cmd_name = cmd.lstrip("/")
            handler_fn = await _make_handler(mod)
            application.add_handler(CommandHandler(cmd_name, handler_fn))

    app.post_init = _post_init
    print("Bot is starting...")
    app.run_polling()


def main() -> None:
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="INPUT",
        help='Test mode: route a command and print the response (e.g. --test "/start")',
    )
    args = parser.parse_args()

    if args.test is not None:
        run_test(args.test)
    else:
        run_telegram()


if __name__ == "__main__":
    main()
