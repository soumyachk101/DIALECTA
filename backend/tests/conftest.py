"""Pytest fixtures.

Uses an in-memory SQLite DB (via aiosqlite) for fast hermetic tests.
Postgres-specific types (UUID, JSONB, BYTEA) are emulated on SQLite.
Postgres-specific server defaults (`gen_random_uuid()`, `func.now()`) are
swapped for client-side Python defaults so SQLite can satisfy them.
"""
import os
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import pytest_asyncio

# Configure settings BEFORE importing the app
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("USE_DEMO_FALLBACK", "true")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("TOKEN_ENCRYPTION_KEY", "test-only-key-not-real")

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.sqlite.base import SQLiteDialect
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.types import JSON, LargeBinary, TypeDecorator

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


# Monkey-patch column types AND server defaults on already-imported models so
# SQLite can satisfy them without invoking Postgres-only `gen_random_uuid()` /
# `func.now()` server functions.
import sqlalchemy as _sa
from sqlalchemy.dialects.postgresql import BYTEA as _PGBYTEA
from sqlalchemy.dialects.postgresql import JSONB as _PGJSONB
from sqlalchemy.dialects.postgresql import UUID as _PGUUID
from sqlalchemy.sql.schema import ColumnDefault


def _uuid_default():
    return str(uuid.uuid4())


def _now_default():
    return datetime.now(UTC)


def _patch_columns():
    for table in Base.metadata.tables.values():
        for col in table.columns:
            # Type patches — Postgres → SQLite friendly equivalents
            if isinstance(col.type, _PGUUID):
                col.type = _SQLiteUUID()
            elif isinstance(col.type, _PGJSONB):
                col.type = _JSONBCompat()
            elif isinstance(col.type, _PGBYTEA):
                col.type = _BYTEACompat()
            # Server-default patches — drop Postgres-only `gen_random_uuid()`
            # / `now()` server functions and replace with client-side defaults.
            sd = col.server_default
            if sd is None:
                continue
            arg = getattr(sd, "arg", None)
            arg_text = str(arg) if arg is not None else ""
            if "gen_random_uuid" in arg_text:
                col.server_default = None
                col.default = ColumnDefault(_uuid_default, for_update=False)
            elif "now()" in arg_text and isinstance(col.type, _sa.DateTime):
                col.server_default = None
                col.default = ColumnDefault(_now_default, for_update=False)


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
