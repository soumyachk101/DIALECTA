"""
LLM runners for the 4 agents + moderator.

Two execution modes:
  - run_agent(...) returns a single dict (used by tests and the demo fallback)
  - stream_agent(...) yields incremental token deltas (used by the WebSocket path
    to hit the <1.5s first-token latency target per TRD §4)

Model tiering per TRD §9: Groq (fast/cheap) for optimist/skeptic/analyst,
Claude (reasoning quality) for ethicist + moderator.

When API keys are absent AND `use_demo_fallback=True`, both paths use the
scripted demo turns from `Docs/AI_INSTRUCTIONS.md` §5.
"""
from __future__ import annotations

import asyncio
import json
import re
import time
from typing import Any, AsyncIterator, Literal

from app.agents.prompts import MODERATOR, PERSONAS
from app.config import get_settings

AgentName = Literal["optimist", "skeptic", "analyst", "ethicist", "moderator"]


# ---------- Demo fallback turns (per AI_INSTRUCTIONS.md §5) ----------

DEMO_TURNS: dict[str, dict[str, Any]] = {
    "optimist": {
        "message": "Your last two well-timed purchases both paid for themselves within a month — the pattern supports acting when the fit is right.",
        "citations": [{"source": "purchase_history", "detail": "2/2 recent considered purchases were retained past 30 days"}],
        "confidence": 0.72, "no_context_found": False,
    },
    "skeptic": {
        "message": "That 'limited time' banner has been on the page for 6 days — the urgency is manufactured, the price isn't actually moving.",
        "citations": [{"source": "browser_dom", "detail": "urgency banner first observed 6 days ago"}],
        "confidence": 0.81, "no_context_found": False,
    },
    "analyst": {
        "message": "3 similar purchases in the last 30 days, 2 of them unused. Discretionary spend is at 78% of your monthly cap.",
        "citations": [{"source": "purchase_history", "detail": "3 similar in 30d, 2 unused; 78% of monthly cap"}],
        "confidence": 0.85, "no_context_found": False,
    },
    "ethicist": {
        "message": "Your stated goal is a trip in 8 weeks — this purchase doesn't align with that priority right now. Not a moral issue, just a values match.",
        "citations": [{"source": "user_values", "detail": "stated: saving for a trip"}],
        "confidence": 0.78, "no_context_found": False,
    },
    "moderator": {
        "message": "Strongest point: the urgency isn't real. Biggest risk: it crowds out a stated goal. Take 24 hours — if you still want it tomorrow, buy it.",
        "citations": [], "confidence": 0.9, "no_context_found": False,
    },
}


def _extract_json(text: str) -> dict:
    """Models sometimes wrap JSON in code fences; tolerate that."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise


def _empty_turn(reason: str) -> dict[str, Any]:
    """Used when an agent's LLM call times out — we still emit a turn."""
    return {
        "message": f"[{reason}] this advisor is taking longer than expected; the others' points still stand.",
        "citations": [],
        "confidence": 0.4,
        "no_context_found": False,
    }


def _provider_for(agent: AgentName) -> tuple[str, str]:
    if agent == "moderator":
        return "anthropic", MODERATOR
    return ("groq" if agent in ("optimist", "skeptic", "analyst") else "anthropic"), PERSONAS[agent]


def _user_prompt(
    agent: AgentName,
    decision: str,
    context: str,
    other_turns: list[dict] | None = None,
) -> str:
    base = f"DECISION UNDER DEBATE:\n{decision}\n\nCONTEXT AVAILABLE TO YOU:\n{context}\n\nRespond as {agent} per your system rules."
    if agent == "moderator" and other_turns:
        bullet = "\n".join(f"- {t['agent']}: {t['message']}" for t in other_turns)
        return f"DECISION: {decision}\n\nTHE FOUR ADVISORS SAID:\n{bullet}\n\nSynthesize as the Moderator."
    return base


# ---------- Live LLM calls ----------

