"""Privacy boundary tests (ARCHITECTURE.md §5)."""
import uuid

import pytest

from app.mcp.context import Citation, gather_context, bundle_to_agent_context
from app.models.orm import ConnectedAccount, User, UserValue
from app.services.crypto import decrypt_token, encrypt_token


DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.mark.asyncio
async def test_gather_context_returns_structured_citations(db_session):
    user = User(id=DEMO_USER_ID, email="t@dialecta.local")
    db_session.add(user)
    db_session.add(ConnectedAccount(
        user_id=DEMO_USER_ID, provider="google_calendar", scope="readonly",
        encrypted_token=encrypt_token("real-looking-token"),
    ))
    db_session.add(UserValue(user_id=DEMO_USER_ID, statement="save for trip", priority=10))
    await db_session.commit()

    bundle = await gather_context(db_session, DEMO_USER_ID, page_context={"item": "chair", "amount": "4999"})
    assert isinstance(bundle.calendar, list)
    assert isinstance(bundle.email, list)
    assert isinstance(bundle.purchase_history, list)
    assert all(isinstance(c, Citation) for c in bundle.calendar + bundle.email + bundle.purchase_history)


@pytest.mark.asyncio
async def test_no_raw_payloads_in_context_string(db_session):
    """The context string passed to agents must not contain raw token bytes."""
    user = User(id=DEMO_USER_ID, email="t@dialecta.local")
    db_session.add(user)
    raw_token = "ya29.a0Af-super-secret-token"
    db_session.add(ConnectedAccount(
        user_id=DEMO_USER_ID, provider="google_calendar", scope="readonly",
        encrypted_token=encrypt_token(raw_token),
    ))
    await db_session.commit()

    bundle = await gather_context(db_session, DEMO_USER_ID)
    ctx = bundle_to_agent_context(bundle)
    assert raw_token not in ctx
    # The encrypted form is also a Fernet token (starts with gAAAAA) — that should not leak either
    assert "gAAAAA" not in ctx


@pytest.mark.asyncio
async def test_missing_user_values_recorded_as_no_context(db_session):
    user = User(id=DEMO_USER_ID, email="t@dialecta.local")
    db_session.add(user)
    await db_session.commit()

    bundle = await gather_context(db_session, DEMO_USER_ID, page_context=None)
    assert bundle.stated_values == []
    assert "browser_dom" in bundle.no_context_providers


@pytest.mark.asyncio
async def test_token_decryption_roundtrip():
    """encrypt_token + decrypt_token is the only path to recover the raw token."""
    plaintext = "ya29.this-is-an-oauth-refresh-token"
    ciphertext = encrypt_token(plaintext)
    assert plaintext.encode() != ciphertext
    assert decrypt_token(ciphertext) == plaintext
