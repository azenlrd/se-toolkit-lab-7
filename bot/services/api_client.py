"""HTTP client for the LMS backend API."""

import httpx
import config


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {config.LMS_API_KEY}"}


def _base_url() -> str:
    return config.LMS_API_URL.rstrip("/")


def get_items() -> list[dict]:
    """Fetch all items from the backend."""
    resp = httpx.get(f"{_base_url()}/items/", headers=_headers(), timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_pass_rates(lab: str) -> list[dict]:
    """Fetch per-task pass rates for a lab."""
    resp = httpx.get(
        f"{_base_url()}/analytics/pass-rates",
        params={"lab": lab},
        headers=_headers(),
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()
