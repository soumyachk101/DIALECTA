"""
Orchestrator — implements the ARCHITECTURE.md §3 state machine.
  Intake → Context Fetch → Parallel Agent Debate (per-token stream) → Moderator Synthesis → Stream + Persist

The WebSocket path yields incremental token events so the client can render
the debate in real time, hitting the <1.5s first-token target per TRD §4.
"""
from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.runner import stream_agent
from app.mcp.context import bundle_to_agent_context, gather_context
from app.models.orm import DebateSession, DebateTurn
from app.schemas.api import WSMessage

# Display order — fixed so the UI can render deterministically.
TURN_ORDER = ["optimist", "skeptic", "analyst", "ethicist"]


async def run_debate(
    session: AsyncSession,
    session_id: uuid.UUID,
    decision: str,
    user_id: uuid.UUID,
    page_context: dict | None,
) -> AsyncIterator[dict]:
    """
    Yields events for the client. Event types:
      {"type": "context_loaded", ...}
      {"type": "token", "agent": str, "delta": str, "turn_order": int}   (many per agent)
      {"type": "agent_done", "agent": str, "turn_order": int, "turn": {...}}
      {"type": "moderator_token", "delta": str}
      {"type": "moderator_done", "turn": {...}}
      {"type": "done"}
    """
    # 1. Context fetch
    bundle = await gather_context(session, user_id, page_context)
    context_str = bundle_to_agent_context(bundle)

    yield {"type": "context_loaded", "session_id": str(session_id), "detail": "context ready"}

    # 2. Parallel agent debate — stream each agent's tokens
    async def stream_one(agent: str, order: int) -> tuple[str, int, dict]:
        """Collect all events for one agent, return (agent, order, final_turn)."""
        final_turn: dict | None = None
        async for ev in stream_agent(agent, decision, context_str):
            if ev["type"] == "done":
                final_turn = ev["turn"]
            # Re-emit to the outer caller with agent/order stamped on
            yield_event = {**ev, "agent": agent, "turn_order": order}
            if ev["type"] == "token":
                yield_event["type"] = "token"
            yield yield_event
        if final_turn is None:
            final_turn = {
                "message": "[no output]",
                "citations": [],
                "confidence": 0.3,
                "no_context_found": True,
            }
        return agent, order, final_turn

    # Use a queue + tasks to interleave tokens from all 4 agents in real time
    queue: asyncio.Queue[tuple[str, str, dict]] = asyncio.Queue()
    tasks: list[asyncio.Task] = []

    async def runner(agent: str, order: int) -> None:
        async for ev in stream_agent(agent, decision, context_str):
            await queue.put(("event", agent, {**ev, "agent": agent, "turn_order": order}))
        await queue.put(("done", agent, {"agent": agent, "turn_order": order}))

    for i, agent in enumerate(TURN_ORDER, start=1):
        tasks.append(asyncio.create_task(runner(agent, i)))

    persisted: list[dict] = [None] * 4  # one slot per agent
    completed_agents: set[str] = set()

    while len(completed_agents) < 4:
        kind, agent, payload = await queue.get()
        if kind == "event":
            yield payload  # token or agent_done
            if payload.get("type") == "agent_done":
                # Persist this agent's final turn
                turn = payload["turn"]
                order = payload["turn_order"]
                persisted[order - 1] = {"agent": agent, **turn, "turn_order": order}
                db_turn = DebateTurn(
                    session_id=session_id, agent=agent, message=turn["message"],
                    citations=turn.get("citations", []), confidence=turn.get("confidence"),
                    no_context_found=turn.get("no_context_found", False), turn_order=order,
                )
                session.add(db_turn)
                await session.flush()
        else:  # kind == "done"
            completed_agents.add(agent)

    await asyncio.gather(*tasks)
    # Drop the None placeholders
    persisted_turns = [t for t in persisted if t is not None]

    # 3. Moderator synthesis
    moderator_order = len(persisted_turns) + 1
    final_turn: dict | None = None
    async for ev in stream_agent("moderator", decision, context="", other_turns=persisted_turns):
        if ev["type"] == "token":
            yield {**ev, "type": "moderator_token"}
        elif ev["type"] == "done":
            final_turn = ev["turn"]
            yield {
                "type": "moderator_done",
                "turn_order": moderator_order,
                "turn": final_turn,
            }

    if final_turn is None:
        final_turn = {
            "message": "[moderator unavailable]",
            "citations": [],
            "confidence": 0.3,
            "no_context_found": True,
        }

    db_mod = DebateTurn(
        session_id=session_id, agent="moderator", message=final_turn["message"],
        citations=final_turn.get("citations", []), confidence=final_turn.get("confidence"),
        no_context_found=final_turn.get("no_context_found", False),
        turn_order=moderator_order,
    )
    session.add(db_mod)

    # 4. Mark session complete
    db_session = await session.get(DebateSession, session_id)
    if db_session:
        db_session.status = "completed"
    await session.commit()

    yield {"type": "done", "session_id": str(session_id)}


# ---- Legacy non-streaming run_debate_blocking — used by tests + API fallback ----

async def run_debate_blocking(
    session: AsyncSession,
    session_id: uuid.UUID,
    decision: str,
    user_id: uuid.UUID,
    page_context: dict | None,
) -> AsyncIterator[WSMessage]:
    """Non-streaming path. Yields WSMessage envelopes (1 per turn, not per token).
    Used by tests and as a fallback when streaming is undesirable."""
    from app.agents.runner import run_agents_parallel, run_moderator

    bundle = await gather_context(session, user_id, page_context)
    context_str = bundle_to_agent_context(bundle)

    yield WSMessage(type="context_loaded", session_id=session_id, detail="context ready")

    raw_turns = await run_agents_parallel(decision, context_str)
    by_agent = dict(zip(TURN_ORDER, raw_turns, strict=False))

    order = 0
    persisted_turns: list[dict] = []
    for agent_name in TURN_ORDER:
        order += 1
        turn = by_agent[agent_name]
        persisted_turns.append({"agent": agent_name, **turn, "turn_order": order})

        db_turn = DebateTurn(
            session_id=session_id, agent=agent_name, message=turn["message"],
            citations=turn["citations"], confidence=turn["confidence"],
            no_context_found=turn["no_context_found"], turn_order=order,
        )
        session.add(db_turn)
        await session.flush()

        yield WSMessage(
            type="agent_turn", session_id=session_id, agent=agent_name,
            message=turn["message"], citations=turn["citations"],
            confidence=turn["confidence"], no_context_found=turn["no_context_found"],
            turn_order=order,
        )

    moderator = await run_moderator(decision, persisted_turns)
    order += 1
    db_mod = DebateTurn(
        session_id=session_id, agent="moderator", message=moderator["message"],
        citations=moderator["citations"], confidence=moderator["confidence"],
        no_context_found=moderator["no_context_found"], turn_order=order,
    )
    session.add(db_mod)

    db_session = await session.get(DebateSession, session_id)
    if db_session:
        db_session.status = "completed"
    await session.commit()

    yield WSMessage(
        type="moderator_turn", session_id=session_id, agent="moderator",
        message=moderator["message"], citations=moderator["citations"],
        confidence=moderator["confidence"], no_context_found=moderator["no_context_found"],
        turn_order=order,
    )
    yield WSMessage(type="done", session_id=session_id)
