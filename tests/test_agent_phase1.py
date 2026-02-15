"""Phase 1 tests: package skeleton, constants, settings, models."""

import pytest
from glassbox_agent import __version__
from glassbox_agent.core.constants import HARD_ASPECTS, HARD_CHALLENGES, TEST_PATTERNS
from glassbox_agent.core.settings import Settings
from glassbox_agent.core.models import TriageResult, EdgeCase, LineEdit, Fix, TestResult, TestFailure


class TestPackage:
    def test_version_exists(self):
        assert __version__ == "2.0.0-alpha"


class TestConstants:
    def test_hard_aspects_count(self):
        assert len(HARD_ASPECTS) == 5

    def test_hard_aspects_ids(self):
        ids = [a["id"] for a in HARD_ASPECTS]
        assert ids == ["HA1", "HA2", "HA3", "HA4", "HA5"]

    def test_hard_challenges_count(self):
        assert len(HARD_CHALLENGES) == 5

    def test_hard_challenges_ids(self):
        ids = [c["id"] for c in HARD_CHALLENGES]
        assert ids == ["HC1", "HC2", "HC3", "HC4", "HC5"]

    def test_test_patterns_count(self):
        assert len(TEST_PATTERNS) == 3

    def test_constants_are_frozen(self):
        with pytest.raises(AttributeError):
            HARD_ASPECTS.append({"id": "HA6"})


class TestSettings:
    def test_defaults(self):
        s = Settings()
        assert s.model == "gpt-4o"
        assert s.max_retries == 2
        assert s.temperature_code == 0.1
        assert s.repo == "agentic-trust-labs/glassbox-ai"

    def test_override(self):
        s = Settings(model="gpt-4o-mini", max_retries=5)
        assert s.model == "gpt-4o-mini"
        assert s.max_retries == 5


class TestModels:
    def test_edge_case(self):
        ec = EdgeCase(tier="T1", scenario="get_trust('unknown')", expected="returns 0.85")
        assert ec.tier == "T1"

    def test_line_edit(self):
        le = LineEdit(file="src/glassbox/trust_db.py", start_line=28, end_line=28, new_text="return result[0] if result else 0.85")
        assert le.start_line == 28

    def test_line_edit_invalid_line(self):
        with pytest.raises(Exception):
            LineEdit(file="f.py", start_line=0, end_line=1, new_text="x")

    def test_fix(self):
        f = Fix(edits=[], summary="fix trust default", strategy="single value change")
        assert f.summary == "fix trust default"

    def test_triage_result(self):
        tr = TriageResult(template_id="wrong_value", confidence=0.95)
        assert tr.difficulty == "easy"
        assert tr.skip_reason is None

    def test_triage_result_with_edge_cases(self):
        ec = EdgeCase(tier="T1", scenario="test", expected="pass")
        tr = TriageResult(template_id="typo_fix", confidence=0.8, edge_cases=[ec])
        assert len(tr.edge_cases) == 1

    def test_test_result_pass(self):
        r = TestResult(passed=True, total=22)
        assert r.passed
        assert r.failures == []

    def test_test_result_fail(self):
        f = TestFailure(test_name="test_02", message="0.50 != 0.85")
        r = TestResult(passed=False, total=22, failures=[f])
        assert not r.passed
        assert len(r.failures) == 1

    def test_confidence_bounds(self):
        with pytest.raises(Exception):
            TriageResult(template_id="x", confidence=1.5)
        with pytest.raises(Exception):
            TriageResult(template_id="x", confidence=-0.1)
