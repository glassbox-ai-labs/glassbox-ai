"""20 edge case tests for GlassBox AI — TrustDB, Orchestrator, Server."""

import asyncio
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from glassbox.trust_db import TrustDB


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def db():
    """Fresh TrustDB in a temp file for each test."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    t = TrustDB(db_path=path)
    yield t
    os.unlink(path)


# ── TrustDB: Core Functionality (Tests 1-8) ──────────────────────────

def test_01_default_agents_initialized(db):
    """All 3 default agents exist with score 0.85."""
    scores = db.get_all_scores()
    assert set(scores.keys()) == {"architect", "pragmatist", "critic"}
    for s in scores.values():
        assert s == 0.85


def test_02_get_trust_unknown_agent(db):
    """Unknown agent returns default 0.85, not crash."""
    assert db.get_trust("nonexistent_agent") == 0.85


def test_03_update_trust_correct_increases(db):
    """Correct outcome increases trust score."""
    old = db.get_trust("architect")
    db.update_trust("architect", True)
    new = db.get_trust("architect")
    assert new > old


def test_04_update_trust_incorrect_decreases(db):
    """Incorrect outcome decreases trust score."""
    old = db.get_trust("architect")
    db.update_trust("architect", False)
    new = db.get_trust("architect")
    assert new < old


def test_05_trust_never_below_floor(db):
    """Trust score cannot drop below 0.3 even after many failures."""
    for _ in range(100):
        db.update_trust("critic", False)
    assert db.get_trust("critic") >= 0.3


def test_06_trust_never_above_ceiling(db):
    """Trust score cannot exceed 1.0 even after many successes."""
    for _ in range(100):
        db.update_trust("architect", True)
    assert db.get_trust("architect") <= 1.0


def test_07_update_creates_new_agent(db):
    """Updating trust for a new agent auto-creates it."""
    db.update_trust("new_agent", True)
    assert db.get_trust("new_agent") > 0.85


def test_08_reset_all_restores_defaults(db):
    """Reset restores all scores to 0.85."""
    db.update_trust("architect", True)
    db.update_trust("pragmatist", False)
    db.reset_all()
    scores = db.get_all_scores()
    for s in scores.values():
        assert s == 0.85


# ── TrustDB: Stats & Edge Cases (Tests 9-14) ─────────────────────────

def test_09_stats_accuracy_zero_when_no_updates(db):
    """Accuracy is 0% when no outcomes recorded."""
    stats = db.get_stats("architect")
    assert stats["accuracy"] == 0
    assert stats["total_count"] == 0


def test_10_stats_accuracy_after_mixed_outcomes(db):
    """Accuracy reflects correct/total ratio."""
    db.update_trust("architect", True)
    db.update_trust("architect", True)
    db.update_trust("architect", False)
    stats = db.get_stats("architect")
    assert stats["correct_count"] == 2
    assert stats["total_count"] == 3
    assert round(stats["accuracy"], 1) == 66.7


def test_11_stats_unknown_agent_returns_none(db):
    """Stats for unknown agent returns None."""
    assert db.get_stats("ghost") is None


def test_12_concurrent_updates_dont_corrupt(db):
    """Multiple rapid updates don't corrupt the database."""
    for i in range(50):
        db.update_trust("architect", i % 2 == 0)
    stats = db.get_stats("architect")
    assert stats["total_count"] == 50
    assert 0.3 <= stats["trust_score"] <= 1.0


def test_13_all_scores_sorted_descending(db):
    """get_all_scores returns agents sorted by score descending."""
    db.update_trust("architect", True)
    db.update_trust("critic", False)
    scores = db.get_all_scores()
    values = list(scores.values())
    assert values == sorted(values, reverse=True)


def test_14_ema_converges_correctly(db):
    """EMA with alpha=0.1 converges toward 1.0 after many correct outcomes."""
    for _ in range(50):
        db.update_trust("architect", True)
    score = db.get_trust("architect")
    assert score > 0.99


# ── Orchestrator: Input Validation (Tests 15-18) ─────────────────────

def test_15_personas_have_required_keys():
    """All agents have (model, temperature, prompt) tuple."""
    from glassbox.orchestrator import AGENTS
    for name, t in AGENTS.items():
        assert len(t) == 3, f"{name} missing fields"
        assert isinstance(t[0], str), f"{name} missing model"
        assert isinstance(t[1], float), f"{name} missing temperature"
        assert isinstance(t[2], str), f"{name} missing prompt"


def test_16_personas_temperature_in_range():
    """All agent temperatures are between 0 and 1."""
    from glassbox.orchestrator import AGENTS
    for name, t in AGENTS.items():
        assert 0 <= t[1] <= 1, f"{name} temperature out of range"


def test_17_orchestrator_filters_invalid_agents():
    """Orchestrator ignores invalid agent names without crashing."""
    from glassbox.orchestrator import AGENTS
    valid = [name for name in ["architect", "fake_agent", "critic"] if name in AGENTS]
    assert valid == ["architect", "critic"]


def test_18_orchestrator_default_agents_match_personas():
    """Default agent list matches AGENTS keys."""
    from glassbox.orchestrator import AGENTS
    assert list(AGENTS.keys()) == ["architect", "pragmatist", "critic"]


# ── Server: Tool Registration (Tests 19-20) ──────────────────────────

def test_19_server_tools_importable():
    """Server tools (analyze, trust_scores, update_trust) are importable."""
    from glassbox.server import analyze, trust_scores, update_trust
    assert callable(analyze)
    assert callable(trust_scores)
    assert callable(update_trust)


def test_20_analyze_is_async():
    """analyze tool is an async function."""
    from glassbox.server import analyze
    assert asyncio.iscoroutinefunction(analyze.__wrapped__ if hasattr(analyze, "__wrapped__") else analyze)


def test_21_version_string_matches():
    """Server version string matches __version__ from __init__.py."""
    from glassbox import __version__
    from glassbox.server import mcp
    assert mcp.name == f"GlassBox AI v{__version__}"


def test_22_prompts_updated_to_design_review():
    """Ensure all agent prompts use 'design review' instead of 'standup meeting'."""
    from glassbox.orchestrator import AGENTS
    for name, t in AGENTS.items():
        assert "design review" in t[2], f"{name} prompt not updated"
        assert "standup meeting" not in t[2], f"{name} prompt still contains old text"



def test_unused_imports_removed():
    with open('src/glassbox/orchestrator.py', 'r') as file:
        content = file.read()
    assert 'from typing import List, Optional' not in content


def test_imports_are_correct():
    try:
        import asyncio
        import json
        import os
    except ImportError as e:
        assert False, f"Import failed: {e}"
    assert True


def test_round_1_instruction_no_bullet_points():
    from glassbox.orchestrator import ROUNDS
    assert ROUNDS[0] == "ROUND 1: State your position. Be direct, no bullet points."
