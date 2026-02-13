"""Integration tests — call real OpenAI API. Only run in CI on push to main (not fork PRs)."""

import asyncio
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Skip entire file if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set — skipping integration tests"
)

from glassbox.trust_db import TrustDB
from glassbox.orchestrator import MultiAgentOrchestrator


@pytest.fixture
def orch():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    o = MultiAgentOrchestrator()
    o.trust_db = TrustDB(db_path=path)
    yield o
    os.unlink(path)


def test_int_01_single_agent_responds(orch):
    """Single agent returns a non-empty response from GPT."""
    result = asyncio.get_event_loop().run_until_complete(
        orch.execute("What is 2+2?", ["architect"])
    )
    assert len(result["agent_responses"]) == 1
    assert len(result["agent_responses"][0]["response"]) > 0


def test_int_02_all_three_agents_respond(orch):
    """All 3 agents respond in parallel with non-empty text."""
    result = asyncio.get_event_loop().run_until_complete(
        orch.execute("Should I use Redis or Postgres for caching?")
    )
    assert len(result["agent_responses"]) == 3
    for r in result["agent_responses"]:
        assert len(r["response"]) > 10
        assert r["agent"] in ["architect", "pragmatist", "critic"]


def test_int_03_trust_scores_attached(orch):
    """Each response has a valid trust score."""
    result = asyncio.get_event_loop().run_until_complete(
        orch.execute("Explain microservices vs monolith", ["pragmatist"])
    )
    for r in result["agent_responses"]:
        assert 0.3 <= r["trust"] <= 1.0


def test_int_04_consensus_is_nonempty(orch):
    """Consensus field contains real text from highest-trust agent."""
    result = asyncio.get_event_loop().run_until_complete(
        orch.execute("Best database for time-series data?")
    )
    assert len(result["consensus"]) > 20


def test_int_05_formatted_output(orch):
    """execute_formatted returns a readable string with all agent names."""
    output = asyncio.get_event_loop().run_until_complete(
        orch.execute_formatted("Compare Python vs Go for APIs")
    )
    assert "@architect" in output
    assert "@pragmatist" in output
    assert "@critic" in output
    assert "Consensus" in output
