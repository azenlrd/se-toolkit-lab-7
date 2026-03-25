"""Handler for the /help command."""


def handle(args: str = "") -> str:
    """Return the list of available commands."""
    return (
        "Available commands:\n"
        "/start  — Welcome message\n"
        "/help   — Show this help\n"
        "/health — Check backend status\n"
        "/labs   — List available labs\n"
        "/scores <lab-id> — View per-task pass rates for a lab"
    )
