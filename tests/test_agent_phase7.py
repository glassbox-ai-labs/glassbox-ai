"""Phase 7 tests: TestRunner + Tester agent."""

import pytest
from unittest.mock import MagicMock, patch

from glassbox_agent.agents.tester import Tester
from glassbox_agent.core.models import EdgeCase, Fix, LineEdit, TestResult, TestFailure
from glassbox_agent.core.settings import Settings
from glassbox_agent.tools.github_client import GitHubClient
from glassbox_agent.tools.test_runner import TestRunner


class TestTestRunnerParse:
    def test_parse_all_passed(self):
        runner = TestRunner("/tmp")
        output = "tests/test_glassbox.py::test_01 PASSED\n===== 22 passed in 0.5s ====="
        result = runner._parse_output(output, passed=True)
        assert result.passed
        assert result.total == 22
        assert result.failures == []

    def test_parse_with_failures(self):
        runner = TestRunner("/tmp")
        output = (
            "FAILED tests/test_glassbox.py::test_02 - assert 0.50 == 0.85\n"
            "===== 1 failed, 21 passed in 0.5s ====="
        )
        result = runner._parse_output(output, passed=False)
        assert not result.passed
        assert result.total == 22
        assert len(result.failures) == 1
        assert result.failures[0].test_name == "test_02"
        assert "0.50" in result.failures[0].message

    def test_parse_no_summary(self):
        runner = TestRunner("/tmp")
        result = runner._parse_output("some random output", passed=False)
        assert not result.passed
        assert len(result.failures) == 1  # fallback failure

    def test_parse_multiple_failures(self):
        runner = TestRunner("/tmp")
        output = (
            "FAILED tests/test_a.py::test_x - error x\n"
            "FAILED tests/test_b.py::test_y - error y\n"
            "===== 2 failed, 10 passed in 1s ====="
        )
        result = runner._parse_output(output, passed=False)
        assert len(result.failures) == 2
        assert result.total == 12


class TestTesterAgent:
    def setup_method(self):
        self.client = MagicMock()
        self.github = MagicMock(spec=GitHubClient)
        self.settings = Settings()
        self.runner = MagicMock(spec=TestRunner)
        self.tester = Tester(
            client=self.client, github=self.github,
            settings=self.settings, test_runner=self.runner,
        )

    def test_validate_all_pass(self):
        self.runner.syntax_check.return_value = (True, "")
        self.runner.run_tests.return_value = TestResult(passed=True, total=22, output="22 passed")
        fix = Fix(edits=[LineEdit(file="f.py", start_line=5, end_line=5, new_text="x")],
                  summary="s", strategy="st")
        result = self.tester.validate(fix, [])
        assert result.passed
        assert result.diff_lines == 1

    def test_validate_syntax_fail(self):
        self.runner.syntax_check.return_value = (False, "SyntaxError line 12")
        fix = Fix(edits=[], summary="s", strategy="st")
        result = self.tester.validate(fix, [])
        assert not result.passed
        assert "TP1" in result.output

    def test_validate_test_fail(self):
        self.runner.syntax_check.return_value = (True, "")
        self.runner.run_tests.return_value = TestResult(
            passed=False, total=22, output="1 failed",
            failures=[TestFailure(test_name="test_02", message="assert fail")],
        )
        fix = Fix(edits=[LineEdit(file="f.py", start_line=1, end_line=1, new_text="x")],
                  summary="s", strategy="st")
        result = self.tester.validate(fix, [])
        assert not result.passed

    def test_think_and_act(self):
        assert "Running" in self.tester.think({})

    def test_diff_lines_counted(self):
        self.runner.syntax_check.return_value = (True, "")
        self.runner.run_tests.return_value = TestResult(passed=True, total=10, output="")
        fix = Fix(edits=[
            LineEdit(file="a.py", start_line=1, end_line=3, new_text="x"),
            LineEdit(file="b.py", start_line=5, end_line=5, new_text="y"),
        ], summary="s", strategy="st")
        result = self.tester.validate(fix, [])
        assert result.diff_lines == 4  # 3 + 1


class TestTesterReport:
    def setup_method(self):
        self.tester = Tester(
            client=MagicMock(), github=MagicMock(spec=GitHubClient),
            settings=Settings(), test_runner=MagicMock(spec=TestRunner),
        )

    def test_report_all_pass(self):
        result = TestResult(passed=True, total=22, diff_lines=1, output="22 passed")
        edge_cases = [
            EdgeCase(tier="T1", scenario="get_trust('unknown')", expected="0.85"),
            EdgeCase(tier="T4", scenario="get_trust('')", expected="fallback"),
        ]
        body = self.tester.format_report(result, edge_cases, max_diff_lines=3)
        assert "✅" in body
        assert "22 passed" in body
        assert "1 lines (max 3)" in body
        assert "T1" in body
        assert "T4" in body
        assert "Manager" in body

    def test_report_failure(self):
        result = TestResult(
            passed=False, total=22, diff_lines=1, output="1 failed",
            failures=[TestFailure(test_name="test_02", message="0.50 != 0.85")],
        )
        body = self.tester.format_report(result, [])
        assert "❌" in body
        assert "test_02" in body
        assert "Junior Dev" in body

    def test_report_diff_warning(self):
        result = TestResult(passed=True, total=10, diff_lines=10, output="10 passed")
        body = self.tester.format_report(result, [], max_diff_lines=3)
        assert "⚠️" in body
        assert "10 lines" in body

    def test_report_no_edge_cases(self):
        result = TestResult(passed=True, total=5, diff_lines=1, output="5 passed")
        body = self.tester.format_report(result, [])
        assert "edge cases" not in body.lower() or "Manager" in body
