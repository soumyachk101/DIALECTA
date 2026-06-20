# DIALECTA

> **Don't think alone. Carry a team.**

A real-time, multimodal, adversarial multi-agent system that acts as a *cognitive parliament* in your pocket. Four AI agents — each with a distinct thinking style — debate your decisions as you make them, catching cognitive biases before they cost you money, relationships, or sleep.

![Hero — live debate streaming](assets/gifs/hero-debate.gif)

---

## What is DIALECTA?

Imagine you're about to click **Buy** on a ₹4,999 chair. A little badge pops up at the bottom of the page: *"DIALECTA is opening a debate…"* A new tab opens with **four colored seats around a central decision prompt**, and each seat types out one short, specific take — citing *your* calendar, *your* past purchases, *your* stated values. A moderator then weighs all four and gives you one closing recommendation. Then you decide.

DIALECTA is **not** a chatbot. It's an **intervention layer** that meets you at the actual point of commitment.

- 🟢 **The Optimist** — finds the strongest *honest* case **for** the decision
- 🔴 **The Skeptic** — stress-tests assumptions, hunts for manufactured urgency
- 🔵 **The Analyst** — surfaces the numbers: frequency, cost, pattern
- 🟣 **The Ethicist** — checks the decision against *your* stated values

---

## 🗺️ Table of Contents

