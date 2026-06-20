# DIALECTA

> Don't think alone. Carry a team.

A real-time, multimodal, adversarial multi-agent system — a *cognitive parliament* in your pocket. Four AI agents (Optimist, Skeptic, Analyst, Ethicist) debate your decisions as you make them, catching cognitive biases before they cost you.

Built for the 48-hour hackathon. See `Docs/` for the full PRD, TRD, architecture, schema, UI/UX spec, and AI agent instructions.

## Repository layout

```
DIALECTA/
├── Docs/                # PRD, TRD, Architecture, Schema, UI/UX, App Flow, AI instructions
├── design-system/       # UI/UX Pro Max generated design tokens + page overrides
├── backend/             # FastAPI + LangGraph-style orchestrator + MCP context layer + Postgres
├── extension/           # Browser extension (MV3) — intercepts checkout/send, opens debate
├── dashboard/           # Next.js 15 dashboard — Decision Log + radial debate view + Settings
└── docker-compose.yml   # Local Postgres for the backend
```

## Quick start (3 terminals)

```bash
# 1. Database
docker compose up -d

# 2. Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env   # leave API keys empty to use the demo fallback turns
uvicorn app.main:app --reload --port 8000
python -m scripts.seed_demo_user   # one-time demo data

# 3. Dashboard
cd ../dashboard
npm install
npm run dev            # http://localhost:3000

# 4. Extension
cd ../extension
npm install
npm run build          # outputs to dist/
# → chrome://extensions → enable Developer mode → "Load unpacked" → select extension/dist
```

## How the system hangs together

```
[Browser extension]                [Dashboard]            [Voice client]
        │                               │                       │
        └──────────────┬────────────────┴───────────┬───────────┘
                       ▼                            ▼
            POST /v1/sessions          GET /v1/decisions
                       │
                       ▼
              [FastAPI + LangGraph orchestrator]
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   MCP Context    Agent nodes     Moderator
   (calendar,     (parallel,      synthesis
    email, DOM,   Groq+Claude)
    documents)
                       │
                       ▼
              WS /v1/sessions/{id}/stream  →  radial debate view
```

## Demo fallback mode

If you start the backend without `ANTHROPIC_API_KEY` and `GROQ_API_KEY`, all agent turns use scripted responses (the same ones documented in `Docs/AI_INSTRUCTIONS.md` §5). The full pipeline — context fetch, parallel orchestration, WebSocket streaming, persistence — still runs end-to-end, so the demo is fully reproducible.

## Status

🚧 Active hackathon build. See `Docs/PRD.md` §3 for goals and §10 for risks.
