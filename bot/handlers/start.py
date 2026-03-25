"""Handler for the /start command."""


def handle(args: str = "") -> str:
    """Return a welcome message."""
    return (
        "Welcome to the LMS Bot!\n"
        "I can help you check lab scores, view available labs, "
        "and monitor the backend health.\n"
        "Type /help to see available commands."
    )
