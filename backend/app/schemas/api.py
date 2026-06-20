"""Pydantic schemas for the public API + WebSocket messages."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# ---------- Requests ----------

class CreateSessionRequest(BaseModel):
    user_id: uuid.UUID
    trigger_type: Literal["checkout", "voice", "manual"]
    decision_summary: str = Field(min_length=1, max_length=500)
    page_context: dict | None = None  # browser DOM, page title, amount, etc.


class ResolveRequest(BaseModel):
    outcome: Literal["accepted", "overridden", "ignored"]
    user_reported_result: str | None = None


# ---------- Responses ----------

class SessionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    trigger_type: str
    decision_summary: str
    status: str
    created_at: datetime


class DecisionResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    outcome: str
    moderator_summary: str | None
    user_reported_result: str | None
    resolved_at: datetime


class DecisionLogItem(BaseModel):
    session_id: uuid.UUID
    decision_summary: str
    outcome: str | None
    trigger_type: str
    created_at: datetime
    moderator_summary: str | None


class TurnResponse(BaseModel):
    agent: str
    message: str
    citations: list[dict]
    confidence: float | None
    no_context_found: bool
    turn_order: int


# ---------- WebSocket envelope ----------

class WSMessage(BaseModel):
    type: Literal["agent_turn", "moderator_turn", "context_loaded", "error", "done"]
    session_id: uuid.UUID | None = None
    agent: str | None = None
    message: str | None = None
    citations: list[dict] | None = None
    confidence: float | None = None
    no_context_found: bool | None = None
    turn_order: int | None = None
    detail: str | None = None
