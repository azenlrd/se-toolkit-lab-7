"""Handler for the /help command."""


def handle(args: str = "") -> str:
    """Return the list of available commands."""
    return (
        "Available commands:\n"
        "/start  — Welcome message\n"
        "/help   — Show this help\n"
        "/health — Check backend status\n"
        "/scores <lab-id> — View scores for a lab\n"
        "/labs   — List available labs"
    )
