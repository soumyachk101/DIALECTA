# DIALECTA — Backend

FastAPI service implementing the Cognitive Parliament orchestrator.

## Quick start

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e .

# 1. Start Postgres (docker-compose at repo root)
# 2. Copy .env.example to .env (leave keys empty for demo fallback)
cp .env.example .env

# 3. Run the server
uvicorn app.main:app --reload --port 8000

# 4. (Optional) seed a demo user with stated values + connected accounts
python -m scripts.seed_demo_user
```

The app boots with the tables auto-created (development mode). For production use Alembic.

## Endpoints

- `POST   /v1/sessions` — create a session
- `GET    /v1/sessions/{id}` — session detail
- `GET    /v1/sessions/{id}/turns` — full debate transcript
- `POST   /v1/sessions/{id}/resolve` — record the user's final outcome
- `GET    /v1/decisions` — paginated decision log
- `GET    /v1/decisions/{id}` — full transcript + outcome
- `WS     /v1/sessions/{id}/stream` — live debate stream
- `GET    /health`

## Demo fallback

If `ANTHROPIC_API_KEY` and `GROQ_API_KEY` are both empty, the system uses the scripted
demo turns from `app/agents/runner.py:42` (visible in `AI_INSTRUCTIONS.md` §5). Set
`USE_DEMO_FALLBACK=false` to disable the fallback and surface live LLM errors instead.
