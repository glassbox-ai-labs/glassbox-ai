"""Renders the HTML dashboard from fetched data."""

import html
from datetime import datetime, timezone
from typing import Dict, List

from .config import REPO


class DashboardRenderer:
    """Generates a complete HTML dashboard from agent data."""

    def __init__(self, data: Dict):
        self._data = data
        self._now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    def _esc(self, text: str) -> str:
        return html.escape(str(text))

    def _metrics(self) -> Dict:
        agent = self._data["agent_issues"]
        prs = self._data["prs"]
        runs = self._data["runs"]

        total_agent = len(agent)
        merged = sum(1 for i in agent if i["outcome"] == "merged")
        failed = sum(1 for i in agent if i["outcome"] in ("failed", "closed"))
        open_pr = sum(1 for i in agent if i["outcome"] == "open_pr")
        by_label = sum(1 for i in agent if i["trigger"] == "label")
        by_mention = sum(1 for i in agent if i["trigger"] == "mention")

        success_rate = (merged / total_agent * 100) if total_agent > 0 else 0

        total_runs = len(runs)
        run_success = sum(1 for r in runs if r.get("conclusion") == "success")
        run_fail = sum(1 for r in runs if r.get("conclusion") == "failure")
        run_skip = sum(1 for r in runs if r.get("conclusion") == "skipped")

        # Failure pattern analysis
        patterns = {}
        for i in agent:
            msg = i.get("failure_msg", "")
            if not msg:
                continue
            if "IndentationError" in msg:
                patterns.setdefault("IndentationError", []).append(i["number"])
            elif "OperationalError" in msg or "SQL" in msg.lower() or "DEFAULT_TRUST" in msg:
                patterns.setdefault("Python var in SQL string", []).append(i["number"])
            elif "AttributeError" in msg:
                patterns.setdefault("AttributeError (bad test)", []).append(i["number"])
            elif "SyntaxError" in msg or "Syntax error" in msg:
                patterns.setdefault("SyntaxError", []).append(i["number"])
            elif "Tests failed" in msg:
                patterns.setdefault("Test failure", []).append(i["number"])
            elif "Debate could not approve" in msg:
                patterns.setdefault("Debate rejection", []).append(i["number"])
            else:
                patterns.setdefault("Other", []).append(i["number"])

        return {
            "total_agent": total_agent,
            "merged": merged,
            "failed": failed,
            "open_pr": open_pr,
            "by_label": by_label,
            "by_mention": by_mention,
            "success_rate": success_rate,
            "total_runs": total_runs,
            "run_success": run_success,
            "run_fail": run_fail,
            "run_skip": run_skip,
            "patterns": patterns,
        }

    def _render_metric_card(self, emoji: str, label: str, value: str, color: str) -> str:
        return f"""
        <div style="background:{color};border-radius:12px;padding:20px 24px;min-width:160px;text-align:center">
            <div style="font-size:28px">{emoji}</div>
            <div style="font-size:32px;font-weight:700;margin:4px 0">{value}</div>
            <div style="font-size:13px;opacity:0.8">{label}</div>
        </div>"""

    def _render_issue_row(self, issue: Dict) -> str:
        n = issue["number"]
        title = self._esc(issue["title"][:60])
        url = issue.get("html_url", f"https://github.com/{REPO}/issues/{n}")
        state = issue.get("state", "")
        trigger = issue.get("trigger", "none")
        outcome = issue.get("outcome", "not_triggered")

        # Linked PR
        pr = issue.get("linked_pr")
        pr_cell = "-"
        if pr:
            pr_num = pr["number"]
            pr_url = pr.get("html_url", f"https://github.com/{REPO}/pull/{pr_num}")
            pr_state = "merged" if pr.get("merged_at") else pr["state"]
            pr_color = "#2ea043" if pr_state == "merged" else ("#d73a49" if pr_state == "closed" else "#0969da")
            pr_cell = f'<a href="{pr_url}" style="color:{pr_color};font-weight:600">#{pr_num} ({pr_state})</a>'

        # Outcome styling
        outcome_map = {
            "merged": ("&#x2705;", "#2ea043", "Merged"),
            "closed": ("&#x274c;", "#d73a49", "Closed"),
            "failed": ("&#x274c;", "#d73a49", "Failed"),
            "open_pr": ("&#x1f7e1;", "#d29922", "Open PR"),
            "not_triggered": ("&#x2796;", "#666", "Not triggered"),
        }
        o_emoji, o_color, o_label = outcome_map.get(outcome, ("?", "#666", outcome))

        # Trigger styling
        trigger_map = {
            "label": ("&#x1f3f7;&#xfe0f;", "Label"),
            "mention": ("&#x1f4ac;", "@mention"),
            "none": ("&#x2796;", "-"),
        }
        t_emoji, t_label = trigger_map.get(trigger, ("-", trigger))

        # Failure excerpt
        fail_msg = issue.get("failure_msg", "")
        fail_cell = "-"
        if fail_msg:
            # Extract key error line
            lines = fail_msg.split("\n")
            error_line = ""
            for line in lines:
                if "Error" in line or "error" in line or "FAILED" in line:
                    error_line = line.strip()[:80]
                    break
            if not error_line:
                error_line = lines[0][:80] if lines else ""
            fail_cell = f'<span style="color:#d73a49;font-size:12px">{self._esc(error_line)}</span>'

        return f"""
        <tr>
            <td><a href="{url}" style="color:#0969da;font-weight:600">#{n}</a></td>
            <td>{title}</td>
            <td>{t_emoji} {t_label}</td>
            <td style="color:{o_color};font-weight:600">{o_emoji} {o_label}</td>
            <td>{pr_cell}</td>
            <td>{fail_cell}</td>
        </tr>"""

    def _render_pr_row(self, pr: Dict) -> str:
        n = pr["number"]
        title = self._esc(pr["title"][:60])
        url = pr.get("html_url", f"https://github.com/{REPO}/pull/{n}")
        branch = self._esc(pr.get("head", ""))
        merged = pr.get("merged_at")
        state = "merged" if merged else pr["state"]

        state_map = {
            "merged": ("&#x2705;", "#2ea043", "Merged"),
            "closed": ("&#x274c;", "#d73a49", "Closed"),
            "open": ("&#x1f7e2;", "#2ea043", "Open"),
        }
        s_emoji, s_color, s_label = state_map.get(state, ("?", "#666", state))

        return f"""
        <tr>
            <td><a href="{url}" style="color:#0969da;font-weight:600">#{n}</a></td>
            <td>{title}</td>
            <td><code>{branch}</code></td>
            <td style="color:{s_color};font-weight:600">{s_emoji} {s_label}</td>
        </tr>"""

    def _render_run_row(self, run: Dict) -> str:
        rid = run["id"]
        url = run.get("html_url", f"https://github.com/{REPO}/actions/runs/{rid}")
        title = self._esc(run.get("display_title", "")[:50])
        event = run.get("event", "")
        conclusion = run.get("conclusion") or "running"
        created = run.get("created_at", "")[:16].replace("T", " ")

        c_map = {
            "success": ("&#x2705;", "#2ea043"),
            "failure": ("&#x274c;", "#d73a49"),
            "skipped": ("&#x23ed;&#xfe0f;", "#888"),
            "running": ("&#x1f535;", "#0969da"),
        }
        c_emoji, c_color = c_map.get(conclusion, ("?", "#666"))

        return f"""
        <tr>
            <td><a href="{url}" style="color:#0969da">{rid}</a></td>
            <td>{title}</td>
            <td>{event}</td>
            <td style="color:{c_color};font-weight:600">{c_emoji} {conclusion}</td>
            <td>{created}</td>
        </tr>"""

    def render(self) -> str:
        m = self._metrics()
        agent_issues = self._data["agent_issues"]
        prs = self._data["prs"]
        runs = self._data["runs"]

        # Sort: most recent first
        agent_issues_sorted = sorted(agent_issues, key=lambda x: x["number"], reverse=True)
        prs_sorted = sorted(prs, key=lambda x: x["number"], reverse=True)
        runs_sorted = sorted(runs, key=lambda x: x.get("created_at", ""), reverse=True)[:50]

        # Build pattern rows
        pattern_rows = ""
        for pattern, issue_nums in sorted(m["patterns"].items(), key=lambda x: -len(x[1])):
            count = len(issue_nums)
            nums_str = ", ".join(f'<a href="https://github.com/{REPO}/issues/{n}" style="color:#0969da">#{n}</a>' for n in issue_nums)
            bar_width = min(count * 40, 200)
            pattern_rows += f"""
            <tr>
                <td style="font-weight:600">{self._esc(pattern)}</td>
                <td>{count}</td>
                <td><div style="background:#d73a49;height:16px;width:{bar_width}px;border-radius:4px;display:inline-block"></div></td>
                <td>{nums_str}</td>
            </tr>"""

        issue_rows = "".join(self._render_issue_row(i) for i in agent_issues_sorted)
        pr_rows = "".join(self._render_pr_row(p) for p in prs_sorted)
        run_rows = "".join(self._render_run_row(r) for r in runs_sorted)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GlassBox Agent Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; background: #0d1117; color: #e6edf3; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
        h1 {{ font-size: 28px; margin-bottom: 4px; }}
        .subtitle {{ color: #8b949e; margin-bottom: 24px; font-size: 14px; }}
        .metrics {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 32px; }}
        h2 {{ font-size: 20px; margin: 32px 0 12px 0; padding-bottom: 8px; border-bottom: 1px solid #30363d; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 24px; }}
        th {{ text-align: left; padding: 10px 12px; background: #161b22; border-bottom: 2px solid #30363d; font-size: 13px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #21262d; font-size: 14px; }}
        tr:hover {{ background: #161b22; }}
        a {{ text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        code {{ background: #161b22; padding: 2px 6px; border-radius: 4px; font-size: 12px; color: #79c0ff; }}
        .updated {{ color: #8b949e; font-size: 12px; text-align: right; margin-top: 16px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>&#x1f4ca; GlassBox Agent .3 - Dashboard</h1>
        <div class="subtitle">Autonomous bug fixer - live tracking of all issues, PRs, workflow runs, and failure patterns</div>

        <div class="metrics">
            {self._render_metric_card("&#x1f41b;", "Agent Issues", str(m["total_agent"]), "#1a2332")}
            {self._render_metric_card("&#x2705;", "PRs Merged", str(m["merged"]), "#122117")}
            {self._render_metric_card("&#x274c;", "Failed", str(m["failed"]), "#2d1215")}
            {self._render_metric_card("&#x1f4c8;", "Success Rate", f"{m['success_rate']:.0f}%", "#1a2332")}
            {self._render_metric_card("&#x1f3f7;&#xfe0f;", "Via Label", str(m["by_label"]), "#1a2332")}
            {self._render_metric_card("&#x1f4ac;", "Via @mention", str(m["by_mention"]), "#1a2332")}
            {self._render_metric_card("&#x26a1;", "Workflow Runs", str(m["total_runs"]), "#1a2332")}
        </div>

        <h2>&#x1f6a8; Failure Patterns</h2>
        <table>
            <tr><th>Pattern</th><th>Count</th><th>Frequency</th><th>Issues</th></tr>
            {pattern_rows if pattern_rows else "<tr><td colspan='4' style='color:#8b949e'>No failures recorded</td></tr>"}
        </table>

        <h2>&#x1f41b; Agent Issues</h2>
        <table>
            <tr><th>#</th><th>Title</th><th>Trigger</th><th>Outcome</th><th>PR</th><th>Error</th></tr>
            {issue_rows if issue_rows else "<tr><td colspan='6' style='color:#8b949e'>No agent issues</td></tr>"}
        </table>

        <h2>&#x1f500; Pull Requests</h2>
        <table>
            <tr><th>#</th><th>Title</th><th>Branch</th><th>Status</th></tr>
            {pr_rows if pr_rows else "<tr><td colspan='4' style='color:#8b949e'>No PRs</td></tr>"}
        </table>

        <h2>&#x26a1; Workflow Runs (last 50)</h2>
        <table>
            <tr><th>Run ID</th><th>Title</th><th>Event</th><th>Result</th><th>Time</th></tr>
            {run_rows}
        </table>

        <div class="updated">Last updated: {self._now} | Generated by scripts/dashboard/generate.py</div>
    </div>
</body>
</html>"""
