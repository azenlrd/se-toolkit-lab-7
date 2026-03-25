"""Handler for the /scores command."""


def handle(args: str = "") -> str:
    """Return scores for a given lab (placeholder)."""
    if not args.strip():
        return "Usage: /scores <lab-id>"
    return f"Scores for {args.strip()}: not implemented yet."
