"""SQLAlchemy ORM models — mirrors BACKEND_SCHEMA.md exactly."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import BYTEA, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    accounts: Mapped[list[ConnectedAccount]] = relationship(back_populates="user", cascade="all, delete-orphan")
    values: Mapped[list[UserValue]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[list[DebateSession]] = relationship(back_populates="user", cascade="all, delete-orphan")


class ConnectedAccount(Base):
    __tablename__ = "connected_accounts"
    __table_args__ = (UniqueConstraint("user_id", "provider", name="uq_accounts_user_provider"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    scope: Mapped[str] = mapped_column(Text, nullable=False)
    encrypted_token: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    connected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped[User] = relationship(back_populates="accounts")


class UserValue(Base):
    __tablename__ = "user_values"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped[User] = relationship(back_populates="values")


class DebateSession(Base):
    __tablename__ = "debate_sessions"
    __table_args__ = (CheckConstraint("trigger_type IN ('checkout','voice','manual')", name="ck_sessions_trigger"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    trigger_type: Mapped[str] = mapped_column(Text, nullable=False)
    decision_summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="in_progress")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped[User] = relationship(back_populates="sessions")
    turns: Mapped[list[DebateTurn]] = relationship(back_populates="session", cascade="all, delete-orphan", order_by="DebateTurn.turn_order")
    decision: Mapped[Decision | None] = relationship(back_populates="session", cascade="all, delete-orphan", uselist=False)


class DebateTurn(Base):
    __tablename__ = "debate_turns"
    __table_args__ = (CheckConstraint("agent IN ('optimist','skeptic','analyst','ethicist','moderator')", name="ck_turns_agent"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("debate_sessions.id", ondelete="CASCADE"), nullable=False)
    agent: Mapped[str] = mapped_column(Text, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    citations: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    confidence: Mapped[float | None] = mapped_column(Numeric(3, 2))
    no_context_found: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    turn_order: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session: Mapped[DebateSession] = relationship(back_populates="turns")


class Decision(Base):
    __tablename__ = "decisions"
    __table_args__ = (CheckConstraint("outcome IN ('accepted','overridden','ignored')", name="ck_decisions_outcome"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("debate_sessions.id", ondelete="CASCADE"), unique=True, nullable=False)
    outcome: Mapped[str] = mapped_column(Text, nullable=False)
    moderator_summary: Mapped[str | None] = mapped_column(Text)
    user_reported_result: Mapped[str | None] = mapped_column(Text)
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session: Mapped[DebateSession] = relationship(back_populates="decision")