async def _call_groq_stream(system: str, user: str) -> AsyncIterator[str]:
    from groq import AsyncGroq
    client = AsyncGroq(api_key=get_settings().groq_api_key)
    stream = await client.chat.completions.create(
        model=get_settings().groq_model,
        max_tokens=get_settings().agent_turn_token_budget,
        temperature=0.4,
        stream=True,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


async def _call_anthropic_stream(system: str, user: str) -> AsyncIterator[str]:
    from anthropic import AsyncAnthropic
    client = AsyncAnthropic(api_key=get_settings().anthropic_api_key)
    async with client.messages.stream(
        model=get_settings().anthropic_model,
        max_tokens=get_settings().agent_turn_token_budget + 40,
        system=system,
        messages=[{"role": "user", "content": user}],
    ) as stream:
        async for text in stream.text_stream:
            yield text


# ---------- Public API ----------

async def run_agent(
    agent: AgentName,
    decision: str,
    context: str,
    other_turns: list[dict] | None = None,
) -> dict:
    """Return one agent's full turn as a dict. Falls back to demo on error/timeout."""
    settings = get_settings()
    has_keys = bool(settings.groq_api_key and settings.anthropic_api_key)
    if not has_keys and settings.use_demo_fallback:
        return DEMO_TURNS[agent]

    provider, system = _provider_for(agent)
    user = _user_prompt(agent, decision, context, other_turns)
    try:
        chunks: list[str] = []
        async def collect() -> AsyncIterator[str]:
            if provider == "groq":
                async for c in _call_groq_stream(system, user):
                    chunks.append(c); yield c
            else:
                async for c in _call_anthropic_stream(system, user):
                    chunks.append(c); yield c

        # Drain with a soft timeout (longer for moderator, shorter for agents)
        timeout = 6.0 if agent == "moderator" else 4.0
        async for _ in _with_timeout(collect(), timeout=timeout):
            pass
        raw = "".join(chunks)
        parsed = _extract_json(raw)
        return {
            "message": parsed["message"],
            "citations": parsed.get("citations", []),
            "confidence": float(parsed.get("confidence", 0.7)),
            "no_context_found": bool(parsed.get("no_context_found", False)),
        }
    except Exception:
        if settings.use_demo_fallback:
            return DEMO_TURNS[agent]
        raise


async def stream_agent(
    agent: AgentName,
    decision: str,
    context: str,
    other_turns: list[dict] | None = None,
) -> AsyncIterator[dict]:
    """
    Yield incremental updates for one agent. Each event is one of:
      {"type": "token", "delta": str}                      — incremental text
      {"type": "done", "turn": {...full turn dict...}}     — final result

    Falls back to the scripted demo turn (no per-token streaming) when API
    keys are missing or the call fails — still yields a single 'done' event.
    """
    settings = get_settings()
    has_keys = bool(settings.groq_api_key and settings.anthropic_api_key)
    if not has_keys and settings.use_demo_fallback:
        # Demo mode — emit the full text in one chunk so the UI still animates
        demo = DEMO_TURNS[agent]
        yield {"type": "token", "delta": demo["message"]}
        yield {"type": "done", "turn": demo}
        return

    provider, system = _provider_for(agent)
    user = _user_prompt(agent, decision, context, other_turns)
    chunks: list[str] = []
    first_token_at: float | None = None
    started = time.monotonic()

    async def producer() -> AsyncIterator[str]:
        nonlocal first_token_at
        if provider == "groq":
            async for c in _call_groq_stream(system, user):
                if first_token_at is None:
                    first_token_at = time.monotonic()
                chunks.append(c); yield c
        else:
            async for c in _call_anthropic_stream(system, user):
                if first_token_at is None:
                    first_token_at = time.monotonic()
                chunks.append(c); yield c

    timeout = 6.0 if agent == "moderator" else 4.0
    try:
        async for _ in _with_timeout(producer(), timeout=timeout):
            pass
    except Exception:
        if settings.use_demo_fallback:
            demo = DEMO_TURNS[agent]
            yield {"type": "token", "delta": demo["message"]}
            yield {"type": "done", "turn": demo}
            return
        yield {"type": "done", "turn": _empty_turn("timeout")}
        return

    raw = "".join(chunks)
    try:
        parsed = _extract_json(raw)
        turn = {
            "message": parsed["message"],
            "citations": parsed.get("citations", []),
            "confidence": float(parsed.get("confidence", 0.7)),
            "no_context_found": bool(parsed.get("no_context_found", False)),
        }
    except Exception:
        turn = _empty_turn("parse_error")

    if first_token_at is not None:
        turn["first_token_ms"] = int((first_token_at - started) * 1000)
    yield {"type": "done", "turn": turn}


async def _with_timeout(async_iter: AsyncIterator, timeout: float) -> AsyncIterator:
    """Wrap an async iterator with a soft timeout that ends iteration cleanly."""
    aiter = async_iter.__aiter__()
    while True:
        try:
            item = await asyncio.wait_for(aiter.__anext__(), timeout=timeout)
            yield item
        except (asyncio.TimeoutError, StopAsyncIteration):
            return


# ---------- Parallel orchestration ----------

async def run_agents_parallel(decision: str, context: str) -> list[dict]:
    return await asyncio.gather(*[
        run_agent(name, decision, context)
        for name in ("optimist", "skeptic", "analyst", "ethicist")
    ])


async def run_moderator(decision: str, turns: list[dict]) -> dict:
    return await run_agent("moderator", decision, context="", other_turns=turns)
