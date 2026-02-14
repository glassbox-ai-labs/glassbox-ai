"""GlassBox AI Agent .3 - GitHub API interactions."""

import json
import subprocess

from .config import REPO


def sh(cmd: str) -> subprocess.CompletedProcess:
    """Run shell command, return CompletedProcess."""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def gh_api(endpoint: str, method: str = "POST", data: dict | None = None) -> subprocess.CompletedProcess:
    """Call GitHub REST API via gh cli."""
    cmd = f"gh api {endpoint}"
    if method != "GET":
        cmd += f" -X {method}"
    if data:
        cmd += " --input -"
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, input=json.dumps(data))
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def read_issue(issue_number: int) -> tuple[str, str]:
    """Read issue title and body. Returns (title, body)."""
    result = sh(f"gh issue view {issue_number} --repo {REPO} --json title,body")
    issue = json.loads(result.stdout)
    return issue["title"], issue.get("body", "")


def post_comment(issue_number: int, body: str) -> None:
    """Post a comment on the issue."""
    gh_api(f"repos/{REPO}/issues/{issue_number}/comments", data={"body": body})
    print(f"  posted comment ({len(body)} chars)")


def create_branch(branch: str) -> None:
    """Delete old branch if exists, create fresh from main."""
    sh(f"git push origin --delete {branch} 2>/dev/null")
    sh(f"git branch -D {branch} 2>/dev/null")
    sh("git checkout main")
    sh("git clean -fd")
    sh("git checkout -- .")
    sh(f"git checkout -b {branch}")


def reset_branch(branch: str) -> None:
    """Reset branch to clean main state."""
    sh("git checkout main")
    sh("git clean -fd")
    sh("git checkout -- .")
    sh(f"git branch -D {branch} 2>/dev/null")
    sh(f"git checkout -b {branch}")


def commit_and_push(branch: str, message: str) -> None:
    """Stage all, commit, push."""
    sh("git add -A")
    subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True)
    sh(f"git push origin {branch}")


def create_pr(branch: str, issue_number: int, title: str, body: str) -> str:
    """Create PR via GitHub API. Returns PR URL."""
    payload = {"title": title, "body": body, "head": branch, "base": "main"}
    tmp = "/tmp/pr_payload.json"
    with open(tmp, "w") as f:
        json.dump(payload, f)
    result = sh(f"gh api repos/{REPO}/pulls --input {tmp}")
    import os
    os.remove(tmp)
    try:
        pr = json.loads(result.stdout)
        return pr.get("html_url") or pr.get("url") or ""
    except Exception:
        return f"https://github.com/{REPO}/compare/main...{branch}"
