"""Tests for the orchestrator's blocking path + DB persistence."""
import uuid

import pytest
from sqlalchemy import select

from app.agents.orchestrator import run_debate_blocking
from app.models.orm import (
    ConnectedAccount,
    DebateSession,
    DebateTurn,
    User,
    UserValue,
)
from app.schemas.api import WSMessage
from app.services.crypto import encrypt_token

DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
DEMO_TOKEN = encrypt_token("demo-token-not-real")


@pytest.mark.asyncio
async def test_run_debate_creates_5_turns(db_session):
    """Orchestrator should produce 4 agent turns + 1 moderator turn."""
    # Seed: a user with a connected account + stated value
    user = User(id=DEMO_USER_ID, email="t@dialecta.local", display_name="Test")
    db_session.add(user)
    db_session.add(ConnectedAccount(
        user_id=DEMO_USER_ID, provider="google_calendar", scope="readonly",
        encrypted_token=DEMO_TOKEN,
    ))
    db_session.add(UserValue(user_id=DEMO_USER_ID, statement="save for trip", priority=10))
    session = DebateSession(
        user_id=DEMO_USER_ID, trigger_type="manual",
        decision_summary="Buy chair?",
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    events: list[WSMessage] = []
    async for msg in run_debate_blocking(
        session=db_session, session_id=session.id,
        decision="Buy chair?", user_id=DEMO_USER_ID, page_context=None,
    ):
        events.append(msg)

    kinds = [e.type for e in events]
    assert "context_loaded" in kinds
    assert kinds.count("agent_turn") == 4
    assert "moderator_turn" in kinds
    assert "done" in kinds

    # Verify DB persistence
    turns = (await db_session.execute(
        select(DebateTurn).where(DebateTurn.session_id == session.id).order_by(DebateTurn.turn_order)
    )).scalars().all()
    assert len(turns) == 5
    agents = [t.agent for t in turns]
    assert agents == ["optimist", "skeptic", "analyst", "ethicist", "moderator"]


@pytest.mark.asyncio
async def test_session_marked_completed(db_session):
    user = User(id=DEMO_USER_ID, email="t@dialecta.local")
    db_session.add(user)
    session = DebateSession(
        user_id=DEMO_USER_ID, trigger_type="checkout",
        decision_summary="Buy expensive thing?",
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    async for _ in run_debate_blocking(
        session=db_session, session_id=session.id,
        decision="Buy expensive thing?", user_id=DEMO_USER_ID, page_context=None,
    ):
        pass

    await db_session.refresh(session)
    assert session.status == "completed"


@pytest.mark.asyncio
async def test_turn_order_is_stable(db_session):
    """TURN_ORDER must be optimistic → skeptic → analyst → ethicist → moderator."""
    user = User(id=DEMO_USER_ID, email="t@dialecta.local")
    db_session.add(user)
    session = DebateSession(
        user_id=DEMO_USER_ID, trigger_type="manual", decision_summary="test"
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    turn_order_seen: list[str] = []
    async for msg in run_debate_blocking(
        session=db_session, session_id=session.id,
        decision="test", user_id=DEMO_USER_ID, page_context=None,
    ):
        if msg.type in ("agent_turn", "moderator_turn") and msg.agent:
            turn_order_seen.append(msg.agent)

    assert turn_order_seen == ["optimist", "skeptic", "analyst", "ethicist", "moderator"]
