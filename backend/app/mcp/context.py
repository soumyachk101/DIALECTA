"""
MCP Context Layer — the only component that holds OAuth tokens or touches
raw provider data. Returns structured, minimal summaries to the orchestrator.
This mirrors ARCHITECTURE.md §5 (privacy boundary).

Provider implementations are isolated in `app/mcp/providers/`. This module
owns the citation shape, the context bundle, and the entry point.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import ConnectedAccount, UserValue
from app.services.crypto import decrypt_token


# ---- Public data shapes returned to the orchestrator ----

@dataclass
class Citation:
    source: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"source": self.source, "detail": self.detail}


@dataclass
class ContextBundle:
    calendar: list[Citation] = field(default_factory=list)
    email: list[Citation] = field(default_factory=list)
    purchase_history: list[Citation] = field(default_factory=list)
    stated_values: list[str] = field(default_factory=list)
    page_context: list[Citation] = field(default_factory=list)
    no_context_providers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "calendar": [c.to_dict() for c in self.calendar],
            "email": [c.to_dict() for c in self.email],
            "purchase_history": [c.to_dict() for c in self.purchase_history],
            "stated_values": list(self.stated_values),
            "page_context": [c.to_dict() for c in self.page_context],
            "no_context_providers": list(self.no_context_providers),
        }


# ---- Provider interface ----
# A provider is an async callable that, given a decrypted token and a user_id,
# returns a tuple of (citations, was_empty). Real implementations live in
# app.mcp.providers; the in-memory mock implementations are kept here so the
# demo works without any external credentials.

from typing import Awaitable, Callable

ProviderFn = Callable[[str, uuid.UUID], Awaitable[tuple[list[Citation], bool]]]


async def _mock_calendar(_token: str, _user_id: uuid.UUID) -> tuple[list[Citation], bool]:
    return [
        Citation("calendar", "Two early-morning meetings scheduled for tomorrow — your recovery sleep window is the 12h before 6am."),
        Citation("calendar", "Travel block next week — discretionary spending this week goes against trip budget."),
    ], False


async def _mock_email(_token: str, _user_id: uuid.UUID) -> tuple[list[Citation], bool]:
    return [
        Citation("email", "Last email in thread was 4h ago from this client asking for a status update — no new aggression noted."),
    ], False


async def _mock_purchase_history(_token: str, _user_id: uuid.UUID) -> tuple[list[Citation], bool]:
    return [
        Citation("purchase_history", "3 similar items in the last 30 days, 2 of them unused."),
        Citation("purchase_history", "Total discretionary spend this month: 78% of monthly cap."),
    ], False


PROVIDER_REGISTRY: dict[str, ProviderFn] = {
    "google_calendar": _mock_calendar,
    "gmail": _mock_email,
    # purchase_history is a virtual provider sourced from a (future) bank/payment connector
    "purchase_history": _mock_purchase_history,
}


# ---- Main entry point ----

async def gather_context(
    session: AsyncSession,
    user_id: uuid.UUID,
    page_context: dict | None = None,
) -> ContextBundle:
    """Pull context from all connected providers. Returns structured summaries only."""
    bundle = ContextBundle()

    # Stated values — needed by Ethicist
    result = await session.execute(
        select(UserValue).where(UserValue.user_id == user_id).order_by(UserValue.priority.desc())
    )
    bundle.stated_values = [v.statement for v in result.scalars().all()]

    # Determine which providers are connected
    accounts_q = await session.execute(
        select(ConnectedAccount).where(ConnectedAccount.user_id == user_id)
    )
    accounts = {a.provider: a for a in accounts_q.scalars().all()}

    # Call each provider, decrypting the token only inside this function
    # (the token never leaves the MCP layer)
    for provider_name, provider_fn in PROVIDER_REGISTRY.items():
        # purchase_history is always queried (sourced from a future bank connector)
        if provider_name != "purchase_history" and provider_name not in accounts:
            bundle.no_context_providers.append(_display_name(provider_name))
            continue

        token = ""
        if provider_name in accounts:
            try:
                token = decrypt_token(accounts[provider_name].encrypted_token)
            except Exception:
                # Token decryption failure is recorded as "no context", not an exception
                bundle.no_context_providers.append(_display_name(provider_name))
                continue

        try:
            citations, empty = await provider_fn(token, user_id)
        except Exception:
            bundle.no_context_providers.append(_display_name(provider_name))
            continue

        if provider_name == "google_calendar":
            bundle.calendar = citations
        elif provider_name == "gmail":
            bundle.email = citations
        elif provider_name == "purchase_history":
            bundle.purchase_history = citations

        if empty:
            bundle.no_context_providers.append(_display_name(provider_name))

    # Page context from the browser extension
    if page_context:
        if title := page_context.get("page_title"):
            bundle.page_context.append(Citation("browser_dom", f"Page title: {title}"))
        if amount := page_context.get("amount"):
            bundle.page_context.append(
                Citation(
                    "browser_dom",
                    f"Checkout amount: {amount} {page_context.get('currency', '')}".strip(),
                )
            )
        if item := page_context.get("item"):
            bundle.page_context.append(Citation("browser_dom", f"Item: {item}"))
        if banner_days := page_context.get("urgency_banner_age_days"):
            bundle.page_context.append(
                Citation(
                    "browser_dom",
                    f"Urgency banner first observed {banner_days} days ago — not actually new.",
                )
            )
    else:
        bundle.no_context_providers.append("browser_dom")

    return bundle


def bundle_to_agent_context(bundle: ContextBundle) -> str:
    """Render a context bundle as a single string the agent prompts can reference."""
    parts: list[str] = []
    if bundle.stated_values:
        parts.append("Stated values:\n- " + "\n- ".join(bundle.stated_values))
    if bundle.calendar:
        parts.append(
            "Calendar signals:\n- " + "\n- ".join(f"{c.source}: {c.detail}" for c in bundle.calendar)
        )
    if bundle.email:
        parts.append(
            "Email signals:\n- " + "\n- ".join(f"{c.source}: {c.detail}" for c in bundle.email)
        )
    if bundle.purchase_history:
        parts.append(
            "Purchase history:\n- "
            + "\n- ".join(f"{c.source}: {c.detail}" for c in bundle.purchase_history)
        )
    if bundle.page_context:
        parts.append(
            "Page context (the intercepted action):\n- "
            + "\n- ".join(f"{c.source}: {c.detail}" for c in bundle.page_context)
        )
    if bundle.no_context_providers:
        parts.append("Providers with no context available: " + ", ".join(bundle.no_context_providers))
    return "\n\n".join(parts) if parts else "No context available for this decision."


def _display_name(provider: str) -> str:
    return {
        "google_calendar": "calendar",
        "gmail": "email",
        "purchase_history": "purchase_history",
    }.get(provider, provider)
