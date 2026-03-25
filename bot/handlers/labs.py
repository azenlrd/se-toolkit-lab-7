"""Handler for the /labs command."""

import httpx
from services import api_client


def handle(args: str = "") -> str:
    """List available labs from the backend."""
    try:
        items = api_client.get_items()
        labs = [item for item in items if item.get("type") == "module"]
        if not labs:
            return "No labs found."
        lines = ["Available labs:"]
        for lab in labs:
            title = lab.get("title", "Untitled")
            lines.append(f"- {title}")
        return "\n".join(lines)
    except httpx.ConnectError:
        return f"Backend error: connection refused. Check that the services are running."
    except httpx.HTTPStatusError as exc:
        return f"Backend error: HTTP {exc.response.status_code} {exc.response.reason_phrase}."
    except Exception as exc:
        return f"Backend error: {exc}."
