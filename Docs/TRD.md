# DIALECTA — Technical Requirements Document (TRD)

## 1. System Overview

DIALECTA is a FastAPI backend orchestrating a LangGraph multi-agent debate, fed by MCP context servers, streamed over WebSocket to a browser extension and a lightweight Next.js dashboard. See `ARCHITECTURE.md` for the full diagram.

## 2. Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Backend API | FastAPI (Python) | Async-native, pairs cleanly with LangGraph, matches existing stack |
| Orchestration | LangGraph | Explicit state machine for parallel agent debate + synthesis step |
| Agent Framework (alt) | CrewAI | Drop-in alternative if LangGraph state management feels heavy under time pressure |
| LLM Providers | Claude (Anthropic), Groq (Llama 3.3 70B), Gemini | Claude for Ethicist/Moderator reasoning quality, Groq for low-latency Optimist/Skeptic/Analyst turns, Gemini as vision fallback |
| Speech-to-Text | Whisper (streaming) | Voice query mode |
| Real-time transport | WebSocket (FastAPI native) | Streams agent turns as they're generated |
| Context Integration | Custom MCP servers | Browser DOM, Calendar, Email, Documents |
| Database | PostgreSQL | Sessions, debates, decisions, user goals |
| Frontend (dashboard) | Next.js + TypeScript | Decision Log, settings, onboarding |
| Browser Extension | TypeScript (Manifest V3) | Checkout/send interception, intervention overlay |
| Deployment | Railway (backend + DB), Vercel (dashboard + extension build pipeline) | Matches existing deployment pattern, avoids Vercel's request size/time limits on the backend |

## 3. Functional Requirements

| ID | Requirement |
|---|---|
| FR-1 | System must detect a checkout-like DOM event on a demo page and trigger a debate session |
| FR-2 | System must accept a voice query, transcribe it, and trigger a debate session |
| FR-3 | System must fetch relevant context (calendar, email, purchase history) via MCP before agents respond |
| FR-4 | All 4 agents must run with shared context but independent reasoning, in parallel |
| FR-5 | A Moderator step must synthesize the 4 agent outputs into a single closing recommendation |
| FR-6 | All agent turns must stream to the client incrementally, not as one blocking response |
| FR-7 | Every debate must be persisted with its final user decision (accept / override / ignore) |
| FR-8 | If no relevant context is found, agents must say so explicitly rather than fabricate it |

## 4. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Latency | First token visible within 1.5s of trigger; full debate resolved within 8–12s |
| Privacy | No raw email/calendar content persisted beyond the session; only structured citations (source + short excerpt) are stored |
| Security | OAuth tokens encrypted at rest; MCP layer is the only component with raw provider access; orchestrator only ever sees pre-summarized context |
| Reliability (demo) | Every scripted demo scenario has a cached fallback transcript in case of a live API failure |
| Portability | All agent prompts and model choices are config-driven (no hardcoded provider lock-in) |

## 5. API Contracts (high-level)

```
POST /v1/sessions                 → create a debate session, returns session_id
POST /v1/sessions/{id}/context    → trigger MCP context fetch for this session
WS   /v1/sessions/{id}/stream     → streams agent turns + moderator synthesis
POST /v1/sessions/{id}/resolve    → record user's final decision (accepted | overridden | ignored)
GET  /v1/decisions                → paginated decision log for the dashboard
GET  /v1/decisions/{id}           → full debate transcript for one past decision
POST /v1/connectors/{provider}    → OAuth connect flow for calendar/email (read-only scopes)
```

Example WebSocket message (one agent turn):
```json
{
  "type": "agent_turn",
  "agent": "skeptic",
  "message": "That 'limited time' banner has shown for 6 days straight — it's not real urgency.",
  "citations": [{"source": "browser_dom", "detail": "banner element first seen 6 days ago"}],
  "confidence": 0.8
}
```

## 6. Third-Party Integrations

| Integration | Scope | Notes |
|---|---|---|
| Google Calendar API | Read-only | Used by Analyst/Ethicist for schedule/goal context |
| Gmail API | Read-only, metadata + relevant thread only | Used for "should I send this" voice queries |
| Anthropic API | Claude for Ethicist + Moderator | Higher reasoning quality where it matters most |
| Groq API | Llama 3.3 70B for Optimist/Skeptic/Analyst | Speed for real-time demo feel |
| Whisper | Streaming STT | Voice query transcription |

## 7. Deployment

- **Backend** (FastAPI + LangGraph orchestrator + WebSocket gateway + MCP servers): Railway
- **Dashboard** (Next.js): Vercel
- **Extension build**: bundled via Vite, distributed as an unpacked build for demo (no store submission needed for hackathon)
- **Database**: Railway PostgreSQL (or Supabase if a managed dashboard is useful during the build)

## 8. Environment Variables

```
ANTHROPIC_API_KEY=
GROQ_API_KEY=
GOOGLE_OAUTH_CLIENT_ID=
GOOGLE_OAUTH_CLIENT_SECRET=
DATABASE_URL=
TOKEN_ENCRYPTION_KEY=
WHISPER_MODEL=base.en
ENVIRONMENT=development|production
```

## 9. Rate Limiting & Cost Controls

- Each debate triggers up to 5 model calls (4 agents + moderator). Run the 4 personas **concurrently** (`asyncio.gather`), not sequentially, to hit the latency target.
- Tier models by role: fast/cheap (Groq Llama 3.3 70B) for Optimist, Skeptic, Analyst; stronger model (Claude) reserved for Ethicist and Moderator synthesis, where reasoning quality matters more than speed.
- Cap each agent turn to ~60–80 tokens to keep the debate readable in real time and to control cost.

## 10. Testing Strategy (hackathon-appropriate)

- No full test suite — time-boxed to scripted demo reliability.
- 3–5 golden demo scenarios (per README roadmap) tested end-to-end before judging, with transcripts cached as fallback.
- Manual smoke test of each MCP connector with a dummy account before demo day.
