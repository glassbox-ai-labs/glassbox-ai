"""Phase 6 tests: JuniorDev agent."""

import json
import os
import pytest
from unittest.mock import MagicMock

from glassbox_agent.agents.junior_dev import JuniorDev
from glassbox_agent.core.models import EdgeCase, Fix, LineEdit, TriageResult
from glassbox_agent.core.settings import Settings
from glassbox_agent.core.template import TemplateLoader
from glassbox_agent.tools.code_editor import CodeEditor
from glassbox_agent.tools.file_reader import FileReader
from glassbox_agent.tools.github_client import GitHubClient


TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "glassbox_agent", "templates")

MOCK_FIX_RESPONSE = json.dumps({
    "edits": [
        {"file": "src/glassbox/trust_db.py", "start_line": 5, "end_line": 5,
         "new_text": "        return result[0] if result else 0.85\n"}
    ],
    "test_code": "def test_trust_default():\n    assert True",
    "summary": "fix: correct default trust from 0.50 to 0.85",
    "strategy": "Single value replacement on line 5",
})


def make_junior_dev(llm_response=MOCK_FIX_RESPONSE, tmp_path=None):
    client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = llm_response
    client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])
    github = MagicMock(spec=GitHubClient)
    settings = Settings()
    root = str(tmp_path) if tmp_path else "/tmp"
    editor = CodeEditor(root)
    reader = FileReader(root)
    return JuniorDev(client=client, github=github, settings=settings, editor=editor, file_reader=reader)


class TestJuniorDevGenerate:
    def test_generate_fix_returns_fix(self):
        jd = make_junior_dev()
        loader = TemplateLoader(TEMPLATES_DIR)
        template = loader.get("wrong_value")
        triage = TriageResult(
            template_id="wrong_value", confidence=0.95,
            soft_aspects=[{"id": "SA1", "name": "Cross-boundary"}],
            soft_challenges=[{"id": "SC1", "name": "Multi", "risk": "appears twice"}],
            edge_cases=[EdgeCase(tier="T1", scenario="test", expected="pass")],
        )
        fix = jd.generate_fix(
            issue_number=42, title="wrong default", body="0.50 should be 0.85",
            template=template, triage=triage,
            sources={"src/glassbox/trust_db.py": "line1\nline2\nline3\nline4\nresult else 0.50\n"},
        )
        assert isinstance(fix, Fix)
        assert len(fix.edits) == 1
        assert fix.edits[0].start_line == 5
        assert "0.85" in fix.edits[0].new_text

    def test_generate_fix_includes_aspects_in_prompt(self):
        jd = make_junior_dev()
        loader = TemplateLoader(TEMPLATES_DIR)
        template = loader.get("wrong_value")
        triage = TriageResult(
            template_id="wrong_value", confidence=0.95,
            soft_aspects=[{"id": "SA1", "name": "Cross-boundary"}],
            soft_challenges=[], edge_cases=[],
        )
        jd.generate_fix(42, "t", "b", template, triage, {"f.py": "content"})
        prompt = jd.client.chat.completions.create.call_args[1]["messages"][0]["content"]
        assert "Cross-boundary" in prompt
        assert "wrong_value" in prompt

    def test_generate_fix_with_feedback(self):
        jd = make_junior_dev()
        loader = TemplateLoader(TEMPLATES_DIR)
        template = loader.get("typo_fix")
        triage = TriageResult(template_id="typo_fix", confidence=0.9)
        jd.generate_fix(42, "t", "b", template, triage, {"f.py": "c"}, feedback="Previous attempt broke tests")
        prompt = jd.client.chat.completions.create.call_args[1]["messages"][0]["content"]
        assert "PREVIOUS ATTEMPT FEEDBACK" in prompt
        assert "broke tests" in prompt

    def test_think_and_act(self):
        jd = make_junior_dev()
        assert "Reading" in jd.think({})


class TestJuniorDevApply:
    def test_apply_fix_success(self, tmp_path):
        src = tmp_path / "src" / "glassbox"
        src.mkdir(parents=True)
        (src / "trust_db.py").write_text(
            "line1\nline2\nline3\nline4\nreturn result[0] if result else 0.50\nline6\n"
        )
        jd = make_junior_dev(tmp_path=tmp_path)
        fix = Fix(
            edits=[LineEdit(file="src/glassbox/trust_db.py", start_line=5, end_line=5,
                            new_text="return result[0] if result else 0.85\n")],
            summary="fix", strategy="replace",
        )
        ok, err = jd.apply_fix(fix)
        assert ok, err
        content = (src / "trust_db.py").read_text()
        assert "0.85" in content
        assert "0.50" not in content

    def test_apply_fix_file_not_found(self, tmp_path):
        jd = make_junior_dev(tmp_path=tmp_path)
        fix = Fix(
            edits=[LineEdit(file="nope.py", start_line=1, end_line=1, new_text="x")],
            summary="fix", strategy="replace",
        )
        ok, err = jd.apply_fix(fix)
        assert not ok
        assert "not found" in err.lower()


class TestJuniorDevComment:
    def test_format_comment(self):
        jd = make_junior_dev()
        fix = Fix(
            edits=[LineEdit(file="src/glassbox/trust_db.py", start_line=5, end_line=5,
                            new_text="return result[0] if result else 0.85\n")],
            summary="fix default", strategy="Single value change",
        )
        body = jd.format_comment(fix)
        assert "Got it, boss" in body
        assert "trust_db.py" in body
        assert "0.85" in body
        assert "Tester" in body
        assert "Single value change" in body
