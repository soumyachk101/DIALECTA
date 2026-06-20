"""
REST + WebSocket routes. Mirrors TRD.md §5 contracts.

Two execution paths:
  - REST: blocking (one POST creates + executes synchronously for the demo)
  - WS:   streaming per-token events (the real-time path)

The REST path also has a `?stream=false` mode that returns the full debate
turn-by-turn after it completes (used by the dashboard "replay" view).
"""
from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import run_debate, run_debate_blocking
from app.db.session import SessionLocal, get_session
from app.models.orm import DebateSession, DebateTurn, Decision
from app.schemas.api import (
    CreateSessionRequest,
    DecisionLogItem,
    DecisionResponse,
    ResolveRequest,
    SessionResponse,
    TurnResponse,
)

router = APIRouter(prefix="/v1")


# ---- Sessions ----

@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(
    payload: CreateSessionRequest,
    stream: bool = Query(False, description="If true, run the debate synchronously and return the full transcript"),
    session: AsyncSession = Depends(get_session),
) -> SessionResponse | dict:
    db_session = DebateSession(
        user_id=payload.user_id,
        trigger_type=payload.trigger_type,
        decision_summary=payload.decision_summary,
    )
    session.add(db_session)
    await session.commit()
    await session.refresh(db_session)

    if not stream:
        return SessionResponse(
            id=db_session.id, user_id=db_session.user_id, trigger_type=db_session.trigger_type,
            decision_summary=db_session.decision_summary, status=db_session.status,
            created_at=db_session.created_at,
        )

    # Synchronous replay path — runs the debate, persists, returns turns
    turns: list[dict] = []
    async for msg in run_debate_blocking(
        session=session, session_id=db_session.id, decision=db_session.decision_summary,
        user_id=db_session.user_id, page_context=payload.page_context,
    ):
        if msg.type == "agent_turn":
            turns.append({"agent": msg.agent, "message": msg.message, "citations": msg.citations or [],
                          "confidence": msg.confidence, "no_context_found": msg.no_context_found,
                          "turn_order": msg.turn_order})
        elif msg.type == "moderator_turn":
            turns.append({"agent": "moderator", "message": msg.message, "citations": msg.citations or [],
                          "confidence": msg.confidence, "no_context_found": msg.no_context_found,
                          "turn_order": msg.turn_order})

    return {
        "session": SessionResponse(
            id=db_session.id, user_id=db_session.user_id, trigger_type=db_session.trigger_type,
            decision_summary=db_session.decision_summary, status=db_session.status,
            created_at=db_session.created_at,
        ).model_dump(mode="json"),
        "turns": turns,
    }


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session_detail(session_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> SessionResponse:
    db_session = await session.get(DebateSession, session_id)
    if not db_session:
        raise HTTPException(404, "session not found")
    return SessionResponse(
        id=db_session.id, user_id=db_session.user_id, trigger_type=db_session.trigger_type,
        decision_summary=db_session.decision_summary, status=db_session.status,
        created_at=db_session.created_at,
    )


@router.get("/sessions/{session_id}/turns", response_model=list[TurnResponse])
async def get_session_turns(session_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> list[TurnResponse]:
    result = await session.execute(
        select(DebateTurn).where(DebateTurn.session_id == session_id).order_by(DebateTurn.turn_order)
    )
    return [
        TurnResponse(
            agent=t.agent, message=t.message, citations=t.citations or [],
            confidence=float(t.confidence) if t.confidence is not None else None,
            no_context_found=t.no_context_found, turn_order=t.turn_order,
        )
        for t in result.scalars().all()
    ]


@router.post("/sessions/{session_id}/resolve", response_model=DecisionResponse)
async def resolve_session(session_id: uuid.UUID, payload: ResolveRequest, session: AsyncSession = Depends(get_session)) -> DecisionResponse:
    db_session = await session.get(DebateSession, session_id)
    if not db_session:
        raise HTTPException(404, "session not found")

    mod_q = await session.execute(
        select(DebateTurn).where(DebateTurn.session_id == session_id, DebateTurn.agent == "moderator")
    )
    moderator_turn = mod_q.scalar_one_or_none()
    moderator_summary = moderator_turn.message if moderator_turn else None

    decision = Decision(
        session_id=session_id, outcome=payload.outcome,
        moderator_summary=moderator_summary, user_reported_result=payload.user_reported_result,
    )
    session.add(decision)
    db_session.status = "completed"
    await session.commit()
    await session.refresh(decision)
    return DecisionResponse(
        id=decision.id, session_id=decision.session_id, outcome=decision.outcome,
        moderator_summary=decision.moderator_summary, user_reported_result=decision.user_reported_result,
        resolved_at=decision.resolved_at,
    )


# ---- Decision Log ----

@router.get("/decisions", response_model=list[DecisionLogItem])
async def list_decisions(limit: int = 50, session: AsyncSession = Depends(get_session)) -> list[DecisionLogItem]:
    result = await session.execute(
        select(DebateSession).order_by(desc(DebateSession.created_at)).limit(limit)
    )
    items: list[DecisionLogItem] = []
    for s in result.scalars().all():
        d = await session.execute(select(Decision).where(Decision.session_id == s.id))
        decision = d.scalar_one_or_none()
        items.append(DecisionLogItem(
            session_id=s.id, decision_summary=s.decision_summary,
            outcome=decision.outcome if decision else None,
            trigger_type=s.trigger_type, created_at=s.created_at,
            moderator_summary=decision.moderator_summary if decision else None,
        ))
    return items


@router.get("/decisions/{session_id}")
async def get_decision_detail(session_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> dict:
    db_session = await session.get(DebateSession, session_id)
    if not db_session:
        raise HTTPException(404, "decision not found")
    turns_q = await session.execute(
        select(DebateTurn).where(DebateTurn.session_id == session_id).order_by(DebateTurn.turn_order)
    )
    decision_q = await session.execute(select(Decision).where(Decision.session_id == session_id))
    decision = decision_q.scalar_one_or_none()
    return {
        "session": SessionResponse(
            id=db_session.id, user_id=db_session.user_id, trigger_type=db_session.trigger_type,
            decision_summary=db_session.decision_summary, status=db_session.status,
            created_at=db_session.created_at,
        ).model_dump(mode="json"),
        "turns": [
            TurnResponse(
                agent=t.agent, message=t.message, citations=t.citations or [],
                confidence=float(t.confidence) if t.confidence is not None else None,
                no_context_found=t.no_context_found, turn_order=t.turn_order,
            ).model_dump(mode="json")
            for t in turns_q.scalars().all()
        ],
        "decision": DecisionResponse(
            id=decision.id, session_id=decision.session_id, outcome=decision.outcome,
            moderator_summary=decision.moderator_summary, user_reported_result=decision.user_reported_result,
            resolved_at=decision.resolved_at,
        ).model_dump(mode="json") if decision else None,
    }


# ---- WebSocket streaming ----

async def _stream_to_ws(ws: WebSocket, events: AsyncIterator[dict]) -> None:
    async for ev in events:
        await ws.send_text(json.dumps(ev, default=str))


@router.websocket("/sessions/{session_id}/stream")
async def stream_session(ws: WebSocket, session_id: uuid.UUID) -> None:
    await ws.accept()
    async with SessionLocal() as session:
        db_session = await session.get(DebateSession, session_id)
        if not db_session:
            await ws.send_text(json.dumps({"type": "error", "detail": "session not found"}))
            await ws.close()
            return

        try:
            events = run_debate(
                session=session, session_id=session_id,
                decision=db_session.decision_summary, user_id=db_session.user_id,
                page_context=None,
            )
            await _stream_to_ws(ws, events)
        except WebSocketDisconnect:
            return
        except Exception as e:
            await ws.send_text(json.dumps({"type": "error", "detail": str(e)}))
            await ws.close()
