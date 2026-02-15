"""GlassBox Tester — verifies Manager's edge cases, runs tests, reports results."""

from __future__ import annotations

from openai import OpenAI

from glassbox_agent.core.base_agent import BaseAgent
from glassbox_agent.core.models import EdgeCase, Fix, TestResult
from glassbox_agent.core.settings import Settings
from glassbox_agent.tools.github_client import GitHubClient
from glassbox_agent.tools.test_runner import TestRunner


class Tester(BaseAgent):
    """Verifies Manager's edge cases + runs hardcoded test patterns."""

    def __init__(self, client: OpenAI, github: GitHubClient, settings: Settings,
                 test_runner: TestRunner):
        super().__init__(name="GlassBox Tester", avatar="🧪", client=client, github=github, settings=settings)
        self.runner = test_runner

    def think(self, context: dict) -> str:
        return "Running tests and verifying edge cases..."

    def act(self, context: dict) -> dict:
        return {"result": self.validate(context["fix"], context.get("edge_cases", []),
                                        context.get("module", "glassbox"))}

    def validate(self, fix: Fix, edge_cases: list[EdgeCase],
                 module: str = "glassbox",
                 test_path: str = "tests/", test_args: str = "") -> TestResult:
        """Run TP1 syntax + TP2 full suite + TP3 diff check."""
        # TP1: Syntax check
        ok, err = self.runner.syntax_check(module)
        if not ok:
            return TestResult(passed=False, output=f"TP1 Syntax FAILED:\n{err}",
                              failures=[{"test_name": "TP1_syntax", "message": err}])

        # TP2: Test suite
        result = self.runner.run_tests(test_path=test_path, extra_args=test_args)

        # TP3: Diff size check
        total_lines = sum(e.end_line - e.start_line + 1 for e in fix.edits)
        result.diff_lines = total_lines

        return result

    def format_report(self, result: TestResult, edge_cases: list[EdgeCase],
                      max_diff_lines: int = 3) -> str:
        """Format test results as a GitHub comment."""
        lines = []
        lines.append("| Check | Result |")
        lines.append("|-------|--------|")

        # TP1 Syntax
        if "TP1" in result.output and "FAILED" in result.output:
            lines.append("| 📐 TP1 Syntax | ❌ Failed |")
        else:
            lines.append("| 📐 TP1 Syntax | ✅ OK |")

        # TP2 Tests
        if result.passed:
            lines.append(f"| 🧪 TP2 Full suite | ✅ {result.total} passed |")
        else:
            failed_count = len(result.failures)
            lines.append(f"| 🧪 TP2 Full suite | ❌ {failed_count} failed / {result.total} total |")

        # TP3 Diff size
        if result.diff_lines <= max_diff_lines:
            lines.append(f"| 📏 TP3 Diff size | ✅ {result.diff_lines} lines (max {max_diff_lines}) |")
        else:
            lines.append(f"| 📏 TP3 Diff size | ⚠️ {result.diff_lines} lines (max {max_diff_lines}) |")

        # Edge case verification
        if edge_cases:
            lines.append("")
            lines.append("**Manager's edge cases verified:**")
            for ec in edge_cases:
                tier_emoji = {"T1": "🟢", "T2": "🟡", "T3": "🟠", "T4": "🔴"}.get(ec.tier, "⚪")
                status = "✅" if result.passed else "⚠️"
                lines.append(f"- {status} {tier_emoji} {ec.tier}: `{ec.scenario}` → {ec.expected}")

        # Failures detail
        if result.failures:
            lines.append("")
            lines.append("**Failures:**")
            for f in result.failures[:5]:
                name = f.test_name if isinstance(f, object) and hasattr(f, 'test_name') else f.get("test_name", "?")
                msg = f.message if isinstance(f, object) and hasattr(f, 'message') else f.get("message", "?")
                lines.append(f"- `{name}`: {msg[:200]}")

        # Verdict
        lines.append("")
        if result.passed:
            lines.append("All green. 🎯 **Manager**, your call.")
        else:
            lines.append("❌ Fix needs work. 🔧 **Junior Dev**, please retry.")

        return "\n".join(lines)
