# DIALECTA — Product Requirements Document (PRD)

> Don't think alone. Carry a team.

## 1. Summary

DIALECTA is a real-time, multimodal, adversarial multi-agent system that intercepts a user at the point of decision — checkout, send, sign, post — and runs that decision through four AI personas (Optimist, Skeptic, Analyst, Ethicist) who debate it live, using the user's real context (calendar, email, past behavior, stated goals).

It is not a chatbot. It is an **intervention layer**.

## 2. Problem Statement

- Cognitive bias is estimated to cost the global economy **$1.5 trillion annually** through bad financial decisions, poor hires, and failed projects.
- People rarely regret a decision *before* making it — regret shows up hours or days later, when it's too late to act on it.
- Existing AI assistants are reactive: the user has to remember to ask. DIALECTA is proactive: it shows up at the moment of commitment, uninvited but useful.

## 3. Goals

### 3.1 Hackathon Goals (48h MVP)
- Demonstrate a live, multi-agent debate triggered by a real browser action (checkout) and a voice query.
- Prove the "cognitive parliament" concept is technically real — not a mockup — by wiring actual LLM calls, actual MCP context fetches, and actual streaming output.
- Land a 3-minute demo that gets an emotional "oh damn" reaction from judges.

### 3.2 Post-Hackathon Vision
- Always-on browser + mobile companion with persistent decision history and outcome tracking.
- B2B compliance variant for regulated decision-making (banking, insurance, healthcare).
- Marketplace of "agent packs" — domain-specific persona sets (see Theme Variations in README).

## 4. Non-Goals (MVP)

- No real mobile app for the 48h build (stretch only).
- No fine-tuned/custom models — orchestration over existing LLM APIs only.
- No production-grade auth/billing — demo-grade login is enough.
- No claim of medical, legal, or financial advice — the Ethicist explicitly defers to professionals on regulated topics.

## 5. Target Users / Personas

| Persona | Description | What they need from DIALECTA |
|---|---|---|
| The Impulsive Spender | Shops when stressed or bored, regrets purchases within a day | A pause + reality check at checkout |
| The Reactive Communicator | Sends emails/messages in anger, regrets tone later | A debate before hitting send |
| The Hackathon Judge | Evaluating 20+ projects in a few minutes | A demo that is visually self-explanatory and fast to "get" |

## 6. User Stories

| As a... | I want... | So that... |
|---|---|---|
| User | the system to pause my checkout for 5 seconds with a quick debate | I don't buy something I'll regret |
| User | to ask a voice question before sending a risky message | I get a second opinion grounded in my real history |
| User | to see *why* each agent says what it says | I trust the system instead of dismissing it |
| User | to review past interventions | I can see patterns in my own decision-making |
| Judge | to understand the concept within 30 seconds of the demo starting | I can evaluate it fairly against other projects |

## 7. Core Features (MVP Scope)

| ID | Feature | Description |
|---|---|---|
| F1 | Cognitive Parliament Debate Engine | Orchestrates 4 personas + 1 moderator over a single decision, streamed live |
| F2 | Browser Extension Interceptor | Detects a checkout/send action on a demo page and triggers a debate overlay |
| F3 | Voice Query Mode | User asks a question out loud; Whisper transcribes; debate triggers the same engine |
| F4 | Context Connectors (read-only) | Calendar + email + a small "purchase history" mock dataset feed real context into the debate |
| F5 | Decision Log | Every debate is saved with its outcome (accepted / overridden / ignored) |

## 8. Stretch Features (if time permits)

- Screenshot/vision context (webcam or page capture) for the Analyst.
- Wearable trigger (phone vibration before action commits).
- A second, opposing voice in the live demo (devil's advocate audience plant) — purely theatrical, not a product feature.

## 9. Success Metrics

**Demo-day (hackathon):**
- First agent token visible within ~1.5s of trigger.
- Full 4-agent debate resolved within 8–12s.
- Zero dead air during the live demo (fallback transcript ready if a live call fails).

**Product (post-hackathon, directional):**
- % of intercepted decisions where the user changes course.
- Decision Log retention/return rate after 7 days.
- Time-to-trust: number of interventions before a user stops dismissing them reflexively.

## 10. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Live LLM calls fail/time out mid-demo | Pre-recorded fallback transcript for each scripted demo scenario |
| Judges read agents as gimmicky | Ground every agent turn in a specific, named piece of real context (not generic advice) |
| Privacy concern (reading calendar/email) | Read-only OAuth scopes, MCP layer is the only thing touching raw data, nothing raw persisted (see TRD §4, ARCHITECTURE §5) |
| 4 parallel LLM calls per debate = cost/latency | Model-tier the agents: fast/cheap model for Optimist & Skeptic, stronger model for Ethicist & Moderator (see TRD §9) |

## 11. Prior Art Landscape (general categories, not specific products)

- General-purpose AI chat assistants — reactive, no intervention layer.
- Browser shopping-assistant extensions — focused on price/coupons, not behavioral bias.
- Journaling / reflection apps — after-the-fact, not real-time.

DIALECTA's differentiation is the combination of **real-time interception** + **adversarial multi-persona debate** + **grounding in the user's actual data**, which none of the above combine.
