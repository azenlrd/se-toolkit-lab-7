"""HTTP client for the LMS backend API."""

import httpx
import config


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {config.LMS_API_KEY}"}


def _base_url() -> str:
    return config.LMS_API_URL.rstrip("/")


def get_items() -> list[dict]:
    """Fetch all items (labs and tasks) from the backend."""
    resp = httpx.get(f"{_base_url()}/items/", headers=_headers(), timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_learners() -> list[dict]:
    """Fetch enrolled students."""
    resp = httpx.get(f"{_base_url()}/learners/", headers=_headers(), timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_scores(lab: str) -> list[dict]:
    """Fetch score distribution (4 buckets) for a lab."""
    resp = httpx.get(
        f"{_base_url()}/analytics/scores",
        params={"lab": lab},
        headers=_headers(),
        timeout=10,
    )
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


def get_timeline(lab: str) -> list[dict]:
    """Fetch submissions per day for a lab."""
    resp = httpx.get(
        f"{_base_url()}/analytics/timeline",
        params={"lab": lab},
        headers=_headers(),
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def get_groups(lab: str) -> list[dict]:
    """Fetch per-group performance for a lab."""
    resp = httpx.get(
        f"{_base_url()}/analytics/groups",
        params={"lab": lab},
        headers=_headers(),
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def get_top_learners(lab: str, limit: int = 5) -> list[dict]:
    """Fetch top N learners by score for a lab."""
    resp = httpx.get(
        f"{_base_url()}/analytics/top-learners",
        params={"lab": lab, "limit": limit},
        headers=_headers(),
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def get_completion_rate(lab: str) -> dict:
    """Fetch completion rate percentage for a lab."""
    resp = httpx.get(
        f"{_base_url()}/analytics/completion-rate",
        params={"lab": lab},
        headers=_headers(),
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def trigger_sync() -> dict:
    """Trigger ETL sync from autochecker."""
    resp = httpx.post(
        f"{_base_url()}/pipeline/sync",
        headers=_headers(),
        json={},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()
