"""GlassBox Agent v2 — CLI entry point. Replaces scripts/agent/main.py."""

from __future__ import annotations

import os
import sys
import traceback

from openai import OpenAI

from glassbox_agent.core.models import TestResult
from glassbox_agent.core.settings import Settings
from glassbox_agent.core.template import TemplateLoader
from glassbox_agent.memory.store import MemoryStore
from glassbox_agent.tools.github_client import GitHubClient
from glassbox_agent.tools.code_editor import CodeEditor
from glassbox_agent.tools.file_reader import FileReader
from glassbox_agent.tools.test_runner import TestRunner
from glassbox_agent.agents.manager import Manager
from glassbox_agent.agents.junior_dev import JuniorDev
from glassbox_agent.agents.tester import Tester


def run_pipeline(issue_number: int) -> None:
    """End-to-end pipeline: Manager → JuniorDev → Tester → PR."""
    settings = Settings()
    repo_root = os.getcwd()
    ack_comment_id = int(os.environ.get("ACK_COMMENT_ID", "0"))

    # Shared dependencies
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "").strip())
    github = GitHubClient(settings.repo)
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    loader = TemplateLoader(templates_dir)
    memory = MemoryStore(settings.reflections_path)
    editor = CodeEditor(repo_root)
    reader = FileReader(repo_root)
    runner = TestRunner(repo_root)

    # Create agents
    manager = Manager(client=client, github=github, settings=settings,
                      template_loader=loader, memory=memory)
    junior = JuniorDev(client=client, github=github, settings=settings,
                       editor=editor, file_reader=reader)
    tester = Tester(client=client, github=github, settings=settings,
                    test_runner=runner)

    # ── Step 1: Read issue ──
    title, body = github.read_issue(issue_number)
    print(f"Issue #{issue_number}: {title}")

    # ── Step 2: Manager classifies + generates full briefing ──
    print("\n🎯 Manager: Classifying...")
    sources = {}
    for f in reader.list_files((".py",)):
        if f.startswith("src/glassbox/"):
            ok, content = reader.read_raw(f)
            if ok:
                sources[f] = content

    triage = manager.classify(issue_number, title, body, sources)
    template = loader.get(triage.template_id) or loader.all()[0]
    print(f"  Template: {template.id} ({triage.confidence:.0%})")

    if triage.skip_reason:
        skip_body = manager.format_briefing(triage, template)
        github.silent_update(issue_number, ack_comment_id,
                             f"🎯 **GlassBox Manager**\n\n⏭️ Skipping: {triage.skip_reason}\n\n{skip_body}")
        print(f"  Skipping: {triage.skip_reason}")
        return

    # Post Manager briefing (update ack comment — no email)
    briefing = manager.format_briefing(triage, template)
    ack_comment_id = github.silent_update(
        issue_number, ack_comment_id,
        f"🎯 **GlassBox Manager**\n\nPicked up **#{issue_number}**: \"{title}\"\n\n{briefing}",
    )

    # ── Step 3: JuniorDev reacts + generates fix ──
    print("\n🔧 Junior Dev: Generating fix...")
    junior.react(ack_comment_id, "+1")

    branch = f"agent/issue-{issue_number}"
    github.create_branch(branch)

    feedback = ""
    fix = None
    result = TestResult(passed=False, output="No attempts succeeded", failures=[])
    for attempt in range(1, template.max_attempts + 1):
        print(f"  Attempt {attempt}/{template.max_attempts}")

        if attempt > 1:
            # Reset branch to main for a fresh retry
            import subprocess
            subprocess.run(["git", "checkout", "main"], cwd=os.getcwd(), capture_output=True)
            subprocess.run(["git", "branch", "-D", branch], cwd=os.getcwd(), capture_output=True)
            github.create_branch(branch)
        fix = junior.generate_fix(
            issue_number=issue_number, title=title, body=body,
            template=template, triage=triage,
            sources=sources, feedback=feedback,
        )

        # Apply fix
        ok, err = junior.apply_fix(fix)
        if not ok:
            feedback = f"Apply failed: {err}"
            print(f"  ❌ Apply failed: {err}")
            continue

        # Validate — run core tests only (skip agent framework + integration tests)
        result = tester.validate(
            fix, triage.edge_cases,
            test_path="tests/test_glassbox.py tests/test_evals.py",
            test_args="--ignore=tests/test_integration.py -k 'not (test_19 or test_20 or test_21)'",
        )
        if result.passed:
            print(f"  ✅ Tests passed on attempt {attempt}")
            break
        else:
            feedback = f"Tests failed:\n" + "\n".join(
                f"- {f.test_name}: {f.message}" for f in result.failures[:5]
            )
            print(f"  ❌ Tests failed: {len(result.failures)} failures")
    else:
        # All attempts exhausted
        report = tester.format_report(result, triage.edge_cases, template.max_diff_lines)
        github.post_comment(issue_number, f"🧪 **GlassBox Tester**\n\n{report}")
        github.post_comment(issue_number,
                            f"🎯 **GlassBox Manager**\n\n❌ Fix failed after {template.max_attempts} attempts. Manual fix needed.")
        memory.save_reflection(MemoryStore.Reflection(
            issue_number=issue_number, issue_title=title,
            template_id=template.id, reflection=feedback,
        )) if hasattr(MemoryStore, 'Reflection') else None
        return

    # ── Step 4: JuniorDev posts fix comment ──
    fix_body = junior.format_comment(fix)
    junior.comment(issue_number, fix_body)

    # ── Step 5: Tester posts validation comment ──
    report = tester.format_report(result, triage.edge_cases, template.max_diff_lines)
    tester.comment(issue_number, report)

    # ── Step 6: Manager approves + creates PR ──
    print("\n🎯 Manager: Approving and creating PR...")
    commit_msg = f"fix: {fix.summary} (#{issue_number})"
    github.commit_and_push(branch, commit_msg)

    pr_body = (
        f"Closes #{issue_number}\n\n"
        f"## Changes\n{fix.summary}\n\n"
        f"## Strategy\n{fix.strategy}\n\n"
        f"## Template\n`{template.id}` — {template.name}\n\n"
        f"## Generated by\n🤖 **GlassBox Agent v1** — template-driven multi-agent\n"
    )
    pr_url = github.create_pr(branch, issue_number, f"fix: {fix.summary}", pr_body)

    manager.comment(issue_number, (
        f"✅ **Approved.** All aspects pass, all edge cases clear.\n\n"
        f"| | |\n|---|---|\n"
        f"| 🔀 **PR** | {pr_url} |\n"
        f"| 🌿 **Branch** | `{branch}` |\n"
        f"| 📋 **Template** | `{template.id}` |\n"
        f"| 🔄 **Attempts** | {attempt} |"
    ))
    print(f"\n✅ Done! PR: {pr_url}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m glassbox_agent.cli <issue_number>")
        sys.exit(1)
    issue_number = int(sys.argv[1])
    run_pipeline(issue_number)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal: {e}")
        traceback.print_exc()
        if len(sys.argv) >= 2:
            try:
                n = int(sys.argv[1])
                settings = Settings()
                gh = GitHubClient(settings.repo)
                gh.post_comment(n, f"🎯 **GlassBox Manager**\n\n❌ Agent crashed: `{type(e).__name__}: {str(e)[:300]}`")
            except Exception:
                pass
        sys.exit(1)
