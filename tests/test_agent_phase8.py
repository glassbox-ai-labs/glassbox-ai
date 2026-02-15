"""Phase 8 tests: CLI entry point + end-to-end integration test (mocked LLM + GitHub)."""

import json
import os
import pytest
from unittest.mock import MagicMock, patch, call

from glassbox_agent.core.settings import Settings
from glassbox_agent.core.template import TemplateLoader
from glassbox_agent.core.models import TriageResult, EdgeCase, Fix, LineEdit, TestResult
from glassbox_agent.memory.store import MemoryStore
from glassbox_agent.tools.github_client import GitHubClient
from glassbox_agent.tools.code_editor import CodeEditor
from glassbox_agent.tools.file_reader import FileReader
from glassbox_agent.tools.test_runner import TestRunner
from glassbox_agent.agents.manager import Manager
from glassbox_agent.agents.junior_dev import JuniorDev
from glassbox_agent.agents.tester import Tester


TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "glassbox_agent", "templates")


CLASSIFY_RESPONSE = json.dumps({
    "template_id": "wrong_value",
    "confidence": 0.95,
    "skip_reason": None,
    "soft_aspects": [{"id": "SA1", "name": "Cross-boundary safety", "reason": "SQL"}],
    "soft_challenges": [{"id": "SC1", "name": "Multi-occur", "risk": "0.85 appears twice"}],
    "edge_cases": [
        {"tier": "T1", "scenario": "get_trust('unknown') == 0.85", "expected": "returns 0.85"},
        {"tier": "T2", "scenario": "get_trust('critic')", "expected": "seeded value"},
    ],
})

FIX_RESPONSE = json.dumps({
    "edits": [{"file": "src/glassbox/trust_db.py", "start_line": 5, "end_line": 5,
               "new_text": "        return result[0] if result else 0.85\n"}],
    "test_code": "def test_fix(): assert True",
    "summary": "correct default trust from 0.50 to 0.85",
    "strategy": "Single value replacement",
})


