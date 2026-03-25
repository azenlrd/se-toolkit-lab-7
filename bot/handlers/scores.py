"""Handler for the /scores command."""

import httpx
from services import api_client


def handle(args: str = "") -> str:
    """Return per-task pass rates for a given lab."""
    lab = args.strip()
    if not lab:
        return "Usage: /scores <lab-id>\nExample: /scores lab-04"

    try:
        rates = api_client.get_pass_rates(lab)
        if not rates:
            return f"No score data found for {lab}."
        lines = [f"Pass rates for {lab}:"]
        for entry in rates:
            task = entry.get("task", "Unknown")
            avg = entry.get("avg_score", 0.0)
            attempts = entry.get("attempts", 0)
            lines.append(f"- {task}: {avg}% ({attempts} attempts)")
        return "\n".join(lines)
    except httpx.ConnectError:
        return f"Backend error: connection refused. Check that the services are running."
    except httpx.HTTPStatusError as exc:
        return f"Backend error: HTTP {exc.response.status_code} {exc.response.reason_phrase}."
    except Exception as exc:
        return f"Backend error: {exc}."
