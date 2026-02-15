"""TestRunner — run pytest, parse results structurally."""

from __future__ import annotations

import re
import subprocess

from glassbox_agent.core.models import TestFailure, TestResult


class TestRunner:
    """Runs pytest and parses output into structured TestResult."""

    def __init__(self, repo_root: str):
        self._root = repo_root

    def syntax_check(self, module: str) -> tuple[bool, str]:
        """Check syntax by importing the module. Returns (ok, error)."""
        cmd = f"python -c \"import {module}\""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self._root)
        if result.returncode == 0:
            return True, ""
        return False, result.stderr.strip()

    def run_tests(self, test_path: str = "tests/", extra_args: str = "") -> TestResult:
        """Run pytest and parse output."""
        cmd = f"python -m pytest {test_path} -v --tb=short {extra_args}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self._root)
        output = result.stdout + "\n" + result.stderr
        return self._parse_output(output, result.returncode == 0)

    def _parse_output(self, output: str, passed: bool) -> TestResult:
        """Parse pytest output into structured TestResult."""
        total = 0
        failures: list[TestFailure] = []

        # Match summary line: "X passed" or "X passed, Y failed"
        summary_match = re.search(r"(\d+) passed", output)
        if summary_match:
            total += int(summary_match.group(1))
        failed_match = re.search(r"(\d+) failed", output)
        if failed_match:
            total += int(failed_match.group(1))

        # Parse individual failures: "FAILED tests/test_x.py::test_name - reason"
        for m in re.finditer(r"FAILED\s+([\w/.]+)::(\w+)\s*[-–]\s*(.*)", output):
            failures.append(TestFailure(
                file=m.group(1), test_name=m.group(2), message=m.group(3).strip(),
            ))

        # Fallback: if failures detected but not parsed, grab short tb
        if not passed and not failures:
            lines = output.strip().split("\n")
            last_lines = "\n".join(lines[-15:])
            failures.append(TestFailure(test_name="unknown", message=last_lines))

        return TestResult(passed=passed, total=total, failures=failures, output=output)
