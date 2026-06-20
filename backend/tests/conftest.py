"""Pytest fixtures.

Uses an in-memory SQLite DB (via aiosqlite) for fast hermetic tests.
Postgres-specific types (UUID, JSONB, BYTEA) are emulated on SQLite.
"""
import asyncio
import os
import uuid
from typing import AsyncIterator

import pytest
import pytest_asyncio


# Configure settings BEFORE importing the app
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("USE_DEMO_FALLBACK", "true")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("TOKEN_ENCRYPTION_KEY", "test-only-key-not-real")

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.types import JSON, LargeBinary, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB, BYTEA, UUID
from sqlalchemy.dialects.sqlite.base import SQLiteDialect

from app.db.session import Base
from app.models import orm  # noqa: F401


# Patch Postgres types to SQLite-friendly equivalents at import time so that
# the model definitions work on SQLite without changing the source.
class _JSONBCompat(JSON):
    pass


class _BYTEACompat(LargeBinary):
    pass


class _UUIDCompat(TypeDecorator):
    impl = LargeBinary
    cache_ok = True

    def __init__(self, as_uuid: bool = True):
        super().__init__()
        self.as_uuid = as_uuid

    def load_dialect_impl(self, dialect):
        if isinstance(dialect, SQLiteDialect):
            return dialect.type_descriptor(_SQLiteUUID())
        return dialect.type_descriptor(UUID(as_uuid=self.as_uuid))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(dialect, SQLiteDialect):
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(dialect, SQLiteDialect):
            return uuid.UUID(value)
        return value


from sqlalchemy import String


class _SQLiteUUID(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return str(value) if value is not None else None

    def process_result_value(self, value, dialect):
        return uuid.UUID(value) if value is not None else None


# Monkey-patch column types on already-imported models (Postgres → SQLite compat)
from sqlalchemy import Boolean, CheckConstraint, Column as _Col
from sqlalchemy.dialects.postgresql import UUID as _PGUUID, JSONB as _PGJSONB, BYTEA as _PGBYTEA
import sqlalchemy as _sa


def _patch_columns():
    for table in Base.metadata.tables.values():
        for col in table.columns:
            if isinstance(col.type, _PGUUID):
                col.type = _SQLiteUUID()
            elif isinstance(col.type, _PGJSONB):
                col.type = _JSONBCompat()
            elif isinstance(col.type, _PGBYTEA):
                col.type = _BYTEACompat()


_patch_columns()


@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def db_session(session_factory) -> AsyncIterator[AsyncSession]:
    async with session_factory() as s:
        yield s
