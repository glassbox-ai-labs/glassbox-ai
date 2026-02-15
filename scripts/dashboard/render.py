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

    def _render_success_chart(self, agent_issues: List[Dict]) -> str:
        """SVG line chart: cumulative success rate over time."""
        sorted_issues = sorted(agent_issues, key=lambda x: x.get("created_at", ""))
        if not sorted_issues:
            return ""
        points = []
        total = 0
        merged = 0
        for i in sorted_issues:
            total += 1
            if i["outcome"] == "merged":
                merged += 1
            rate = (merged / total) * 100
            points.append((total, rate))

        w, h = 700, 220
        pad_l, pad_r, pad_t, pad_b = 50, 20, 20, 40
        chart_w = w - pad_l - pad_r
        chart_h = h - pad_t - pad_b
        max_x = max(total, 1)

        def sx(v):
            return pad_l + (v / max_x) * chart_w

        def sy(v):
            return pad_t + chart_h - (v / 100) * chart_h

        # Grid lines + labels
        grid = ""
        for pct in [0, 25, 50, 75, 100]:
            y = sy(pct)
            grid += f'<line x1="{pad_l}" y1="{y}" x2="{w - pad_r}" y2="{y}" stroke="#21262d" stroke-width="1"/>'
            grid += f'<text x="{pad_l - 8}" y="{y + 4}" fill="#8b949e" font-size="11" text-anchor="end">{pct}%</text>'

        # X-axis labels
        for i in range(0, max_x + 1, max(1, max_x // 5)):
            x = sx(i)
            grid += f'<text x="{x}" y="{h - 5}" fill="#8b949e" font-size="11" text-anchor="middle">#{i}</text>'

        # Line path
        path_d = ""
        for idx, (xi, yi) in enumerate(points):
            cmd = "M" if idx == 0 else "L"
            path_d += f"{cmd}{sx(xi):.1f},{sy(yi):.1f} "

        # Area fill
        area_d = path_d + f"L{sx(points[-1][0]):.1f},{sy(0):.1f} L{sx(points[0][0]):.1f},{sy(0):.1f} Z"

        # Dots for each data point
        dots = ""
        for xi, yi in points:
            color = "#2ea043" if yi >= 50 else "#d29922" if yi >= 30 else "#d73a49"
            dots += f'<circle cx="{sx(xi):.1f}" cy="{sy(yi):.1f}" r="4" fill="{color}" stroke="#0d1117" stroke-width="2"/>'

        # Current rate annotation
        cur_rate = points[-1][1]
        rate_color = "#2ea043" if cur_rate >= 50 else "#d29922" if cur_rate >= 30 else "#d73a49"

        return f"""
        <div style="margin:24px 0">
            <h2 style="border-bottom:1px solid #30363d;padding-bottom:8px">&#x1f4c8; Success Rate Over Time</h2>
            <div style="background:#161b22;border-radius:12px;padding:20px;margin-top:12px">
                <svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">
                    {grid}
                    <path d="{area_d}" fill="url(#successGrad)" opacity="0.3"/>
                    <path d="{path_d}" fill="none" stroke="{rate_color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                    {dots}
                    <defs>
                        <linearGradient id="successGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="{rate_color}" stop-opacity="0.4"/>
                            <stop offset="100%" stop-color="{rate_color}" stop-opacity="0.0"/>
                        </linearGradient>
                    </defs>
                </svg>
                <div style="text-align:center;margin-top:8px;font-size:13px;color:#8b949e">
                    Issue # (chronological) &mdash; Current: <span style="color:{rate_color};font-weight:700">{cur_rate:.0f}%</span>
                </div>
            </div>
        </div>"""

    def _render_funnel(self, agent_issues: List[Dict]) -> str:
        """SVG conversion funnel: total → assigned → analyzed → tested → merged."""
        total = len(agent_issues)
        if total == 0:
            return ""
        assigned = total  # all were assigned
        analyzed = sum(1 for i in agent_issues if i.get("comment_count", 0) >= 1)
        tested = sum(1 for i in agent_issues if i["outcome"] in ("merged", "open_pr", "closed"))
        merged = sum(1 for i in agent_issues if i["outcome"] == "merged")

        stages = [
            ("Assigned", assigned, "#58a6ff"),
            ("Analyzed", analyzed, "#79c0ff"),
            ("PR Created", tested, "#d29922"),
            ("Merged", merged, "#2ea043"),
        ]

        w, h_per = 600, 52
        total_h = len(stages) * h_per + 20
        bars = ""
        for idx, (label, count, color) in enumerate(stages):
            pct = (count / total * 100) if total > 0 else 0
            bar_w = max(40, (count / total) * (w - 160)) if total > 0 else 40
            y = idx * h_per + 10
            x_start = (w - 160 - bar_w) / 2 + 80
            bars += f"""
                <rect x="{x_start:.0f}" y="{y}" width="{bar_w:.0f}" height="36" rx="6" fill="{color}" opacity="0.85"/>
                <text x="{w // 2}" y="{y + 23}" fill="#fff" font-size="13" font-weight="600" text-anchor="middle">{label}: {count} ({pct:.0f}%)</text>"""

        success_pct = (merged / total * 100) if total > 0 else 0
        rate_color = "#2ea043" if success_pct >= 50 else "#d29922" if success_pct >= 30 else "#d73a49"

        return f"""
        <div style="margin:24px 0">
            <h2 style="border-bottom:1px solid #30363d;padding-bottom:8px">&#x1f4ca; Conversion Funnel</h2>
            <div style="background:#161b22;border-radius:12px;padding:20px;margin-top:12px;text-align:center">
                <svg width="{w}" height="{total_h}" viewBox="0 0 {w} {total_h}">
                    {bars}
                </svg>
                <div style="margin-top:12px;font-size:22px;font-weight:700;color:{rate_color}">
                    {success_pct:.0f}% End-to-End Success
                </div>
                <div style="font-size:13px;color:#8b949e;margin-top:4px">{merged} merged out of {total} assigned</div>
            </div>
        </div>"""

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
    <title>GlassBox Agent - Real-time Performance Tracking</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>💎</text></svg>">
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
        <h1>&#x1f4ca; GlassBox Agent v0.3 - Real-time Performance Tracking</h1>
        <div class="subtitle">Live tracking of every issue, PR, workflow run, and failure pattern &mdash; <a href="https://github.com/{REPO}" style="color:#58a6ff">github.com/{REPO}</a></div>

        <div class="metrics">
            {self._render_metric_card("&#x1f41b;", "Agent Issues", str(m["total_agent"]), "#1a2332")}
            {self._render_metric_card("&#x2705;", "PRs Merged", str(m["merged"]), "#122117")}
            {self._render_metric_card("&#x274c;", "Failed", str(m["failed"]), "#2d1215")}
            {self._render_metric_card("&#x1f4c8;", "Success Rate", f"{m['success_rate']:.0f}%", "#1a2332")}
            {self._render_metric_card("&#x1f3f7;&#xfe0f;", "Via Label", str(m["by_label"]), "#1a2332")}
            {self._render_metric_card("&#x1f4ac;", "Via @mention", str(m["by_mention"]), "#1a2332")}
            {self._render_metric_card("&#x26a1;", "Workflow Runs", str(m["total_runs"]), "#1a2332")}
        </div>

        {self._render_success_chart(agent_issues_sorted)}
        {self._render_funnel(agent_issues_sorted)}

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
