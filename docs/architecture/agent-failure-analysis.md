# Why the GlassBox AI Agent Fails — Deep Analysis

**Date:** 2026-02-15
**Scope:** Analysis of GitHub Issues #14, #16, #18, #19 agent attempts
**Sources:** Our agent logs, SWE-Bench Pro (2025), Augment Code failure taxonomy, arXiv:2411.10213

---

## Executive Summary

Out of 4 issues assigned to the agent:
- **2 passed** (#14 version string, #16 standup→design review) — simple, single-file, text-level changes
- **1 failed hard** (#18 magic number) — agent broke all tests by confusing Python variables with SQL literals
- **1 partially failed** (#19 find 3 bugs) — agent changed correct code to incorrect code (`.content` → `['content']`)

**Core pattern: the agent succeeds at grep-and-replace tasks but fails when the fix requires understanding cross-boundary semantics (Python↔SQL, object↔dict, runtime↔schema).**

---

## Issue-by-Issue Failure Analysis

### Issue #14 — Hardcoded version string ✅ PASSED

| Aspect | Detail |
|--------|--------|
| **Task** | Replace `"GlassBox AI v0.3.0"` with `f"GlassBox AI v{__version__}"` |
| **Difficulty** | Low — single file, single line, import + f-string |
| **Agent behavior** | Found the line, added import, wrote test. Clean PR. |
| **Why it passed** | No cross-boundary reasoning needed. Pure Python refactor. |

### Issue #16 — "standup meeting" → "design review" ✅ PASSED

| Aspect | Detail |
|--------|--------|
| **Task** | Replace string "standup meeting" with "design review" in prompts |
| **Difficulty** | Trivial — find-and-replace |
| **Agent behavior** | Found all 3 occurrences, replaced, tests pass. |
| **Why it passed** | Text substitution. Zero semantic reasoning required. |

### Issue #18 — Magic number 0.85 → DEFAULT_TRUST ❌ FAILED (3 retries + debate rejection)

| Aspect | Detail |
|--------|--------|
| **Task** | Extract `0.85` into a named constant `DEFAULT_TRUST` |
| **Difficulty** | Medium — the value appears in Python code AND SQL strings |
| **Agent behavior** | Replaced `0.85` with `DEFAULT_TRUST` everywhere, including inside SQL `DEFAULT 0.85` and SQL `VALUES (?, 0.85)` |
| **Error** | `sqlite3.OperationalError: no such column: DEFAULT_TRUST` — agent put a Python variable name inside an SQL string literal |
| **Retries** | 3 code attempts (all same error), then 3 debate-rejected attempts |
| **Debate feedback** | Critics caught the SQL string issue but the agent couldn't fix it |

**Root cause: CROSS-BOUNDARY CONFUSION**
The agent treated Python code and SQL strings as the same namespace. It saw `0.85` in a SQL `DEFAULT 0.85` clause and replaced it with the Python variable name, not understanding that SQL literals are evaluated by SQLite, not Python.

**The correct fix:**
```python
DEFAULT_TRUST = 0.85

# In SQL: still use the literal 0.85 or use f-string interpolation
conn.execute(f"...DEFAULT {DEFAULT_TRUST}...")
# OR keep SQL default as-is and only change Python references
```

### Issue #19 — Find 3 bugs ❌ PARTIALLY FAILED

| Aspect | Detail |
|--------|--------|
| **Task** | Find and fix 3 low-hanging bugs in the codebase |
| **Difficulty** | Medium — requires reading code, understanding runtime behavior |
| **Agent behavior** | Changed `r.choices[0].message.content` to `r['choices'][0]['message']['content']` |
| **Error** | OpenAI returns typed objects (`ChatCompletionMessage`), not dicts. The original code was correct. |
| **Additional** | PR auto-creation also failed (org name change timing) |

**Root cause: API MODEL HALLUCINATION**
The agent assumed the OpenAI response is a dict (JSON-like) when it's actually a Pydantic model with attribute access. The agent "fixed" working code into broken code.

---

## Taxonomy of Agent Failure Modes

Based on our issues + research literature, here are the **15 distinct failure modes** that affect coding agents:

### Category 1: SEMANTIC UNDERSTANDING FAILURES

| # | Failure Mode | Seen In | Research Source |
|---|-------------|---------|-----------------|
| **F1** | **Cross-boundary confusion** — treating SQL/HTML/regex strings as the same namespace as host language | Issue #18 | SWE-Bench Pro: "semantic understanding issues" |
| **F2** | **API model hallucination** — assuming wrong return types, calling nonexistent methods | Issue #19 | Augment Code: "Hallucinated APIs That Don't Exist" (1 in 5 AI code samples) |
| **F3** | **Fixing what isn't broken** — changing correct code based on wrong assumptions | Issue #19 | arXiv:2411.10213: "incorrect reproduction can lead to failure of entire solving process" |
| **F4** | **Shallow pattern matching** — replacing text patterns without understanding context | Issue #18 | SWE-Bench Pro: "models heavily rely on explicit human-provided context" |

### Category 2: RETRY & RECOVERY FAILURES

| # | Failure Mode | Seen In | Research Source |
|---|-------------|---------|-----------------|
| **F5** | **Same-mistake retry loop** — retrying the same approach 3 times despite same error | Issue #18 | NeurIPS 2024: "Code Repair gives Exploration-Exploitation Tradeoff" |
| **F6** | **Debate echo chamber** — all 3 debate agents approve a broken fix | Issue #19 | Augment Code: "collective delusion rather than objective validator" |
| **F7** | **Error message blindness** — not reading/understanding the error to adjust strategy | Issue #18 | arXiv:2411.10213: "mechanisms to avoid randomness of model's output" |

### Category 3: CONTEXT & SCOPE FAILURES

| # | Failure Mode | Seen In | Research Source |
|---|-------------|---------|-----------------|
| **F8** | **Missing global impact analysis** — not checking how a local change propagates | Issue #18 | Augment Code: "Pattern 8: Missing Context Dependencies" |
| **F9** | **Multi-file context loss** — failing when fix spans multiple files/layers | General | SWE-Bench Pro: "sharp decline in performance as files increase" |
| **F10** | **Schema/runtime mismatch** — code works syntactically but fails against actual data schemas | Issue #18 | Augment Code: "Pattern 7: Data Model Mismatches" |

### Category 4: SPECIFICATION & JUDGMENT FAILURES

| # | Failure Mode | Seen In | Research Source |
|---|-------------|---------|-----------------|
| **F11** | **Vague issue interpretation** — filling in ambiguity with wrong assumptions | Issue #19 | Augment Code: "agents can't read between lines, infer context" |
| **F12** | **Test-blind fix** — generating a fix without running tests mentally first | Issue #18 | arXiv:2411.10213: "check completeness of patches" |
| **F13** | **False confidence in debate** — debate approves because agents review code superficially | Issue #18, #19 | Our debate logs: all agents said ✅ but fix was broken |

### Category 5: INFRASTRUCTURE FAILURES

| # | Failure Mode | Seen In | Research Source |
|---|-------------|---------|-----------------|
| **F14** | **PR creation failure** — tooling breaks (org rename, permissions, branch issues) | Issue #19 | Beam AI: "No Production-Ready Architecture" |
| **F15** | **Stale context after env change** — agent uses old org/repo name after rename | Issue #19 | General: environment drift |

---

## Why the Debate Didn't Catch the Bugs

This is the most important finding for GlassBox AI's core thesis.

**Issue #18 — debate approved a broken fix 3 times:**
```
@architect: ✅ The change correctly replaces the magic number with a named constant
@pragmatist: ✅ Minimal changes, appropriate
@critic: ✅ Changes correctly replace the magic number
```
Then after tests failed, debate STILL couldn't fix it:
```
@critic: ❌ The code still has hardcoded instances of 0.85 in SQL strings
@architect: ❌ Not in SQL strings, inconsistency
```
The critics identified the problem in plain English but the code generator couldn't translate "don't put Python variables in SQL strings" into working code.

**Issue #19 — debate approved a wrong fix:**
```
@architect: ✅ No syntax or runtime errors detected
@pragmatist: ✅ Minimal changes effectively address the bugs
@critic: ✅ No SQL injection risk
```
All 3 agents approved changing `.content` to `['content']` — which breaks the OpenAI SDK.

### Why?

1. **Debate agents don't execute code** — they review text, not runtime behavior
2. **Same model, same blind spots** — all agents use GPT-4o/4o-mini, share training data gaps
3. **No grounding in actual test results** — agents don't see test output before approving
4. **Superficial code review** — agents check syntax, not semantics
5. **No adversarial testing** — no agent tries to break the fix

---

## What Research Says About Fixing This

| Fix | Source | How It Helps |
|-----|--------|-------------|
| **Independent judge with isolated context** | Augment Code | Judge agent that ONLY sees code diff + test results, not the debate |
| **Test-first validation** | arXiv:2411.10213 | Run tests before debate. Don't debate if tests fail. |
| **Exploration-exploitation in retries** | NeurIPS 2024 | Don't retry same approach. Branch out: try different strategies. |
| **Specification as JSON schema** | Augment Code | Issue requirements as structured contracts, not prose |
| **Multi-model diversity** | SWE-Bench Pro | Use Claude + GPT + Gemini — different training data = different blind spots |
| **Reflexion memory** | NeurIPS 2023 (Shinn et al.) | Store verbal failure reflections → agent learns from past mistakes |
| **Line-level fault localization** | arXiv:2411.10213 | Pinpoint exact lines, don't rely on file-level grep |
| **Circuit breakers** | Augment Code | Max 3 retries, then escalate to human with full context |

---

## The Feedback Flywheel

This is our proof-in-the-pudding system:

```
┌─────────────────────────────────────────┐
│  1. Human creates GitHub Issue          │
│     (bug, feature, or improvement)      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  2. Agent picks up issue                │
│     - Reads issue, analyzes codebase    │
│     - Generates fix + debate            │
│     - Runs tests                        │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
   PASS ✅         FAIL ❌
       │               │
┌──────▼───────┐ ┌─────▼──────────────────┐
│  3a. PR      │ │  3b. Failure logged    │
│  created     │ │  - Error message       │
│  + merged    │ │  - Debate transcript   │
│              │ │  - Root cause tag      │
└──────┬───────┘ │  - Failure mode (F1-15)│
       │         └─────┬──────────────────┘
       │               │
┌──────▼───────────────▼──────────────────┐
│  4. Comment posted on GitHub Issue      │
│     - Full reasoning chain visible      │
│     - Debate transcript                 │
│     - Test results                      │
│     - Success/failure + root cause      │
│     → TRANSPARENCY: anyone can audit    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  5. Human reviews                       │
│     - Approves/rejects PR               │
│     - Tags failure mode if agent failed │
│     - Creates follow-up issue if needed │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  6. Agent improves                      │
│     - Failure patterns → prompt updates │
│     - Trust scores adjust               │
│     - New test cases added              │
│     → LOOP BACK TO STEP 1              │
└─────────────────────────────────────────┘
```

**Key principle:** Every agent attempt — pass or fail — is public in the GitHub issue comments. This IS the transparency. The reasoning is the product.

---

## Scorecard

| Issue | Task Type | Files | Cross-Boundary | Agent Result | Failure Modes |
|-------|-----------|-------|----------------|-------------|---------------|
| #14 | Refactor (import + f-string) | 1 | No | ✅ Pass | — |
| #16 | Text replacement | 1 | No | ✅ Pass | — |
| #18 | Refactor (constant extraction) | 1 | Yes (Python↔SQL) | ❌ Fail | F1, F4, F5, F7, F8, F10, F12, F13 |
| #19 | Bug finding (open-ended) | 3 | Yes (SDK objects) | ⚠️ Partial | F2, F3, F6, F11, F13, F14 |

**Pattern:** Agent passes 100% of single-file, no-boundary tasks. Agent fails 100% of cross-boundary tasks.
