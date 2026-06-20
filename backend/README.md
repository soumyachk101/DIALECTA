# DIALECTA — Backend

FastAPI service implementing the Cognitive Parliament orchestrator with per-token LLM streaming.

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env       # leave keys empty for demo fallback
alembic upgrade head       # apply schema
uvicorn app.main:app --port 8000
python -m scripts.seed_demo_user   # one-time demo data
```

## Quick start (Docker)

```bash
docker build -t dialecta-backend .
docker run --rm -p 8000:8000 --env-file .env dialecta-backend
# The container runs `alembic upgrade head` on boot
```

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/v1/sessions` | Create a session. `?stream=true` runs the debate synchronously and returns the full transcript |
| `GET`  | `/v1/sessions/{id}` | Session detail |
| `GET`  | `/v1/sessions/{id}/turns` | Full debate transcript |
| `POST` | `/v1/sessions/{id}/resolve` | Record the user's final outcome |
| `GET`  | `/v1/decisions` | Paginated Decision Log |
| `GET`  | `/v1/decisions/{id}` | Full transcript + outcome |
| `WS`   | `/v1/sessions/{id}/stream` | **Live** per-token debate stream |
| `GET`  | `/health` | Liveness + provider status |

## Streaming protocol

The WebSocket path emits per-token events so the client can render the debate in real time:

```json
{"type": "context_loaded", "session_id": "..."}
{"type": "token", "agent": "optimist", "delta": "Your last", "turn_order": 1}
{"type": "token", "agent": "optimist", "delta": " two well-timed", "turn_order": 1}
...
{"type": "agent_done", "agent": "optimist", "turn_order": 1, "turn": {...}}
...
{"type": "moderator_token", "delta": "Strongest", "turn_order": 5}
{"type": "moderator_done", "turn_order": 5, "turn": {...}}
{"type": "done", "session_id": "..."}
```

## Tests

```bash
pytest                              # runner + orchestrator + privacy suite
ruff check app tests                # lint
```

The suite uses SQLite in-memory (with Postgres UUID/JSONB/BYTEA emulated) for hermetic tests. Real Postgres is only required for production.

## Layout

```
backend/
├── app/
│   ├── main.py                # FastAPI entry, lifespan, /health
│   ├── config.py              # pydantic-settings
│   ├── api/routes.py          # REST + WebSocket
│   ├── agents/
│   │   ├── prompts.py         # Persona system prompts (copy of AI_INSTRUCTIONS.md)
│   │   ├── runner.py          # LLM runners (Groq + Claude) with per-token streaming
│   │   └── orchestrator.py    # State machine: context → parallel debate → moderator → stream
│   ├── mcp/
│   │   ├── context.py         # MCP context layer (privacy boundary)
│   │   └── providers/         # Real Google Calendar + Gmail provider implementations
│   ├── models/orm.py          # SQLAlchemy models
│   ├── schemas/api.py         # Pydantic request/response/WS schemas
│   ├── services/crypto.py     # Fernet-based OAuth token encryption
│   └── db/session.py          # Async engine + session factory
├── alembic/                   # DB migrations
├── scripts/                   # seed_demo_user.py
└── tests/                     # pytest suite
```

## Demo fallback

If `ANTHROPIC_API_KEY` and `GROQ_API_KEY` are both empty (or `USE_DEMO_FALLBACK=true`), the runners emit the scripted demo turns from `app/agents/runner.py:42` (visible in `Docs/AI_INSTRUCTIONS.md` §5). Set `USE_DEMO_FALLBACK=false` to surface live LLM errors instead of falling back.
