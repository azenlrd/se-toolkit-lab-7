"""Handler for the /health command."""

import httpx
from services import api_client


def handle(args: str = "") -> str:
    """Check backend health by fetching items."""
    try:
        items = api_client.get_items()
        return f"Backend is healthy. {len(items)} items available."
    except httpx.ConnectError:
        return f"Backend error: connection refused ({api_client._base_url()}). Check that the services are running."
    except httpx.HTTPStatusError as exc:
        return f"Backend error: HTTP {exc.response.status_code} {exc.response.reason_phrase}. The backend service may be down."
    except Exception as exc:
        return f"Backend error: {exc}."
