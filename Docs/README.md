# DIALECTA

**Don't think alone. Carry a team.**

A real-time, multimodal, adversarial multi-agent system that acts as a *cognitive parliament* in your pocket. Four AI agents — each with a distinct thinking style — debate your decisions as you make them, catching cognitive biases before they cost you money, relationships, or sleep.

---

## Table of Contents

- [Overview](#overview)
- [The Problem](#the-problem)
- [Core Architecture: The Cognitive Parliament](#core-architecture-the-cognitive-parliament)
- [Tech Stack](#tech-stack)
- [How It Works (Demo Flow)](#how-it-works-demo-flow)
- [Why This Wins](#why-this-wins)
- [Implementation Roadmap (48-Hour Build)](#implementation-roadmap-48-hour-build)
- [Theme Variations](#theme-variations)
- [Business Model](#business-model)
- [Pitch Script](#pitch-script)
- [Status](#status)

---

## Overview

DIALECTA is not another chatbot. It's an **intervention layer** that sits at the exact moment you're about to commit to a decision — a checkout button, a "send" click, a signature, a post — and runs that decision through four adversarial AI personas before you act on it.

Each persona pulls live context from your actual data (calendar, email, past purchases, stated goals) through MCP tools, debates the decision out loud, and hands you a clearer picture in seconds.

## The Problem

- Cognitive bias is estimated to cost the global economy **$1.5 trillion annually** through bad financial decisions, poor hires, and failed projects.
- Everyone has made a decision they regretted within 24 hours — and almost no one has a system that catches it *before* it happens, not after.
- Most "AI assistants" are reactive (you ask, it answers). DIALECTA is proactive — it intercepts you at the point of commitment.

## Core Architecture: The Cognitive Parliament

Four agents, four jobs, one debate:

| Agent | Role |
|---|---|
| 🟢 **The Optimist** | Surfaces opportunities, finds supporting evidence, builds the best-case scenario |
| 🔴 **The Skeptic** | Stress-tests assumptions, hunts for flaws, demands evidence, asks "what could go wrong?" |
| 🔵 **The Analyst** | Crunches the numbers, checks historical patterns, runs quick projections |
| 🟣 **The Ethicist** | Tests alignment against your stated values, long-term goals, and broader impact |

The agents don't just answer — they **argue with each other**, and you watch the debate unfold in real time.

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Multi-Agent Orchestration | CrewAI / LangGraph | Custom task delegation between the four personas |
| Context Integration | Custom MCP servers (browser, email, calendar, documents) | Gives agents access to your real data, not generic knowledge |
| Multimodal Input | Whisper (voice) + Vision (screenshots/webcam) | Goes beyond text-only interaction |
| Real-Time Streaming | WebRTC + WebSocket | Live, low-latency voice debates |
| Edge/Local Processing | Local LLM (Llama 3.1/3.2 or Qwen) | Privacy-preserving inference where possible |
| Intervention Layer | Browser extension + mobile app + wearable trigger | Meets the user at the actual point of decision |

## How It Works (Demo Flow)

1. **The Hook** — A familiar moment: about to commit to a decision you might regret.
2. **The Intercept** — DIALECTA pauses the action. Example: at checkout, the Analyst flags a pattern of unused past purchases, the Skeptic calls out fake urgency in a "limited time" banner, and the Ethicist checks the purchase against a stated savings goal.
3. **The Voice Debate** — Ask a question out loud (e.g. "Should I send this angry email to my client?") and the four agents debate it live, citing context pulled from your actual sent folder and calendar.
4. **The Decision** — You decide, fully informed, in seconds — not regretfully, hours later.

## Why This Wins

1. **Universal, high-pain problem.** Every judge has personally made a bad decision in the heat of the moment.
2. **Rides the right technical waves.** Agentic AI, MCP-based tool integration, multimodal input, and adversarial multi-agent design are all front-and-center trends right now.
3. **Technical depth, not a wrapper.** Four distinct, coordinated agent personalities with live tool access and real-time voice — not a single prompt to a single model.
4. **Clear differentiation.** Not a chatbot, not a coding assistant, not a RAG search tool — a new category: personal cognitive infrastructure.
5. **A real business underneath.** Freemium for everyday decisions, premium for high-stakes financial/medical calls, and a B2B compliance angle for regulated industries like banking and insurance.

## Implementation Roadmap (48-Hour Build)

**Phase 1 — MVP Core (Hours 0–12)**
- [ ] Stand up the four agent personas in CrewAI/LangGraph
- [ ] Build one MCP server (browser extension for web decisions)
- [ ] Create the debate output formatter

**Phase 2 — Polish & Demo (Hours 12–30)**
- [ ] Add voice input via streaming Whisper
- [ ] Add vision input via screenshot context
- [ ] Build the browser extension UI around the "intervention" moment
- [ ] Pre-seed 3–5 compelling demo scenarios

**Phase 3 — Presentation (Hours 30–48)**
- [ ] Record a 3-minute demo video (a purchase intervention + an email intervention)
- [ ] Build the slide deck around the "cognitive parliament" metaphor
- [ ] Clean up the GitHub repo: README, architecture diagram, setup instructions

## Theme Variations

If a hackathon track calls for a specific domain, DIALECTA pivots cleanly:

| Theme | Pivot |
|---|---|
| Healthcare | **Clinical Dialecta** — debates treatment decisions against patient history to reduce medical error |
| Finance | **Trade Parliament** — real-time trade analysis with dedicated risk, compliance, and opportunity agents |
| Education | **Socratic Council** — students debate ideas against Socratic and devil's-advocate AI personas |
| Sustainability | **Green Council** — evaluates purchases against carbon footprint and ethical sourcing |
| Accessibility | **NeuroParliament** — tuned for ADHD/autism/executive dysfunction, focused on task initiation and follow-through |

## Business Model

- **Freemium:** everyday decisions are free; deep financial/medical decision support is a paid tier.
- **B2B:** enterprise decision-making compliance — a natural fit for banks, insurers, and other regulated industries that need an auditable decision trail.

## Pitch Script

> When you shop online, an algorithm built by someone else is optimizing against you. When you make decisions, you're alone with your biases. DIALECTA is a real-time cognitive immune system — four AI advisors with access to your real data, debating every important choice before you commit. It's not a chatbot. It's not a search engine. It's a cognitive parliament in your pocket. And it was built in 48 hours.

## Status

🚧 **In active development.** Built for hackathon submission — architecture and roadmap above, implementation in progress.

---

<p align="center">
  <em>Built by Soumya</em>
</p>