class TestEndToEnd:
    """Integration test: Manager → JuniorDev → Tester → approval flow (all mocked)."""

    def test_happy_path(self, tmp_path):
        """Full pipeline: classify → fix → test → approve."""
        # Set up tmp repo with a bug
        src = tmp_path / "src" / "glassbox"
        src.mkdir(parents=True)
        (src / "__init__.py").write_text("__version__ = '0.3.0'\n")
        (src / "trust_db.py").write_text(
            "import sqlite3\n"
            "class TrustDB:\n"
            "    def get_trust(self, agent):\n"
            "        result = self.db.get(agent)\n"
            "        return result[0] if result else 0.50\n"
        )
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_glassbox.py").write_text("def test_placeholder(): pass\n")

        # Mock OpenAI: first call = classify, second call = fix
        client = MagicMock()
        responses = [
            MagicMock(choices=[MagicMock(message=MagicMock(content=CLASSIFY_RESPONSE))]),
            MagicMock(choices=[MagicMock(message=MagicMock(content=FIX_RESPONSE))]),
        ]
        client.chat.completions.create.side_effect = responses

        # Mock GitHub
        github = MagicMock(spec=GitHubClient)
        github.read_issue.return_value = (
            "[Bug] get_trust() returns 0.50 instead of 0.85",
            "Default is 0.50 but should be 0.85",
        )
        github.silent_update.return_value = 100
        github.post_comment.return_value = 200
        github.create_branch.return_value = None
        github.commit_and_push.return_value = None
        github.create_pr.return_value = "https://github.com/o/r/pull/49"
        github.add_reaction.return_value = True

        settings = Settings()
        loader = TemplateLoader(TEMPLATES_DIR)
        memory = MemoryStore()
        editor = CodeEditor(str(tmp_path))
        reader = FileReader(str(tmp_path))
        runner = MagicMock(spec=TestRunner)
        runner.syntax_check.return_value = (True, "")
        runner.run_tests.return_value = TestResult(passed=True, total=22, output="22 passed")

        # Create agents
        manager = Manager(client=client, github=github, settings=settings,
                          template_loader=loader, memory=memory)
        junior = JuniorDev(client=client, github=github, settings=settings,
                           editor=editor, file_reader=reader)
        tester = Tester(client=client, github=github, settings=settings,
                        test_runner=runner)

        # ── Run pipeline manually ──
        # Step 1: Read issue
        title, body = github.read_issue(42)

        # Step 2: Manager classifies
        sources = {}
        for f in reader.list_files((".py",)):
            if f.startswith("src/glassbox/"):
                ok, content = reader.read_raw(f)
                if ok:
                    sources[f] = content

        triage = manager.classify(42, title, body, sources)
        assert triage.template_id == "wrong_value"
        assert triage.confidence == 0.95
        assert len(triage.edge_cases) == 2

        template = loader.get(triage.template_id)
        assert template is not None

        # Step 3: Manager posts briefing
        briefing = manager.format_briefing(triage, template)
        assert "wrong_value" in briefing
        assert "HA1" in briefing
        assert "T1" in briefing

        # Step 4: JuniorDev generates + applies fix
        fix = junior.generate_fix(
            issue_number=42, title=title, body=body,
            template=template, triage=triage, sources=sources,
        )
        assert len(fix.edits) == 1
        assert "0.85" in fix.edits[0].new_text

        ok, err = junior.apply_fix(fix)
        assert ok, err

        # Verify file was actually changed
        content = (src / "trust_db.py").read_text()
        assert "0.85" in content
        assert "0.50" not in content

        # Step 5: Tester validates
        result = tester.validate(fix, triage.edge_cases)
        assert result.passed
        assert result.diff_lines == 1

        # Step 6: Format reports
        fix_comment = junior.format_comment(fix)
        assert "Got it" in fix_comment

        test_report = tester.format_report(result, triage.edge_cases, template.max_diff_lines)
        assert "✅" in test_report
        assert "T1" in test_report

    def test_skip_feature_request(self):
        """Manager should skip non-bug issues."""
        skip_response = json.dumps({
            "template_id": "typo_fix", "confidence": 0.3,
            "skip_reason": "feature_request",
            "soft_aspects": [], "soft_challenges": [], "edge_cases": [],
        })
        client = MagicMock()
        client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=skip_response))]
        )
        github = MagicMock(spec=GitHubClient)
        settings = Settings()
        loader = TemplateLoader(TEMPLATES_DIR)
        memory = MemoryStore()

        manager = Manager(client=client, github=github, settings=settings,
                          template_loader=loader, memory=memory)
        triage = manager.classify(42, "Add user profiles", "I want profiles", {})
        assert triage.skip_reason == "feature_request"

        briefing = manager.format_briefing(triage, loader.get("typo_fix"))
        assert "feature_request" in briefing
        assert "Junior Dev" not in briefing

    def test_retry_on_test_failure(self, tmp_path):
        """JuniorDev should retry when tests fail."""
        src = tmp_path / "src" / "glassbox"
        src.mkdir(parents=True)
        (src / "trust_db.py").write_text("line1\nline2\nline3\nline4\nreturn 0.50\n")

        client = MagicMock()
        fix_resp_1 = json.dumps({
            "edits": [{"file": "src/glassbox/trust_db.py", "start_line": 5, "end_line": 5,
                       "new_text": "return 0.85\n"}],
            "summary": "fix", "strategy": "replace", "test_code": "",
        })
        fix_resp_2 = json.dumps({
            "edits": [{"file": "src/glassbox/trust_db.py", "start_line": 5, "end_line": 5,
                       "new_text": "return 0.85\n"}],
            "summary": "fix v2", "strategy": "replace v2", "test_code": "",
        })
        classify_resp = CLASSIFY_RESPONSE
        client.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=MagicMock(content=classify_resp))]),
            MagicMock(choices=[MagicMock(message=MagicMock(content=fix_resp_1))]),
            MagicMock(choices=[MagicMock(message=MagicMock(content=fix_resp_2))]),
        ]

        github = MagicMock(spec=GitHubClient)
        settings = Settings()
        loader = TemplateLoader(TEMPLATES_DIR)
        editor = CodeEditor(str(tmp_path))
        reader = FileReader(str(tmp_path))

        junior = JuniorDev(client=client, github=github, settings=settings,
                           editor=editor, file_reader=reader)
        manager = Manager(client=client, github=github, settings=settings,
                          template_loader=loader, memory=MemoryStore())

        triage = manager.classify(42, "test", "body", {})
        template = loader.get(triage.template_id)

        sources = {"src/glassbox/trust_db.py": "line1\nline2\nline3\nline4\nreturn 0.50\n"}

        # Attempt 1
        fix1 = junior.generate_fix(42, "t", "b", template, triage, sources)
        assert fix1.summary == "fix"

        # Attempt 2 with feedback
        fix2 = junior.generate_fix(42, "t", "b", template, triage, sources,
                                    feedback="test_02 failed: 0.50 != 0.85")
        assert fix2.summary == "fix v2"
        prompt = client.chat.completions.create.call_args[1]["messages"][0]["content"]
        assert "PREVIOUS ATTEMPT FEEDBACK" in prompt


class TestAllPhasesImport:
    """Verify all modules import cleanly."""

    def test_import_all(self):
        import glassbox_agent
        import glassbox_agent.core.constants
        import glassbox_agent.core.settings
        import glassbox_agent.core.models
        import glassbox_agent.core.base_agent
        import glassbox_agent.core.template
        import glassbox_agent.agents.manager
        import glassbox_agent.agents.junior_dev
        import glassbox_agent.agents.tester
        import glassbox_agent.tools.github_client
        import glassbox_agent.tools.code_editor
        import glassbox_agent.tools.file_reader
        import glassbox_agent.tools.test_runner
        import glassbox_agent.memory.store
        import glassbox_agent.cli
        assert glassbox_agent.__version__ == "2.0.0-alpha"
