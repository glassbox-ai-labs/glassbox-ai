# Feedback Flywheel — Requirements Specification

**Date:** 2026-02-15
**Status:** Draft
**Owner:** @sourabharsh

---

## 1. Purpose

Build a public, auditable feedback loop where:
- GitHub Issues are the input (bugs, features)
- The GlassBox agent attempts to fix them
- Every attempt (pass or fail) is transparently logged in issue comments
- Failures are tagged, analyzed, and used to improve the agent
- The improvement is visible to anyone watching the repo

**This is proof-in-the-pudding: the agent's reasoning IS the product.**

---

## 2. Requirements — Step by Step

### REQ-01: Issue Intake

| Aspect | Requirement |
|--------|-------------|
| **What** | Human creates a GitHub Issue using a structured template |
| **Template fields** | Title, Description, Files Affected, Acceptance Criteria, Expected Behavior, Steps to Reproduce |
| **Labels** | `bug` / `enhancement` / `documentation` + `agent` (signals agent should pick it up) |
| **System design** | Issue templates live in `.github/ISSUE_TEMPLATE/`. Agent only picks up issues labeled `agent`. |
| **Best practice** | Issue must be self-contained — an agent can't ask clarifying questions mid-fix. Every ambiguity must be resolved in the issue body before labeling `agent`. |
| **Edge cases** | Vague issues → agent makes wrong assumptions (Issue #19). Mitigation: require Acceptance Criteria field to be non-empty. |

### REQ-02: Agent Picks Up Issue

| Aspect | Requirement |
|--------|-------------|
| **What** | Agent detects new `agent`-labeled issues and starts processing |
| **Trigger** | GitHub webhook or polling (every 5 min) |
| **First action** | Post comment: `🤖 Agent picked this up. Analyzing...` |
| **System design** | Agent runs in a clean environment (fresh clone, clean virtualenv, no stale state) |
| **Best practice** | Agent should NEVER use cached state from previous runs. Fresh context every time. |
| **Edge case** | Two issues assigned simultaneously → queue, not parallel (avoid state conflicts) |

### REQ-03: Codebase Analysis

| Aspect | Requirement |
|--------|-------------|
| **What** | Agent reads the issue, maps it to files, identifies scope |
| **Steps** | 1. Parse issue body → extract affected files, expected behavior, acceptance criteria |
| | 2. Read affected files + their imports/dependencies (transitive) |
| | 3. Read test files that cover the affected code |
| | 4. Build a dependency graph: what depends on what |
| | 5. Identify BOUNDARIES: Python↔SQL, Python↔API, Python↔config |
| **System design** | Use AST parsing, not just grep, to understand code structure |
| **Best practice** | ALWAYS identify cross-boundary interactions before generating a fix. This is where 100% of our failures occurred. |
| **Edge case** | Agent can't find the file mentioned in the issue → post comment asking for clarification, don't guess |

### REQ-04: Fix Generation

| Aspect | Requirement |
|--------|-------------|
| **What** | Agent generates a code fix based on analysis |
| **Steps** | 1. Generate the fix |
| | 2. Before applying: mentally trace through ALL test cases |
| | 3. Check: does the fix touch any boundary (SQL string, API call, config file)? |
| | 4. If boundary: generate the fix with explicit boundary handling |
| | 5. Generate a test for the fix |
| **System design** | Fix generation is a separate step from fix application. Fix is stored as a diff, not applied immediately. |
| **Best practice** | Minimal fix. Don't refactor unrelated code. One concern per PR. |
| **Edge case** | Fix requires changes in multiple files → ensure all files are updated atomically |

### REQ-05: Pre-Debate Test Run

| Aspect | Requirement |
|--------|-------------|
| **What** | Run ALL existing tests + new test BEFORE debate |
| **Steps** | 1. Apply fix to a temporary branch |
| | 2. Run `pytest tests/ -v` |
| | 3. If tests fail → DO NOT proceed to debate. Go to REQ-07 (retry). |
| | 4. If tests pass → proceed to debate |
| **System design** | Tests run in isolated environment (Docker or virtualenv) |
| **Best practice** | Never let debate agents approve a fix that hasn't passed tests. This was the #1 mistake in Issue #18 — debate approved a fix that immediately broke all tests. |
| **Edge case** | Tests themselves are flaky → retry up to 2 times before marking as infrastructure failure |

### REQ-06: Multi-Agent Debate

| Aspect | Requirement |
|--------|-------------|
| **What** | 3 agents debate the fix quality |
| **Input to debate** | The diff, the test results (MUST include), the issue description, the affected files |
| **Steps** | 1. Round 1: Each agent states position on the fix |
| | 2. Round 2: React to each other |
| | 3. Round 3: Final verdict — APPROVE or REJECT with specific reasons |
| **System design** | Debate agents see test output. This is non-negotiable. |
| **Best practice** | At least one agent should be adversarial: "How can this fix break?" not just "Does this look right?" |
| **Edge case** | All agents approve but tests failed → tests override debate. Tests are truth, debate is opinion. |
| **Edge case** | Debate is split 2-1 → log the dissent. If the dissenter's concern is about a boundary crossing, treat as rejection. |

### REQ-07: Retry with Exploration

| Aspect | Requirement |
|--------|-------------|
| **What** | On failure, retry with a DIFFERENT approach (not the same one) |
| **Steps** | 1. Read the error message carefully |
| | 2. Classify the failure mode (F1–F15 from failure taxonomy) |
| | 3. Based on failure mode, select a different strategy: |
| | — F1 (cross-boundary): isolate the boundary, fix only the host language side |
| | — F2 (API hallucination): read actual API docs/source, don't guess |
| | — F5 (same-mistake loop): try a fundamentally different approach |
| | 4. Generate new fix using the different strategy |
| | 5. Run tests again |
| **Max retries** | 3 attempts. After 3 failures, escalate to human. |
| **System design** | Each retry must use a different strategy. Same strategy = same bug. Track strategies used. |
| **Best practice** | NeurIPS 2024 "Code Repair as Exploration-Exploitation": branch out, don't repeat. |
| **Edge case** | All 3 strategies fail → post full failure log + all approaches tried, ask human for guidance |

### REQ-08: PR Creation

| Aspect | Requirement |
|--------|-------------|
| **What** | Create a Pull Request with the fix |
| **Branch naming** | `agent/issue-{number}` |
| **PR body** | Summary of changes, debate transcript, test results, failure mode if any retries |
| **System design** | PR links back to the issue. Issue is updated with PR link. |
| **Best practice** | PR should be reviewable by a human in under 5 minutes. Small diff, clear commit message. |
| **Edge case** | Branch already exists from previous failed attempt → force-push or use `agent/issue-{number}-v2` |

### REQ-09: GitHub Issue Comment Trail

| Aspect | Requirement |
|--------|-------------|
| **What** | Every step is logged as a comment on the GitHub issue |
| **Comments posted** | 1. `🤖 Agent picked this up. Analyzing...` |
| | 2. `🔧 Fix generated: {summary}` |
| | 3. `🗣️ Debate ({approval_count}/3): {@agent}: ✅/❌ {reason}` |
| | 4. `✅ Tests passed` or `❌ Tests failed: {error}` |
| | 5. `🔄 Retry {n}: {new_strategy}` (if retrying) |
| | 6. `✅ PR ready: {link}` or `❌ Failed after {n} attempts. Manual fix needed.` |
| **System design** | Comments are append-only. Never edit previous comments. Full audit trail. |
| **Best practice** | Anyone reading the issue should understand: what was tried, why it failed, what was learned. This IS the transparency. |
| **Edge case** | API rate limit on comments → batch updates, post summary instead of per-step |

### REQ-10: Failure Tagging & Learning

| Aspect | Requirement |
|--------|-------------|
| **What** | Every failure is tagged with a failure mode and stored for learning |
| **Steps** | 1. On failure: classify into F1–F15 |
| | 2. Add label to issue: `failure:cross-boundary`, `failure:api-hallucination`, etc. |
| | 3. Log to `docs/architecture/failure-log.md` with issue number, failure mode, root cause |
| | 4. If same failure mode appears 3+ times → create a meta-issue to fix the agent's approach |
| **System design** | Failure log is append-only markdown. Simple, grep-able, human-readable. |
| **Best practice** | Reflexion (Shinn et al., NeurIPS 2023): store verbal failure reflections → agent reads them before next attempt on similar issues. |
| **Edge case** | Novel failure mode not in F1–F15 → add as F16+ and document |

### REQ-11: Trust Score Integration

| Aspect | Requirement |
|--------|-------------|
| **What** | Agent trust scores update based on issue outcomes |
| **Steps** | 1. Agent fix merged → `update_trust(agent, True)` for agents who approved |
| | 2. Agent fix rejected/failed → `update_trust(agent, False)` for agents who approved the bad fix |
| | 3. If an agent correctly predicted a failure → `update_trust(agent, True)` |
| **System design** | Trust scores persist across issues. Low-trust agents get less weight in debate. |
| **Best practice** | Agents who always approve everything should see trust decay. Agents who catch real bugs should see trust increase. |
| **Edge case** | All agents wrong → all trust scores decrease. System should still function. |

---

## 3. System-Level Design Aspects

### Short-term (now → 2 weeks)
- [ ] Create issue templates in `.github/ISSUE_TEMPLATE/`
- [ ] Implement comment posting on issue pickup
- [ ] Add pre-debate test run (tests before debate, not after)
- [ ] Add failure mode classification to issue comments
- [ ] Create `docs/architecture/failure-log.md`

### Medium-term (2 weeks → 2 months)
- [ ] Implement exploration-exploitation retry (different strategy per attempt)
- [ ] Add boundary detection: flag when fix touches Python↔SQL, Python↔API boundaries
- [ ] Multi-model debate: use Claude for one agent, GPT for another (diverse blind spots)
- [ ] Reflexion memory: store failure reflections, read them before similar issues
- [ ] Dashboard: failure mode frequency, agent pass rate, trust score evolution

### Long-term (2 months → 6 months)
- [ ] Self-improving agent: reads its own failure log, adjusts prompts automatically
- [ ] Community contributions: external users file issues, agent attempts, community reviews
- [ ] Benchmark: track agent pass rate over time as the "GlassBox Agent Benchmark"
- [ ] Publish results: blog post / paper on feedback flywheel outcomes

---

## 4. Success Metrics

| Metric | Current | Target (3 months) |
|--------|---------|-------------------|
| Agent pass rate on bug issues | 50% (2/4) | 80% |
| Agent pass rate on cross-boundary issues | 0% (0/2) | 50% |
| Average retries before success | 2.5 | 1.5 |
| Debate correctly predicts test outcome | 50% | 85% |
| Time from issue creation to PR | ~10 min | ~5 min |
| Failure modes with known mitigations | 0/15 | 12/15 |

---

## 5. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| **Transparency** | Every agent action is visible in GitHub issue comments |
| **Auditability** | Full reasoning chain: issue → analysis → fix → debate → tests → result |
| **Reproducibility** | Same issue + same agent version → same result (deterministic where possible) |
| **Isolation** | Each issue processed in clean environment, no cross-contamination |
| **Graceful degradation** | If agent can't fix, it says so clearly with context for human handoff |
| **Cost awareness** | Track token usage per issue. Budget alerts at $X/issue threshold |
