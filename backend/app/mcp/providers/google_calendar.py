"""
Real Google Calendar provider (ARCHITECTURE.md §5).

Token is decrypted only here, used to call the Calendar API, and never
leaves this function. The result is a list of structured Citation objects
— never raw event payloads.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from app.mcp.context import Citation


async def fetch_calendar_summary(token: str, user_id: uuid.UUID) -> tuple[list[Citation], bool]:
    """Pull the next 24h of calendar events. Returns ([], True) if no events."""
    # Lazy import so the demo fallback path doesn't require httpx to be installed
    try:
        import httpx
    except ImportError:
        return [], True

    now = datetime.now(timezone.utc)
    until = now + timedelta(hours=24)
    params = {
        "timeMin": now.isoformat(),
        "timeMax": until.isoformat(),
        "maxResults": 10,
        "singleEvents": "true",
        "orderBy": "startTime",
    }
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return [], True

    items = data.get("items", [])
    if not items:
        return [], True

    citations: list[Citation] = []
    for ev in items[:5]:
        summary = ev.get("summary", "(no title)")
        start = ev.get("start", {}).get("dateTime", ev.get("start", {}).get("date", ""))
        citations.append(
            Citation(
                source="calendar",
                detail=f"Upcoming event '{summary}' at {start}",
            )
        )
    return citations, False
