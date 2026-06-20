"""Tests for the agent runner — covers demo fallback + structured output."""
import pytest

from app.agents.runner import run_agents_parallel, run_moderator, stream_agent


@pytest.mark.asyncio
async def test_demo_fallback_runs_without_api_keys():
    """No API keys configured — system should fall back to scripted turns."""
    turns = await run_agents_parallel(
        decision="About to buy: chair for \u20B94999",
        context="Stated values:\n- saving for a trip\n\nPage context:\n- browser_dom: banner 6 days old",
    )
    assert len(turns) == 4
    agents = {t["agent"] for t in turns}
    assert agents == {"optimist", "skeptic", "analyst", "ethicist"}
    for t in turns:
        assert "message" in t and len(t["message"]) > 0
        assert 0.0 <= t["confidence"] <= 1.0
        assert "citations" in t
        assert "no_context_found" in t


@pytest.mark.asyncio
async def test_moderator_synthesizes_from_turns():
    """Moderator should reference the four agents' messages."""
    turns = [
        {"agent": "optimist", "message": "strong fit"},
        {"agent": "skeptic",  "message": "urgency is fake"},
        {"agent": "analyst",  "message": "3 similar in 30 days"},
        {"agent": "ethicist", "message": "doesn't match savings goal"},
    ]
    mod = await run_moderator("decision", turns)
    assert mod["agent"] == "moderator"
    assert "message" in mod
    assert len(mod["message"]) > 0


@pytest.mark.asyncio
async def test_stream_agent_emits_done_event():
    """stream_agent should yield at least one 'done' event with a full turn dict."""
    events = []
    async for ev in stream_agent("optimist", "decision", "context"):
        events.append(ev)
        if ev["type"] == "done":
            break
    assert any(ev["type"] == "done" for ev in events)
    done = next(ev for ev in events if ev["type"] == "done")
    assert "turn" in done
    assert "message" in done["turn"]
    assert done["turn"]["agent"] == "optimist"


@pytest.mark.asyncio
async def test_turn_under_token_budget():
    """Demo turns should be short per TRD §9 (60-80 token cap)."""
    turns = await run_agents_parallel("decision", "context")
    for t in turns:
        # Rough word-count proxy: a 70-token turn is ~50-60 words
        assert len(t["message"].split()) <= 100, f"{t['agent']} too long"
