"""
Real Gmail provider (ARCHITECTURE.md §5).

Read-only metadata + relevant thread snippets only. Never returns raw bodies.
"""
from __future__ import annotations

import base64
import uuid

from app.mcp.context import Citation


async def fetch_email_summary(token: str, user_id: uuid.UUID) -> tuple[list[Citation], bool]:
    """Fetch the 3 most recent inbox messages and return short thread summaries."""
    try:
        import httpx
    except ImportError:
        return [], True

    headers = {"Authorization": f"Bearer {token}"}
    list_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    params = {"maxResults": 3, "labelIds": "INBOX"}

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(list_url, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return [], True

    msgs = data.get("messages", [])
    if not msgs:
        return [], True

    citations: list[Citation] = []
    for m in msgs[:3]:
        meta_url = f"{list_url}/{m['id']}"
        meta_params = {"format": "metadata", "metadataHeaders": ["Subject", "From", "Date"]}
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                meta = await client.get(meta_url, params=meta_params, headers=headers)
                meta.raise_for_status()
                payload = meta.json()
        except Exception:
            continue

        headers_list = payload.get("payload", {}).get("headers", [])
        header_map = {h["name"]: h["value"] for h in headers_list}
        subject = header_map.get("Subject", "(no subject)")
        sender = header_map.get("From", "unknown sender")
        # Pull a short excerpt from the body, not the full payload
        excerpt = _short_excerpt(payload.get("snippet", ""))
        citations.append(
            Citation(
                source="email",
                detail=f"Recent email from {sender}: '{subject}'{(' — ' + excerpt) if excerpt else ''}",
            )
        )
    return citations, False


def _short_excerpt(snippet: str) -> str:
    # Gmail's `snippet` is already a short redacted excerpt; cap to 140 chars
    s = snippet.strip()
    if len(s) > 140:
        s = s[:137] + "..."
    return s
