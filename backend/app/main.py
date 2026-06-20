"""FastAPI entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings
from app.db.session import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.environment == "development":
        # Dev convenience: auto-create tables. In production use Alembic migrations.
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="DIALECTA",
    version="0.1.0",
    description="Real-time adversarial multi-agent decision debate.",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(router)


@app.get("/health")
async def health() -> dict:
    """Health check — useful for Railway / monitoring."""
    settings = get_settings()
    has_anthropic = bool(settings.anthropic_api_key)
    has_groq = bool(settings.groq_api_key)
    return {
        "status": "ok",
        "service": "dialecta-backend",
        "version": app.version,
        "environment": settings.environment,
        "llm_providers": {
            "anthropic": "configured" if has_anthropic else "missing",
            "groq": "configured" if has_groq else "missing",
        },
        "demo_fallback": settings.use_demo_fallback and not (has_anthropic and has_groq),
    }