1. [Quick look — what it does](#-quick-look--what-it-does)
2. [How it works — interactive flows](#-how-it-works--interactive-flows)
3. [The architecture — at a glance](#-the-architecture--at-a-glance)
4. [The 60-second mental model](#-the-60-second-mental-model)
5. [Repository layout](#-repository-layout)
6. [Quick start — get it running](#-quick-start--get-it-running)
7. [Use it — a guided tour](#-use-it--a-guided-tour)
8. [Configuration — environment variables](#-configuration--environment-variables)
9. [The privacy boundary](#-the-privacy-boundary)
10. [Testing](#-testing)
11. [Deploying it](#-deploying-it)
12. [Glossary for beginners](#-glossary-for-beginners)

---

## 👀 Quick look — what it does

| Trigger | What happens | Result |
|---|---|---|
| You click **Buy / Checkout / Send / Post** on a tracked page | Extension opens a debate tab in <1.5s | You act with a 4-agent second opinion |
| You ask DIALECTA a voice question out loud | Whisper transcribes, debate runs on the transcript | You get a 4-agent take grounded in your history |
| You ignore / accept / override | Logged to the **Decision Log** | Patterns emerge over time |
| You review past decisions | Each opens the full transcript + outcome | You see *why* a past call went the way it did |

![Decision log populating](assets/gifs/dashboard.gif)

---

## 🔁 How it works — interactive flows

### Flow 1 — Onboarding (one-time)

```mermaid
flowchart LR
    A[📦 Install extension] --> B[🔐 Sign in]
    B --> C[🔗 Connect calendar + email<br>read-only OAuth]
    C --> D[🎯 Set your stated values<br>e.g. 'saving for a trip']
    D --> E[🎬 Watch one demo intervention]
    E --> F[✅ Ready]

    style A fill:#13141A,stroke:#7C3AED
    style C fill:#13141A,stroke:#38BDF8
    style D fill:#13141A,stroke:#F5A524
    style F fill:#13141A,stroke:#34D399
```

> **Beginner note:** OAuth is the same "Sign in with Google" flow you've used a hundred times. "Read-only" means DIALECTA can *read* your email/calendar but never *write* or *send* anything.

### Flow 2 — Browser checkout intercept (the core flow)

```mermaid
flowchart TD
    Start([You're at a checkout page]) --> Click[You click 'Pay']
    Click --> Detect{Extension sees a<br>buy/checkout/send<br>button?}
    Detect -- "No" --> Nothing[Pass through silently]
    Detect -- "Yes" --> Extract[Extract page context:<br>item, amount, banner age]
    Extract --> Call[Service worker calls<br>POST /v1/sessions]
    Call --> Backend[Backend fetches context<br>via MCP layer]
    Backend --> Debate[4 agents debate in parallel<br>+ Moderator synthesizes]
    Debate --> Stream[WebSocket streams turns<br>to the debate tab]
    Stream --> You[You read the debate]
    You --> Choice{What do you do?}
    Choice -- "Cancel" --> Log1[Logged: ACCEPTED]
    Choice -- "Continue" --> Log2[Logged: OVERRIDDEN]
    Choice -- "Dismiss" --> Log3[Logged: IGNORED]

    style Debate fill:#13141A,stroke:#7C3AED
    style Stream fill:#13141A,stroke:#38BDF8
    style Log1 fill:#13141A,stroke:#34D399
    style Log2 fill:#13141A,stroke:#F5A524
    style Log3 fill:#13141A,stroke:#8B8D98
```

> **Why parallel?** All 4 agents see the *same* context but argue from *different* angles. Running them concurrently hits the **<1.5s first-token** target — the debate feels live, not laggy.

### Flow 3 — Voice query (out-loud questions)

```mermaid
flowchart LR
    A[🎤 You ask out loud<br>'Should I send this angry email?'] --> B[Whisper transcribes]
    B --> C[Backend creates a session<br>using the transcript as the decision]
    C --> D[Gmail MCP fetches<br>the thread context]
    D --> E[4 agents debate<br>grounded in the actual thread]
    E --> F[🔉 Voice + text output]
    F --> G[You act / ignore]

    style A fill:#13141A,stroke:#38BDF8
    style E fill:#13141A,stroke:#7C3AED
    style G fill:#13141A,stroke:#34D399
```

### Flow 4 — Decision log review (the long-term payoff)

```mermaid
flowchart LR
    A[📋 Open dashboard] --> B[See all past decisions<br>chronological]
    B --> C[Click a row]
    C --> D[Full debate transcript<br>+ the agent citations]
    D --> E[Optional: tag the real-world<br>outcome later]
    E --> F[Over time, DIALECTA learns<br>which advisor was right for you]

    style A fill:#13141A,stroke:#7C3AED
    style F fill:#13141A,stroke:#34D399
```

### Flow 5 — The full request lifecycle

![Full request lifecycle — sequence](assets/gifs/lifecycle.gif)

In one checkout click you go from **user → extension → backend → LLM → WebSocket → resolved decision in ~150ms**.

---

## 🏛️ The architecture — at a glance

```mermaid
flowchart TB
    subgraph Client
        BX[Browser Extension<br>MV3]
        VC[Voice capture]
        DB[Next.js Dashboard]
    end

    subgraph Backend [FastAPI · Python]
        GW[API Gateway<br>REST + WebSocket]
        ORCH[Orchestrator<br>async state machine]
        A1[Optimist]
        A2[Skeptic]
        A3[Analyst]
        A4[Ethicist]
        MOD[Moderator]
    end

    subgraph MCP [MCP Context Layer<br>privacy boundary]
        CAL[Google Calendar]
        MAIL[Gmail]
        DOM[Browser DOM]
    end

    subgraph LLMs
        GROQ[Groq · Llama 3.3 70B<br>fast + cheap]
        CLAUDE[Claude 3.5 Sonnet<br>reasoning quality]
    end

    DB_STORE[(PostgreSQL)]

    BX --> GW
    VC --> GW
    DB --> GW
    GW --> ORCH
    ORCH --> MCP
    ORCH --> A1
    ORCH --> A2
    ORCH --> A3
    ORCH --> A4
    A1 --> GROQ
    A2 --> GROQ
    A3 --> GROQ
    A4 --> CLAUDE
    A1 --> MOD
    A2 --> MOD
    A3 --> MOD
    A4 --> MOD
    MOD --> CLAUDE
    MOD --> GW
    ORCH --> DB_STORE
```

**Key design choices** (from `Docs/ARCHITECTURE.md`):

| Choice | Why |
|---|---|
| **4 parallel agents + 1 Moderator** | Adversarial, not echo-chamber. Each agent sees the same context but argues from a different angle. |
| **MCP layer as privacy boundary** | OAuth tokens are *only* decrypted inside this layer. The orchestrator never sees raw email bodies. |
| **Per-token WebSocket streaming** | Hits the **<1.5s first-token** target — the debate feels live. |
| **Model tiering** (Groq for speed, Claude for reasoning) | Optimist/Skeptic/Analyst run on fast Llama 3.3 70B; Ethicist + Moderator get Claude for nuance. |
| **Citations, not payloads** | Only `{"source": "...", "detail": "..."}` summaries are stored — never raw event bodies. |

---

## 🧠 The 60-second mental model

> Think of DIALECTA as **4 different friends sitting around a table with your phone's data open**, each asked to weigh in on a decision you're about to make.

1. **You're about to act** — click Buy, hit Send, sign a contract.
2. **The extension intercepts** — pauses the action for ~5 seconds.
3. **A new tab opens** — a small UI where 4 colored "seats" sit around a centered decision prompt.
4. **All 4 seats light up in parallel**, each typing a short, specific take.
5. **A 5th voice (the Moderator)** weighs all four and gives you one closing take.
6. **You decide** — Cancel, Continue anyway, or Dismiss. Your choice is logged.

**The radical part:** the agents are *adversarial*. The Skeptic is *trying* to find flaws. The Analyst is *trying* to find numbers that contradict your gut. The Ethicist is *trying* to show that this decision contradicts your own stated values. They argue with each other; you watch.

```mermaid
sequenceDiagram
    participant U as You
    participant E as Extension
    participant B as Backend
    participant A as Agents (x4)
    participant M as Moderator

    U->>E: clicks 'Buy'
    E->>B: POST /v1/sessions
    B-->>E: session_id
    B->>A: dispatch shared context
    A-->>B: stream tokens (parallel)
    B-->>E: WS: agent turns
    B->>M: all 4 turns
    M-->>B: closing take
    B-->>E: WS: moderator_turn
    U->>E: accept / override / dismiss
    E->>B: POST /resolve
    Note over B: outcome logged
```

---

## 📁 Repository layout

```
DIALECTA/
│
├── 📂 Docs/                ← The spec — read this first
│   ├── README.md           ← 1-page pitch
│   ├── PRD.md              ← What & why
│   ├── TRD.md              ← Tech requirements
│   ├── ARCHITECTURE.md     ← System diagram + state machine
│   ├── BACKEND_SCHEMA.md   ← Postgres tables + SQL
│   ├── APP_FLOW.md         ← User flows
│   ├── UI_UX.md            ← Visual design spec
│   └── AI_INSTRUCTIONS.md  ← Exact persona prompts
│
├── 📂 backend/             ← FastAPI + async orchestrator
│   ├── app/
│   │   ├── agents/         ← orchestrator + runners + persona prompts
│   │   ├── mcp/            ← Context layer (privacy boundary)
│   │   │   └── providers/  ← Real Google Calendar + Gmail clients
│   │   ├── api/routes.py   ← REST + WebSocket endpoints
│   │   ├── models/orm.py   ← SQLAlchemy models
│   │   ├── schemas/        ← Pydantic request/response/WS
│   │   ├── services/       ← Token encryption
│   │   ├── db/session.py   ← Async engine
│   │   ├── config.py       ← pydantic-settings
│   │   └── main.py         ← FastAPI app + lifespan
│   ├── alembic/            ← DB migrations
│   ├── tests/              ← pytest suite (runner + orchestrator + privacy)
│   ├── scripts/            ← seed_demo_user.py
│   ├── Dockerfile          ← Production image
│   └── pyproject.toml
│
├── 📂 extension/           ← Chrome extension (Manifest V3)
│   ├── manifest.json
│   └── src/
│       ├── background/     ← Service worker (creates sessions)
│       ├── content/        ← Detects buy/checkout/send clicks
│       ├── popup/          ← Extension popup + debate tab
│       └── options/        ← Settings page
│
├── 📂 dashboard/           ← Next.js 15 + Tailwind
│   └── src/app/
│       ├── page.tsx        ← Decision Log
│       ├── decisions/[id]/ ← Full transcript + radial replay
│       └── settings/       ← Agent tuning + stated values
│
├── 📂 design-system/       ← UI/UX Pro Max generated tokens
│
├── 📂 assets/gifs/         ← The GIFs you see in this README
│
├── docker-compose.yml      ← Postgres + backend in one command
└── README.md               ← You are here
```

---

## 🚀 Quick start — get it running

### Option A — Everything in Docker (one command)

```bash
# 1. (Optional) Set LLM keys for live debates
export ANTHROPIC_API_KEY=sk-ant-...
export GROQ_API_KEY=gsk_...

# 2. Boot it
docker compose up --build

# 3. Seed a demo user (one-time, in another terminal)
docker compose exec backend python -m scripts.seed_demo_user

# 4. Open
#    Backend:   http://localhost:8000/health
#    Dashboard: http://localhost:3000
#    Extension: see step below
```

> **No LLM keys?** The backend ships with a **demo fallback mode** — agents use the same scripted turns documented in `Docs/AI_INSTRUCTIONS.md` §5. The whole pipeline (context fetch → parallel debate → WebSocket → persistence) still runs.

### Option B — Local dev (3 terminals)

#### Terminal 1 — Database

```bash
docker compose up -d postgres
```

#### Terminal 2 — Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head                       # apply schema
uvicorn app.main:app --reload --port 8000
python -m scripts.seed_demo_user           # demo data
```

Verify it's healthy:

```bash
curl http://localhost:8000/health
# → {"status":"ok","service":"dialecta-backend","llm_providers":{...},...}
```

#### Terminal 3 — Dashboard

```bash
cd dashboard
npm install
npm run dev
# → http://localhost:3000
```

#### Then — Load the extension

```bash
cd extension
npm install
npm run build
# → dist/ ready

# In Chrome:
# 1. Open chrome://extensions
# 2. Enable "Developer mode" (top right)
# 3. Click "Load unpacked"
# 4. Select the extension/dist/ directory
# 5. Pin the DIALECTA icon to your toolbar
```

---

## 🎯 Use it — a guided tour

### 1. Trigger a demo debate from the extension popup

Click the DIALECTA icon in your Chrome toolbar. Click **"Trigger demo intercept"**. A new tab opens with a live debate running.

### 2. Or visit any checkout page

The content script watches for buttons that say `Buy`, `Checkout`, `Pay`, `Send`, `Post`, etc. Click one — the debate tab opens.

### 3. Try the dashboard

Open `http://localhost:3000` and see your past debates. Click any row to see the **radial replay** with the moderator's closing take.

![Settings — sliders animate as you tune each agent](assets/gifs/settings.gif)

In **Settings**, slide the per-agent "gentle ↔ blunt" sliders and edit your stated values. The Ethicist re-checks every decision against the text you save here.

### 4. What the agents actually say (demo mode)

For the decision *"Buy ergonomic chair — ₹4,999"*, the four agents return:

| Agent | What they say (1-2 sentences) |
|---|---|
| 🟢 **Optimist** | "Your last two well-timed purchases both paid for themselves within a month — the pattern supports acting when the fit is right." |
| 🔴 **Skeptic** | "That 'limited time' banner has been on the page for 6 days — the urgency is manufactured, the price isn't actually moving." |
| 🔵 **Analyst** | "3 similar purchases in the last 30 days, 2 of them unused. Discretionary spend is at 78% of your monthly cap." |
| 🟣 **Ethicist** | "Your stated goal is a trip in 8 weeks — this purchase doesn't align with that priority right now." |
| **Moderator** | "Strongest point: the urgency isn't real. Biggest risk: it crowds out a stated goal. Take 24 hours — if you still want it tomorrow, buy it." |

Every claim is **grounded in a citation** — never invented. If a provider returns no data, the agent says so:

![No context — agents say so explicitly](assets/gifs/error-path.gif)

> The rule (from `Docs/AI_INSTRUCTIONS.md` §6): **"`no_context_found: true` is always preferable to an invented citation."**

---

## ⚙️ Configuration — environment variables

Create `backend/.env` from `.env.example`:

```bash
# Environment
ENVIRONMENT=development                  # development auto-creates tables; production uses alembic
DATABASE_URL=postgresql+asyncpg://dialecta:dialecta@localhost:5432/dialecta
TOKEN_ENCRYPTION_KEY=replace-me-32-bytes # Fernet key for OAuth token encryption

# LLM providers (leave empty for demo fallback)
ANTHROPIC_API_KEY=
GROQ_API_KEY=
ANTHROPIC_MODEL=claude-3-5-sonnet-latest
GROQ_MODEL=llama-3.3-70b-versatile

# Streaming targets
STREAM_FIRST_TOKEN_TIMEOUT_S=1.5         # TRD §4: first token in 1.5s
AGENT_TURN_TOKEN_BUDGET=80               # TRD §9: 60-80 tokens per turn

# Demo / fallback
USE_DEMO_FALLBACK=true

# Server
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=["http://localhost:3000","chrome-extension://*"]
```

---

## 🔐 The privacy boundary

DIALECTA reads your email and calendar. That's a lot of trust. Here's the contract:

```mermaid
flowchart LR
    subgraph Out[Outside MCP — orchestrator + agents]
        O[Orchestrator]
        A[Agent prompts]
    end

    subgraph Inside[Inside MCP layer — only place tokens exist]
        D[Decrypt token]
        API[Call Google API]
        S[Return structured Citation]
    end

    DB[(connected_accounts<br>encrypted_token BYTEA)]

    O -. "give me context for user X" .-> Inside
    Inside --> DB
    Inside --> API
    Inside --> S
    S -. "citation only" .-> O
    O --> A

    style Inside fill:#13141A,stroke:#7C3AED,stroke-width:2px
    style Out fill:#0A0A0C,stroke:#38BDF8
```

**Five concrete guarantees:**

1. **OAuth tokens are encrypted at rest** with Fernet (`TOKEN_ENCRYPTION_KEY`). Postgres never stores plaintext.
2. **Only the MCP layer decrypts** them, and only at the moment of an API call.
3. **Only structured citations** (`{source, detail}`) leave the MCP layer. Raw email bodies and calendar event payloads **do not** cross the boundary.
4. **Citations are the only thing persisted** in the debate transcript — no raw payloads, ever.
5. **On disconnect, the row is hard-deleted** (no soft-delete of revoked tokens).

This is enforced by tests in `backend/tests/test_privacy.py`.

---

## 🧪 Testing

```bash
cd backend

# All tests (runner + orchestrator + privacy)
pytest

# Just the privacy boundary
pytest tests/test_privacy.py -v

# Just the orchestrator state machine
pytest tests/test_orchestrator.py -v

# Lint
ruff check app tests
```

The suite uses an in-memory SQLite database (with Postgres types emulated) for fast, hermetic tests. No external services required.

---

## 🌐 Deploying it

The repo ships with a production `Dockerfile` and `docker-compose.yml` for Railway / Fly.io / Render.

**Backend** (`backend/Dockerfile`):
- Multi-stage-friendly, non-root user
- Runs `alembic upgrade head` on boot
- 2 uvicorn workers
- HEALTHCHECK on `/health`

**Database**: PostgreSQL 16 (alpine). Migrations live in `backend/alembic/versions/`.

**Extension**: build with `npm run build`, distribute the `extension/dist/` directory as an unpacked build (no Chrome Web Store submission needed for the hackathon).

**Dashboard**: `npm run build` → deploy `.next/` to Vercel. The `/v1/*` path is proxied to the backend via `next.config.mjs`.

**Environment variables** (set in your platform's secret store):
- `ANTHROPIC_API_KEY`, `GROQ_API_KEY`
- `DATABASE_URL` (point at your managed Postgres)
- `TOKEN_ENCRYPTION_KEY` (generate a fresh 32-byte key — see `cryptography.Fernet.generate_key()`)
- `ENVIRONMENT=production`

---

## 📚 Glossary for beginners

| Term | What it means in DIALECTA |
|---|---|
| **Multi-agent system** | Multiple AI "personalities" each called separately with the same context, arguing from different angles. |
| **Orchestrator** | The Python code that runs the state machine: context → debate → moderator → persist. |
| **MCP (Model Context Protocol)** | The pattern of giving an LLM access to external tools/data. DIALECTA uses a *custom* MCP layer for privacy. |
| **Adversarial** | The agents are *trying* to disagree. The Skeptic is paid to find flaws. The Ethicist is paid to challenge your values. |
| **Citation** | A short, structured `{"source": "...", "detail": "..."}` snippet. Never a raw payload. |
| **WebSocket** | A persistent two-way connection. DIALECTA uses it to stream debate tokens to the UI in real time. |
| **MV3** | Manifest V3 — the current Chrome extension format. |
| **OAuth** | "Sign in with Google" — DIALECTA uses read-only scopes; it can read your email/calendar but never write. |
| **Fernet encryption** | Symmetric encryption from the `cryptography` library. Used to encrypt OAuth tokens at rest. |
| **Alembic** | The standard DB migration tool for SQLAlchemy. Lets you evolve the schema without losing data. |
| **First-token latency** | The time from "user clicks Buy" to "first character appears in the debate UI". Target: 1.5s. |

---

## 🧭 Where to look next

- **Spec deep-dive** → `Docs/PRD.md` (what & why) · `Docs/TRD.md` (tech requirements) · `Docs/AI_INSTRUCTIONS.md` (persona prompts)
- **Architecture** → `Docs/ARCHITECTURE.md` (system diagram + state machine) · `Docs/BACKEND_SCHEMA.md` (DB schema)
- **Visual design** → `Docs/UI_UX.md` (colors, typography, layouts)
- **Code entry points** → `backend/app/main.py` · `backend/app/agents/orchestrator.py` · `extension/src/content/content-script.ts` · `dashboard/src/app/page.tsx`

---

<p align="center">
  <em>Built by Soumya · 48-hour hackathon build</em>
  <br><br>
  <a href="Docs/README.md">One-page pitch →</a>
  &nbsp;·&nbsp;
  <a href="Docs/PRD.md">Full PRD →</a>
  &nbsp;·&nbsp;
  <a href="Docs/ARCHITECTURE.md">Architecture →</a>
</p>
