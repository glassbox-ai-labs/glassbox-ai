"""Phase 4 tests: Manager agent + MemoryStore."""

import json
import os
import tempfile
import pytest
from unittest.mock import MagicMock

from glassbox_agent.agents.manager import Manager
from glassbox_agent.core.models import TriageResult, EdgeCase
from glassbox_agent.core.settings import Settings
from glassbox_agent.core.template import TemplateLoader
from glassbox_agent.memory.store import MemoryStore, Reflection
from glassbox_agent.tools.github_client import GitHubClient


TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "glassbox_agent", "templates")

MOCK_CLASSIFY_RESPONSE = json.dumps({
    "template_id": "wrong_value",
    "confidence": 0.95,
    "skip_reason": None,
    "soft_aspects": [{"id": "SA1", "name": "Cross-boundary safety", "reason": "SQL literal"}],
    "soft_challenges": [{"id": "SC1", "name": "Multiple occurrences", "risk": "0.85 appears twice"}],
    "edge_cases": [
        {"tier": "T1", "scenario": "get_trust('unknown') == 0.85", "expected": "returns 0.85"},
        {"tier": "T2", "scenario": "get_trust('critic')", "expected": "returns seeded value"},
        {"tier": "T3", "scenario": "get_trust(None)", "expected": "fallback works"},
        {"tier": "T4", "scenario": "get_trust('')", "expected": "returns fallback"},
    ],
})


def make_manager(llm_response=MOCK_CLASSIFY_RESPONSE):
    client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = llm_response
    client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])
    github = MagicMock(spec=GitHubClient)
    settings = Settings()
    loader = TemplateLoader(TEMPLATES_DIR)
    memory = MemoryStore()
    return Manager(client=client, github=github, settings=settings,
                   template_loader=loader, memory=memory)


class TestManagerClassify:
    def test_classify_returns_triage_result(self):
        m = make_manager()
        result = m.classify(42, "wrong default 0.50", "should be 0.85", {})
        assert isinstance(result, TriageResult)
        assert result.template_id == "wrong_value"
        assert result.confidence == 0.95

    def test_classify_has_edge_cases(self):
        m = make_manager()
        result = m.classify(42, "test", "body", {})
        assert len(result.edge_cases) == 4
        assert result.edge_cases[0].tier == "T1"

    def test_classify_has_soft_aspects(self):
        m = make_manager()
        result = m.classify(42, "test", "body", {})
        assert len(result.soft_aspects) == 1
        assert result.soft_aspects[0]["id"] == "SA1"

    def test_classify_has_soft_challenges(self):
        m = make_manager()
        result = m.classify(42, "test", "body", {})
        assert len(result.soft_challenges) == 1

    def test_classify_skip_reason(self):
        skip_response = json.dumps({
            "template_id": "typo_fix", "confidence": 0.3,
            "skip_reason": "feature_request",
            "soft_aspects": [], "soft_challenges": [], "edge_cases": [],
        })
        m = make_manager(skip_response)
        result = m.classify(42, "Add feature", "I want profiles", {})
        assert result.skip_reason == "feature_request"

    def test_classify_with_sources(self):
        m = make_manager()
        sources = {"src/glassbox/trust_db.py": "line1\nline2\nline3"}
        result = m.classify(42, "test", "body", sources)
        prompt_arg = m.client.chat.completions.create.call_args[1]["messages"][0]["content"]
        assert "trust_db.py" in prompt_arg
        assert "1: line1" in prompt_arg


class TestManagerBriefing:
    def test_format_briefing_happy_path(self):
        m = make_manager()
        triage = TriageResult(
            template_id="wrong_value", confidence=0.95,
            soft_aspects=[{"id": "SA1", "name": "Cross-boundary", "reason": "SQL"}],
            soft_challenges=[{"id": "SC1", "name": "Multi-occur", "risk": "appears twice"}],
            edge_cases=[
                EdgeCase(tier="T1", scenario="get_trust('unknown')", expected="0.85"),
                EdgeCase(tier="T4", scenario="get_trust('')", expected="fallback"),
            ],
        )
        template = m.templates.get("wrong_value")
        body = m.format_briefing(triage, template)
        assert "wrong_value" in body
        assert "HA1" in body
        assert "HC1" in body
        assert "SA1" in body
        assert "T1" in body
        assert "T4" in body
        assert "Junior Dev" in body

    def test_format_briefing_skip(self):
        m = make_manager()
        triage = TriageResult(template_id="typo_fix", confidence=0.3, skip_reason="feature_request")
        template = m.templates.get("typo_fix")
        body = m.format_briefing(triage, template)
        assert "feature_request" in body
        assert "Junior Dev" not in body

    def test_think_and_act(self):
        m = make_manager()
        assert "Classifying" in m.think({})
        result = m.act({"issue_number": 1, "title": "t", "body": "b"})
        assert isinstance(result, TriageResult)


class TestMemoryStore:
    def test_empty_store(self):
        ms = MemoryStore()
        assert ms.all() == []
        assert ms.format_for_prompt("test") == ""

    def test_save_and_query(self):
        ms = MemoryStore()
        r = Reflection(issue_number=1, issue_title="typo bug", template_id="typo_fix",
                       reflection="Hallucinated old string")
        ms.save_reflection(r)
        assert len(ms.all()) == 1
        results = ms.query("typo")
        assert len(results) == 1

    def test_query_no_match(self):
        ms = MemoryStore()
        r = Reflection(issue_number=1, issue_title="typo bug", reflection="bad")
        ms.save_reflection(r)
        assert ms.query("zzzzz") == []

    def test_persist_and_load(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            f.write("[]")
            path = f.name
        try:
            ms = MemoryStore(path)
            ms.save_reflection(Reflection(issue_number=1, issue_title="test", reflection="r"))
            ms2 = MemoryStore(path)
            assert len(ms2.all()) == 1
        finally:
            os.unlink(path)

    def test_format_for_prompt(self):
        ms = MemoryStore()
        ms.save_reflection(Reflection(issue_number=1, issue_title="trust default",
                                       template_id="wrong_value", reflection="Changed wrong line"))
        result = ms.format_for_prompt("trust issue")
        assert "PAST REFLECTIONS" in result
        assert "Changed wrong line" in result
