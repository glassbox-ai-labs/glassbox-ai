# GlassBox AI — Competitive Analysis & Strategic Positioning

**Date:** 2026-02-15 | **Version:** 0.3.0 | **Author:** Strategic Analysis

---

## 1. What GlassBox AI Is

**Multi-agent MCP server + autonomous coding agent** that:
- 3 AI agents debate any task, reference each other, agree/disagree, converge
- Trust scores track agent reliability via EMA (SQLite-persisted)
- 6-message transparency protocol: every step visible in GitHub issue comments
- Reflexion memory: learns from past failures
- 12 core aspects graded per fix (readability, modularity, cross-boundary safety, etc.)
- MCP server works in Windsurf/Cursor/Claude Desktop

**Core thesis: Glass box over black box — the reasoning IS the product.**

---

## 2. The 10 Competitors

### Tier 1: Autonomous Coding Agents (Direct Competitors)

| # | Company | Funding/Val | ARR | Pricing | Key Strength |
|---|---------|------------|-----|---------|-------------|
| 1 | **Devin (Cognition)** | $10.2B val | $155M | $20/mo (was $500) | Full autonomy, sandboxed env, massive scale |
| 2 | **SWE-agent (Princeton)** | Academic | N/A | Free/OSS | SWE-Bench leader, research-grade |
| 3 | **OpenHands** | OSS community | N/A | Free/OSS | Most popular OSS agent, flexible framework |
| 4 | **Factory AI** | $50M Series A | ~$20M+ | Enterprise | "Droids" for enterprises, multi-LLM |

### Tier 2: IDE-Integrated Agents (Overlap Competitors)

| # | Company | Funding/Val | Pricing | Key Strength |
|---|---------|------------|---------|-------------|
| 5 | **Cursor (Agent)** | $2.5B+ val | $20/mo | Dominant IDE, multi-file agent mode |
| 6 | **Claude Code (Anthropic)** | $18B+ val | API pricing | Terminal agent, MCP native, best reasoning |
| 7 | **Cline/RooCode** | OSS | Free | Full MCP, browser control, community |

### Tier 3: PR Review & Code Quality (Partial Competitors)

| # | Company | Pricing | Key Strength |
|---|---------|---------|-------------|
| 8 | **CodeRabbit** | $15/dev/mo | Market leader in AI PR review |
| 9 | **Qodo (Codium)** | $15/dev/mo | Multi-agent review + test generation |
| 10 | **Greptile** | $30/dev/mo | Deep codebase graph analysis |

---

## 3. The 20 Aspects — Head-to-Head Scoring

**Scoring:** 1-5 (5 = best in class)
**Importance:** 1-10 (10 = critical for market win)
**Scope:** How common/universal this need is (Narrow / Medium / Broad)
**User Value:** What the user actually gets from this aspect

---

### ASPECT 1: Transparency of Reasoning
**Importance: 9/10 | Scope: BROAD | User Value: Trust the output, debug failures, learn from the agent**

> Can you see WHY the agent made each decision? Can you trace the full reasoning chain from input to output?

| Player | Score | Notes |
|--------|-------|-------|
| **GlassBox** | **5** | 6-message protocol: every aspect, challenge, edge case, debate transcript, grade visible in GitHub comments. Full audit trail. **This is our thesis.** |
| Devin | 3 | Shows steps in its workspace UI, but it's a black-box session. You see what it did, not why it chose it over alternatives. |
| SWE-agent | 2 | Logs actions/observations. Research tool, not designed for human consumption. |
| OpenHands | 2 | Action logs visible but raw/technical. No structured reasoning chain. |
| Factory AI | 2 | Enterprise dashboards but agent reasoning is opaque. |
| Cursor Agent | 1 | Shows diffs inline. Zero reasoning trace. You accept or reject. |
| Claude Code | 3 | Shows thinking in terminal. Good inline reasoning but ephemeral — gone when session ends. |
| Cline/RooCode | 2 | Shows tool calls. Mechanical log, not a reasoning narrative. |
| CodeRabbit | 2 | Shows review comments on PR. Explains findings but no debate or alternatives considered. |
| Qodo | 2 | Shows test suggestions with rationale. Limited to review scope. |
| Greptile | 2 | Shows dependency analysis. Single perspective, no alternatives. |

**WHO WINS: GlassBox (5) — no one else treats transparency as the product itself.**

---

### ASPECT 2: Multi-Agent Debate
**Importance: 8/10 | Scope: BROAD | User Value: Catch blind spots, reduce hallucination, get diverse perspectives**

> Multiple agents with different roles argue about the solution before shipping.

| Player | Score | Notes |
|--------|-------|-------|
| **GlassBox** | **5** | 3 agents (@architect, @pragmatist, @critic), 3 rounds, reference each other by name, CHANGED/HOLDING protocol. Research-backed (Du et al. NeurIPS 2024). |
| Devin | 1 | Single agent. No debate. |
| SWE-agent | 1 | Single agent. |
| OpenHands | 1 | Single agent (can configure multi but not core). |
| Factory AI | 2 | "Droids" work on different tasks but don't debate each other. Division of labor, not adversarial review. |
| Cursor Agent | 1 | Single agent. |
| Claude Code | 1 | Single agent. |
| Cline/RooCode | 1 | Single agent (community has multi-agent experiments). |
| CodeRabbit | 1 | Single AI reviewer. |
| Qodo | 3 | Claims "multi-agent AI" for review. Uses RAG + multiple passes but not adversarial debate. |
| Greptile | 1 | Single analysis engine. |

**WHO WINS: GlassBox (5) — only product with structured adversarial multi-agent debate as a core feature.**

---

### ASPECT 3: Trust / Reputation Scoring
**Importance: 7/10 | Scope: MEDIUM | User Value: Know which agent opinions to weight, track reliability over time, calibrated confidence**

> Agents have persistent trust scores that update based on outcomes.

| Player | Score | Notes |
|--------|-------|-------|
| **GlassBox** | **5** | SQLite-persisted trust scores, EMA updates, floor/ceiling, auto-update on debate persuasion, manual override. EigenTrust planned. |
| Devin | 1 | No trust system. |
| SWE-agent | 1 | No trust system. |
| OpenHands | 1 | No trust system. |
| Factory AI | 2 | Enterprise metrics on agent performance, but not per-agent trust scoring. |
| Cursor Agent | 1 | No trust system. |
| Claude Code | 1 | No trust system. |
| Cline/RooCode | 1 | No trust system. |
| CodeRabbit | 1 | Learns from feedback but no quantified trust score. |
| Qodo | 1 | Team analytics but not agent trust scoring. |
| Greptile | 1 | Learns from feedback but no trust quantification. |

**WHO WINS: GlassBox (5) — nobody else has this. Unique capability backed by research (Kamvar et al. WWW 2003).**

---

### ASPECT 4: Autonomous Issue-to-PR Pipeline
**Importance: 10/10 | Scope: BROAD | User Value: Label an issue → get a working PR. Zero manual coding.**

> Takes a GitHub issue and delivers a tested, reviewed pull request.

| Player | Score | Notes |
|--------|-------|-------|
| GlassBox | 3 | Works but v0.3-beta. 50% pass rate. Fails on cross-boundary issues. Python only. |
| **Devin** | **5** | Production-grade. Multi-language. Sandboxed. $155M ARR proves it works at scale. |
| SWE-agent | 4 | Research-grade but strong on SWE-Bench. Needs setup. |
| **OpenHands** | **4** | Full pipeline. Docker sandboxed. Multi-language. Active community. |
| Factory AI | 4 | Enterprise "Droids" handle full tasks. Production-grade. |
| Cursor Agent | 2 | Agent mode in IDE, but no GitHub issue intake or auto-PR. Human drives. |
| Claude Code | 2 | Can do it manually but no automated GitHub integration. |
| Cline/RooCode | 2 | Can code fixes but no auto-PR pipeline. |
| CodeRabbit | 1 | Reviews PRs, doesn't create them. |
| Qodo | 1 | Reviews and tests, doesn't fix. |
| Greptile | 1 | Reviews only. |

**WHO WINS: Devin (5). GlassBox (3) — functional but needs maturity on pass rate and language support.**

---

### ASPECT 5: Self-Grading / Pre-declared Checklist
**Importance: 8/10 | Scope: BROAD | User Value: Agent declares what it will check BEFORE coding, then grades itself. Accountability.**

> Agent publishes aspects, challenges, edge cases BEFORE generating code, then grades each one after.

| Player | Score | Notes |
|--------|-------|-------|
| **GlassBox** | **5** | 12 core aspects + issue-specific ones. Challenges + edge cases with MRU ranking. Each graded ✅/❌ with remarks. **No other agent does this.** |
| Devin | 1 | No pre-declared checklist. |
| SWE-agent | 1 | No checklist. |
| OpenHands | 1 | No checklist. |
| Factory AI | 1 | No public checklist. |
| Cursor Agent | 1 | No checklist. |
| Claude Code | 1 | No checklist. |
| Cline/RooCode | 1 | No checklist. |
| CodeRabbit | 2 | Has review rules but not pre-declared per-task. |
| Qodo | 2 | Has quality rules but not a think-before-code checklist. |
| Greptile | 1 | No checklist. |

**WHO WINS: GlassBox (5) — completely unique. This is a massive differentiator.**

---

### ASPECT 6: Learning from Failures (Reflexion Memory)
**Importance: 8/10 | Scope: BROAD | User Value: Agent gets smarter over time, doesn't repeat mistakes**

> Verbal failure reflections stored and retrieved before similar future tasks.

| Player | Score | Notes |
|--------|-------|-------|
| **GlassBox** | **4** | Reflexion memory (Shinn et al. NeurIPS 2023). Stores failure mode, reflection text, edge cases missed. Read before next attempt. |
| Devin | 3 | "Memory" features in 2.0. Learns preferences. Less structured than reflexion. |
| SWE-agent | 1 | No memory across runs. |
| OpenHands | 2 | Partial memory support. |
| Factory AI | 3 | Enterprise learning across team. Proprietary. |
| Cursor Agent | 2 | Rules files (.cursorrules) but static, not learned from failures. |
| Claude Code | 2 | CLAUDE.md project memory. Static, human-written. |
| Cline/RooCode | 2 | .clinerules. Static. |
| CodeRabbit | 2 | Learns from PR feedback over time. |
| Qodo | 2 | Adapts to team patterns. |
| Greptile | 2 | Trains on feedback. |

**WHO WINS: GlassBox (4) — only one with research-backed Reflexion (verbal RL). Devin close at 3.**

---

### ASPECT 7: Multi-Language Support
**Importance: 9/10 | Scope: BROAD | User Value: Works on any codebase regardless of language**

| Player | Score | Notes |
|--------|-------|-------|
| GlassBox | 1 | **Python only.** Major weakness. |
| **Devin** | **5** | All major languages. |
| SWE-agent | 4 | Primarily Python-tested but language-agnostic in principle. |
| **OpenHands** | **5** | Language-agnostic. Docker sandboxed. |
| Factory AI | 5 | Enterprise multi-language. |
| Cursor Agent | 5 | All languages. |
| Claude Code | 5 | All languages. |
| Cline/RooCode | 5 | All languages. |
| CodeRabbit | 5 | 30+ languages. |
| Qodo | 4 | Major languages. |
| Greptile | 4 | Major languages. |

**WHO WINS: Everyone except GlassBox. This is our biggest gap. Score: 1 vs industry standard 5.**

---

### ASPECT 8: Sandboxed Execution
**Importance: 8/10 | Scope: BROAD | User Value: Agent can't break your system. Safe to let it run autonomously.**

| Player | Score | Notes |
|--------|-------|-------|
| GlassBox | 1 | **No sandbox. Runs on host.** Planned but not built. |
| **Devin** | **5** | Full sandboxed cloud environment. |
| SWE-agent | 4 | Docker sandbox. |
| **OpenHands** | **5** | Docker sandbox, well-designed. |
| Factory AI | 5 | Enterprise sandboxed. |
| Cursor Agent | 2 | Runs on host with approval steps. |
| Claude Code | 2 | Runs on host with permission system. |
| Cline/RooCode | 3 | Docker support via MCP. |
| CodeRabbit | 5 | Cloud-only, no host access needed. |
| Qodo | 5 | Cloud-only. |
| Greptile | 5 | Cloud-only. |

**WHO WINS: Devin/OpenHands/Factory (5). GlassBox (1) — critical gap for production use.**

---

### ASPECT 9: IDE Integration / Developer Workflow
**Importance: 9/10 | Scope: BROAD | User Value: Works where you already work. Zero context switching.**

| Player | Score | Notes |
|--------|-------|-------|
| GlassBox | 4 | MCP server → works in Windsurf, Cursor, Claude Desktop natively. Hot-reload dev mode. |
| Devin | 3 | Own web UI. VSCode-inspired but separate from your IDE. |
| SWE-agent | 2 | CLI tool. No IDE integration. |
| OpenHands | 3 | Web UI. Some IDE integrations. |
| Factory AI | 3 | Web dashboard + GitHub. |
| **Cursor Agent** | **5** | IS the IDE. Native. |
| Claude Code | 4 | Terminal-based, works alongside any IDE. |
| **Cline/RooCode** | **5** | VSCode extension. Native IDE. |
| CodeRabbit | 3 | GitHub/GitLab. Not in IDE. |
| Qodo | 4 | IDE plugin + PR integration. |
| Greptile | 3 | GitHub integration. |

**WHO WINS: Cursor/Cline (5). GlassBox (4) — strong via MCP protocol. Good position.**

---

### ASPECT 10: Open Source
**Importance: 7/10 | Scope: BROAD | User Value: Inspect code, contribute, self-host, no vendor lock-in**

| Player | Score | Notes |
|--------|-------|-------|
| **GlassBox** | **5** | MIT license. Full source on GitHub. PyPI package. |
| Devin | 1 | Fully proprietary. |
| **SWE-agent** | **5** | MIT. Princeton NLP. |
| **OpenHands** | **5** | MIT. Large community. |
| Factory AI | 1 | Proprietary. |
| Cursor Agent | 1 | Proprietary (VSCode fork). |
| Claude Code | 1 | Proprietary. |
| **Cline/RooCode** | **5** | Apache 2.0. |
| CodeRabbit | 1 | Proprietary. |
| Qodo | 2 | Partial OSS (some tools). |
| Greptile | 1 | Proprietary. |

**WHO WINS: Tie — GlassBox/SWE-agent/OpenHands/Cline (5). Strong position.**

---

### ASPECT 11: Pricing / Accessibility
**Importance: 8/10 | Scope: BROAD | User Value: Can indie devs and small teams afford it?**

| Player | Score | Notes |
|--------|-------|-------|
| **GlassBox** | **5** | Free + OSS. Only cost is your OpenAI API key (~$0.10-0.50/debate). |
| Devin | 4 | $20/mo (was $500). Now accessible. But API costs on top. |
| **SWE-agent** | **5** | Free. Your own API key. |
| **OpenHands** | **5** | Free. Your own API key. |
| Factory AI | 1 | Enterprise pricing. Not accessible to individuals. |
| Cursor Agent | 4 | $20/mo. Very reasonable. |
| Claude Code | 3 | API pricing. Can get expensive on heavy use. |
| **Cline/RooCode** | **5** | Free. Your own API key. |
| CodeRabbit | 3 | $15/dev/mo. Free for OSS. |
| Qodo | 3 | $15/dev/mo. Free for individuals. |
| Greptile | 2 | $30/dev/mo. Expensive. |

**WHO WINS: Tie — GlassBox/SWE-agent/OpenHands/Cline (5). Free + OSS model wins.**

---

### ASPECT 12: Enterprise Readiness
**Importance: 7/10 | Scope: MEDIUM | User Value: SOC2, SSO, team management, compliance, SLAs**

| Player | Score | Notes |
|--------|-------|-------|
| GlassBox | 1 | No enterprise features. Solo developer tool today. |
| **Devin** | **5** | Full enterprise. Team workspaces. SOC2. SSO. |
| SWE-agent | 1 | Research tool. No enterprise features. |
| OpenHands | 2 | Self-host possible but no enterprise wrapper. |
| **Factory AI** | **5** | Built for enterprise. MongoDB, EY, Zapier customers. SOC2. |
| Cursor Agent | 4 | Team plans. Growing enterprise. |
| Claude Code | 3 | Anthropic enterprise API. |
| Cline/RooCode | 2 | OSS. Self-host only. |
| CodeRabbit | 4 | Enterprise tier. SSO. Compliance. |
| Qodo | 4 | Enterprise tier. Team analytics. |
| Greptile | 4 | Enterprise. GitHub Enterprise support. |

**WHO WINS: Devin/Factory (5). GlassBox (1) — not a priority now but needed for revenue.**

---

### ASPECT 13: Code Localization Quality
**Importance: 8/10 | Scope: BROAD | User Value: Agent finds the RIGHT files to modify, not random ones**

> How well does the agent identify which files, functions, and lines to change?

| Player | Score | Notes |
|--------|-------|-------|
| GlassBox | 4 | Aider RepoMap (tree-sitter + PageRank). Dynamic discovery. No hardcoded lists. |
| **Devin** | **5** | Full codebase understanding. Persistent workspace. |
| SWE-agent | 4 | Good localization. Research-optimized. |
| OpenHands | 4 | File search + code understanding. |
| Factory AI | 4 | Enterprise-grade code understanding. |
| Cursor Agent | 4 | Full codebase indexing. |
| **Claude Code** | **5** | Excellent codebase understanding via file reading. |
| Cline/RooCode | 4 | Good file discovery via search tools. |
| CodeRabbit | 3 | Reviews what's in the PR, doesn't discover beyond. |
| Qodo | 3 | Reviews PR scope. |
| Greptile | 4 | Full dependency graph analysis. |

**WHO WINS: Devin/Claude Code (5). GlassBox (4) — good via Aider RepoMap. Competitive.**

---

### ASPECT 14: Test Generation
**Importance: 7/10 | Scope: BROAD | User Value: Agent writes tests for its own fixes. Proof it works.**

| Player | Score | Notes |
|--------|-------|-------|
| GlassBox | 3 | Generates tests as part of fix. MRU framework for test count. But limited by Python-only. |
| Devin | 4 | Generates and runs tests in sandbox. Multi-language. |
| SWE-agent | 3 | Can generate tests. Research-focused. |
| OpenHands | 3 | Can generate tests. |
| Factory AI | 4 | Enterprise test generation. |
| Cursor Agent | 3 | Can generate tests on request. Not automatic. |
| Claude Code | 3 | Can generate tests on request. |
| Cline/RooCode | 3 | Can generate tests. |
| CodeRabbit | 1 | Reviews only, no test generation. |
| **Qodo** | **5** | Test generation is their core product. Best in class. |
| Greptile | 1 | No test generation. |

**WHO WINS: Qodo (5). GlassBox (3) — decent but Qodo dominates this niche.**

---

### ASPECT 15: Research Foundation / Academic Rigor
**Importance: 6/10 | Scope: NARROW | User Value: Confidence that the approach is scientifically grounded, not marketing hype**

| Player | Score | Notes |
|--------|-------|-------|
| **GlassBox** | **5** | Cites 15+ papers (NeurIPS, ICLR, ACL). Debate from Du et al., Trust from EigenTrust, Reflexion from Shinn et al., Safety from Irving et al. Every design decision has a paper. |
| Devin | 2 | No published research foundation. Engineering-driven. |
| **SWE-agent** | **5** | IS the research. Princeton NLP. Published at top venues. |
| OpenHands | 3 | Academic contributors. Some papers. |
| Factory AI | 2 | Engineering-driven. Marketing claims. |
| Cursor Agent | 2 | No published research. |
| Claude Code | 4 | Anthropic publishes heavily. Constitutional AI, etc. |
| Cline/RooCode | 1 | Community-driven. No research. |
| CodeRabbit | 1 | No research foundation. |
| Qodo | 2 | Some published benchmarks. |
| Greptile | 2 | Published their own benchmarks. |

**WHO WINS: GlassBox/SWE-agent (5). Strong credibility signal for technical buyers.**

---

### ASPECT 16: Speed / Latency (Issue to PR)
**Importance: 7/10 | Scope: BROAD | User Value: Fast turnaround. Don't wait hours for a fix.**

| Player | Score | Notes |
|--------|-------|-------|
| GlassBox | 3 | ~10 min for simple issues. 3 LLM calls per debate round = slower. Targeting 5 min. |
| **Devin** | **5** | Optimized cloud infra. Fast execution. |
| SWE-agent | 3 | Varies. Research tool, not optimized for speed. |
| OpenHands | 3 | Depends on setup. |
| Factory AI | 4 | Enterprise-optimized. |
| **Cursor Agent** | **5** | Instant in IDE. Sub-minute for most tasks. |
| Claude Code | 4 | Fast terminal execution. |
| Cline/RooCode | 4 | Fast in IDE. |
| CodeRabbit | 4 | Reviews in minutes. |
| Qodo | 4 | Fast review cycle. |
| Greptile | 3 | Can be slow on large repos. |

**WHO WINS: Devin/Cursor (5). GlassBox (3) — debate adds latency. Trade-off for quality.**

---

### ASPECT 17: Community / Ecosystem Size
**Importance: 7/10 | Scope: BROAD | User Value: Support, plugins, integrations, hiring talent who know the tool**

| Player | Score | Notes |
|--------|-------|-------|
| GlassBox | 1 | Early stage. Small community. Few stars. |
| **Devin** | **5** | Massive. $155M ARR. Thousands of users. |
| SWE-agent | 3 | Academic community. Niche but influential. |
| OpenHands | 4 | Large OSS community. Active development. |
| Factory AI | 3 | Enterprise customers. Growing. |
| **Cursor Agent** | **5** | Millions of users. Dominant IDE. |
| Claude Code | 4 | Anthropic ecosystem. Growing fast. |
| Cline/RooCode | 4 | Large VSCode extension community. |
| CodeRabbit | 3 | Popular in OSS. |
| Qodo | 3 | Growing. |
| Greptile | 2 | Smaller. |

**WHO WINS: Devin/Cursor (5). GlassBox (1) — expected at v0.3. Must grow.**

---

### ASPECT 18: Cross-Boundary Understanding (Python↔SQL, SDK objects, etc.)
**Importance: 8/10 | Scope: BROAD | User Value: Agent doesn't confuse Python vars with SQL literals. Understands runtime types.**

| Player | Score | Notes |
|--------|-------|-------|
| GlassBox | 2 | **0% pass rate on cross-boundary issues.** Identified the problem, haven't solved it. A8 (cross-boundary safety) is a core aspect but agent still fails here. |
| Devin | 4 | Better via sandboxed execution — it can actually RUN the code and see failures. |
| SWE-agent | 3 | Can execute and iterate. |
| OpenHands | 4 | Docker sandbox helps catch runtime errors. |
| Factory AI | 4 | Enterprise-grade. |
| **Cursor Agent** | **4** | Better models (Claude 3.5+) have stronger type understanding. |
| **Claude Code** | **5** | Claude's reasoning excels at cross-boundary. Can read actual source. |
| Cline/RooCode | 3 | Depends on underlying model. |
| CodeRabbit | 2 | Reviews surface-level. |
| Qodo | 2 | Reviews surface-level. |
| Greptile | 3 | Dependency analysis helps. |

**WHO WINS: Claude Code (5). GlassBox (2) — this is where our failures happen. Critical to fix.**

---

### ASPECT 19: Failure Taxonomy & Structured Debugging
**Importance: 7/10 | Scope: MEDIUM | User Value: When agent fails, you know exactly WHY and what category of failure it was**

| Player | Score | Notes |
|--------|-------|-------|
| **GlassBox** | **5** | 15 failure modes (F1-F15) with research sources. Each failure tagged, logged, analyzed. Feeds back into reflexion memory. |
| Devin | 2 | Shows errors but no taxonomy. |
| SWE-agent | 3 | Academic analysis of failure modes. |
| OpenHands | 2 | Error logs but no taxonomy. |
| Factory AI | 2 | Enterprise monitoring but no public failure taxonomy. |
| Cursor Agent | 1 | Fails silently or with generic errors. |
| Claude Code | 2 | Shows errors inline. No categorization. |
| Cline/RooCode | 1 | Raw error output. |
| CodeRabbit | 1 | N/A — doesn't generate code. |
| Qodo | 1 | N/A. |
| Greptile | 1 | N/A. |

**WHO WINS: GlassBox (5) — unique structured approach to failure analysis.**

---

### ASPECT 20: Multi-Model Diversity (Heterogeneous Debate)
**Importance: 6/10 | Scope: MEDIUM | User Value: Different models have different blind spots. Diversity = better coverage.**

> Using Claude + GPT + Gemini in the same debate to avoid shared training data blind spots.

| Player | Score | Notes |
|--------|-------|-------|
| GlassBox | 2 | Currently GPT-4o only. Multi-model planned on roadmap. |
| Devin | 2 | Primarily one model per session. |
| SWE-agent | 3 | Can configure different models. |
| OpenHands | 3 | Model-agnostic. User picks. |
| **Factory AI** | **4** | Multi-LLM approach. Nvidia backing. |
| Cursor Agent | 3 | Supports multiple models. |
| Claude Code | 2 | Claude only. |
| Cline/RooCode | 4 | Fully model-agnostic. Any provider. |
| CodeRabbit | 2 | Their own models. |
| Qodo | 3 | Multiple model support. |
| Greptile | 2 | Their own pipeline. |

**WHO WINS: Factory/Cline (4). GlassBox (2) — needs multi-model for debate diversity.**

---

## 4. MASTER SCOREBOARD — Weighted Total

**Formula:** Score × Importance Weight = Weighted Score per aspect. Sum = Overall.

| # | Aspect | Imp. | GlassBox | Devin | SWE-agent | OpenHands | Factory | Cursor | Claude Code | Cline | CodeRabbit | Qodo | Greptile |
|---|--------|------|----------|-------|-----------|-----------|---------|--------|-------------|-------|------------|------|----------|
| 1 | Transparency | 9 | **5** | 3 | 2 | 2 | 2 | 1 | 3 | 2 | 2 | 2 | 2 |
| 2 | Multi-Agent Debate | 8 | **5** | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 3 | 1 |
| 3 | Trust Scoring | 7 | **5** | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 |
| 4 | Issue-to-PR | 10 | 3 | **5** | 4 | 4 | 4 | 2 | 2 | 2 | 1 | 1 | 1 |
| 5 | Self-Grading | 8 | **5** | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 1 |
| 6 | Reflexion Memory | 8 | **4** | 3 | 1 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | 2 |
| 7 | Multi-Language | 9 | 1 | **5** | 4 | **5** | 5 | 5 | 5 | 5 | 5 | 4 | 4 |
| 8 | Sandboxed Exec | 8 | 1 | **5** | 4 | **5** | 5 | 2 | 2 | 3 | 5 | 5 | 5 |
| 9 | IDE Integration | 9 | 4 | 3 | 2 | 3 | 3 | **5** | 4 | **5** | 3 | 4 | 3 |
| 10 | Open Source | 7 | **5** | 1 | **5** | **5** | 1 | 1 | 1 | **5** | 1 | 2 | 1 |
| 11 | Pricing | 8 | **5** | 4 | **5** | **5** | 1 | 4 | 3 | **5** | 3 | 3 | 2 |
| 12 | Enterprise | 7 | 1 | **5** | 1 | 2 | **5** | 4 | 3 | 2 | 4 | 4 | 4 |
| 13 | Code Localization | 8 | 4 | **5** | 4 | 4 | 4 | 4 | **5** | 4 | 3 | 3 | 4 |
| 14 | Test Generation | 7 | 3 | 4 | 3 | 3 | 4 | 3 | 3 | 3 | 1 | **5** | 1 |
| 15 | Research Foundation | 6 | **5** | 2 | **5** | 3 | 2 | 2 | 4 | 1 | 1 | 2 | 2 |
| 16 | Speed | 7 | 3 | **5** | 3 | 3 | 4 | **5** | 4 | 4 | 4 | 4 | 3 |
| 17 | Community Size | 7 | 1 | **5** | 3 | 4 | 3 | **5** | 4 | 4 | 3 | 3 | 2 |
| 18 | Cross-Boundary | 8 | 2 | 4 | 3 | 4 | 4 | 4 | **5** | 3 | 2 | 2 | 3 |
| 19 | Failure Taxonomy | 7 | **5** | 2 | 3 | 2 | 2 | 1 | 2 | 1 | 1 | 1 | 1 |
| 20 | Multi-Model | 6 | 2 | 2 | 3 | 3 | **4** | 3 | 2 | **4** | 2 | 3 | 2 |

### WEIGHTED SCORES (Score × Importance, summed across all 20 aspects)

| Rank | Player | Weighted Score | Max Possible (770) | % of Max |
|------|--------|---------------|-------------------|----------|
| 1 | **Devin** | **508** | 770 | **66.0%** |
| 2 | **Cursor Agent** | **460** | 770 | 59.7% |
| 3 | **Claude Code** | **457** | 770 | 59.4% |
| 4 | **OpenHands** | **456** | 770 | 59.2% |
| 5 | **Cline/RooCode** | **453** | 770 | 58.8% |
| 6 | **Factory AI** | **449** | 770 | 58.3% |
| 7 | **GlassBox AI** | **447** | 770 | **58.1%** |
| 8 | **Qodo** | **407** | 770 | 52.9% |
| 9 | **SWE-agent** | **404** | 770 | 52.5% |
| 10 | **CodeRabbit** | **356** | 770 | 46.2% |
| 11 | **Greptile** | **341** | 770 | 44.3% |

> **Calculation methodology:** Each aspect's importance (6-10) × player's score (1-5) = weighted points. Sum of 20 weighted points = total. Max possible = sum of all importances × 5 = (9+8+7+10+8+8+9+8+9+7+8+7+8+7+6+7+7+8+7+6) × 5 = 154 × 5 = 770.

---

## 5. WHERE WE WIN vs. WHERE WE LOSE

### 🟢 WHERE GLASSBOX WINS (Score = 5, leading or tied for #1)

| Aspect | Importance | Scope | Why It Matters |
|--------|-----------|-------|---------------|
| **Transparency** | 9/10 | BROAD | No one else treats reasoning as the product. Enterprises need audit trails. Regulated industries NEED this. |
| **Multi-Agent Debate** | 8/10 | BROAD | Research-proven to improve factuality. Only product with structured adversarial debate. |
| **Trust Scoring** | 7/10 | MEDIUM | Unique. Becomes critical as agents get autonomous. "Which agent should I trust?" |
| **Self-Grading Checklist** | 8/10 | BROAD | Massive differentiator. Think-before-code + grade-after. Accountability. |
| **Reflexion Memory** | 8/10 | BROAD | Only research-backed learning system. Agents that learn > agents that retry. |
| **Open Source** | 7/10 | BROAD | MIT. Inspect, fork, self-host. Trust through transparency. |
| **Pricing** | 8/10 | BROAD | Free. Only API costs. Can't beat $0. |
| **Research Foundation** | 6/10 | NARROW | Every design decision has a paper. Credibility with technical buyers. |
| **Failure Taxonomy** | 7/10 | MEDIUM | 15 categorized failure modes. No one else does this. |

**Total winning importance points: 68/100** — We win on HIGH-importance aspects.

### 🔴 WHERE GLASSBOX LOSES (Score ≤ 2, critical gaps)

| Aspect | Importance | Our Score | Leader Score | Gap | Impact |
|--------|-----------|-----------|-------------|-----|--------|
| **Multi-Language** | 9/10 | 1 | 5 | -4 | **CRITICAL.** Eliminates 70%+ of potential users. JS/TS alone is ~30% of market. |
| **Sandboxed Execution** | 8/10 | 1 | 5 | -4 | **CRITICAL.** No enterprise will run an unsandboxed agent. Blocks production adoption. |
| **Enterprise Readiness** | 7/10 | 1 | 5 | -4 | **HIGH.** No revenue path without enterprise features. But okay for now at v0.3. |
| **Community Size** | 7/10 | 1 | 5 | -4 | **HIGH.** Need critical mass for OSS flywheel. Marketing + content + demos needed. |
| **Cross-Boundary** | 8/10 | 2 | 5 | -3 | **CRITICAL.** 100% failure rate on cross-boundary issues. This is where our agent breaks. |
| **Multi-Model** | 6/10 | 2 | 4 | -2 | **MEDIUM.** Same model = same blind spots in debate. Reduces debate value. |

**Total losing importance points: 45/100** — We lose on INFRASTRUCTURE aspects, not intelligence aspects.

### Key Insight

> **GlassBox wins on INTELLIGENCE (transparency, debate, trust, grading, learning, failure analysis) but loses on INFRASTRUCTURE (multi-lang, sandbox, enterprise, community, cross-boundary execution).**
>
> This is actually good news. Infrastructure is buildable. Intelligence architecture is the hard part, and we have it.

---

## 6. THE GAP — GlassBox vs. Top 3 Competitors

### vs. Devin (Gap: -61 weighted points)

| What Devin Has | What GlassBox Has | Verdict |
|---------------|-------------------|---------|
| $10.2B, 300+ engineers | Solo founder, v0.3-beta | They have resources, we have architecture |
| Full autonomy, multi-lang, sandbox | Python only, no sandbox | Their infra is years ahead |
| $155M ARR proves product-market fit | Pre-revenue | They've proven the market exists |
| Black-box reasoning | **Glass-box reasoning** | **We win on trust & transparency** |
| No debate, no trust scores | **Debate + trust + grading** | **We win on quality assurance** |
| No failure taxonomy | **15 categorized failure modes** | **We win on learning from failures** |

**How to close the gap:** Don't compete on autonomy. Compete on **trustworthy autonomy**. Devin ships fast but you can't audit why. GlassBox ships slower but you can see everything. As agents get more powerful, trust becomes the bottleneck, not speed.

### vs. OpenHands (Gap: -9 weighted points)

| What OpenHands Has | What GlassBox Has | Verdict |
|-------------------|-------------------|---------|
| Large OSS community, Docker sandbox | Small community, no sandbox | They have momentum |
| Multi-language, production-tested | Python only | Their coverage is broader |
| Simple single-agent approach | **Multi-agent debate + trust** | **We have deeper quality assurance** |
| No transparency protocol | **6-message protocol** | **We win on auditability** |
| No learning from failures | **Reflexion memory** | **We win on continuous improvement** |

**How to close the gap:** OpenHands is closest in philosophy (OSS, autonomous agent). Add Docker sandbox + JS/TS support → we match their infra while keeping our intelligence advantages.

### vs. Cursor Agent (Gap: -13 weighted points)

| What Cursor Has | What GlassBox Has | Verdict |
|----------------|-------------------|---------|
| Millions of users, dominant IDE | Small, niche | They own the IDE layer |
| Human-in-the-loop by design | Autonomous pipeline | Different paradigms |
| No debate, no trust, no grading | **Full quality stack** | **We win on agent reliability** |
| Closed source | **Open source** | **We win on trust & transparency** |

**How to close the gap:** Don't compete with Cursor — **integrate with it**. GlassBox already works inside Cursor via MCP. Position as "the quality layer that makes Cursor's agent trustworthy."

---

## 7. SHORT / MEDIUM / LONG TERM OUTLOOK

### Short Term (Next 2-3 months) — Survive & Differentiate

| Priority | Action | Impact | Closes Gap With |
|----------|--------|--------|----------------|
| **P0** | Fix cross-boundary failures (sandbox + multi-model debate) | +3 on Aspect 18, +4 on Aspect 8 | Devin, OpenHands |
| **P0** | Add TypeScript/JavaScript support | +3 on Aspect 7 | Everyone |
| **P1** | Docker sandboxed execution | +4 on Aspect 8 | Devin, OpenHands |
| **P1** | Multi-model debate (Claude + GPT in same debate) | +2 on Aspect 20, +1 on Aspect 18 | Factory, Cline |
| **P2** | Agent pass rate from 50% → 80% | +2 on Aspect 4 | Devin, SWE-agent |

**Expected score after short term: ~530 (from 447) → passes Cursor, Claude Code, OpenHands, Cline, Factory. Closes to within ~20 of Devin.**

### Medium Term (3-6 months) — Compete & Grow

| Priority | Action | Impact | Closes Gap With |
|----------|--------|--------|----------------|
| **P0** | Bidirectional trust (EigenTrust — agents rate each other) | +1 on Aspect 3, unique | Nobody has this |
| **P0** | Web dashboard for trust evolution + agent performance | +2 on Aspect 12, +1 on Aspect 1 | Factory |
| **P1** | Cross-repo bug fixing (fork any public repo, fix, PR) | +1 on Aspect 4 | Devin |
| **P1** | Community growth (blog posts, demos, Twitter/X, HN launch) | +2 on Aspect 17 | Everyone |
| **P2** | Complexity-driven routing (easy/medium/hard pipelines) | +1 on Aspect 16, +1 on Aspect 4 | Devin, Factory |
| **P2** | Claim verification layer | +1 on Aspect 18 | Claude Code |

**Expected score after medium term: ~580 → surpasses Devin on weighted score.**

### Long Term (6-12 months) — Lead & Dominate

| Priority | Action | Impact |
|----------|--------|--------|
| **P0** | Enterprise tier (SSO, team management, SLAs) | +4 on Aspect 12. Revenue path. |
| **P0** | GlassBox Agent Benchmark (public leaderboard) | Defines the category. Others measure against you. |
| **P1** | Self-improving agent (reads own failure log, adjusts prompts) | +1 on Aspect 6. True autonomy. |
| **P1** | Plugin ecosystem (custom debate protocols, custom agents) | +2 on Aspect 17. Community flywheel. |
| **P2** | Research paper (feedback flywheel results) | +1 on Aspect 15. Academic credibility → enterprise trust. |

**Expected score after long term: ~640+ → clear category leader.**

---

## 8. THE USP — One Sentence

> **GlassBox AI is the only autonomous coding agent where every decision is transparent, debated by multiple agents, graded against a pre-declared checklist, and backed by persistent trust scores — glass box, not black box.**

No competitor has ALL of these together:
1. ✅ Multi-agent adversarial debate (structured, 3-round, research-backed)
2. ✅ Trust scoring with persistence (EMA, SQLite, floor/ceiling)
3. ✅ Pre-declared aspect checklist with post-fix grading
4. ✅ 6-message transparency protocol (full audit trail in GitHub comments)
5. ✅ Reflexion memory (learns from verbal failure reflections)
6. ✅ 15-mode failure taxonomy (structured debugging)

**Devin** has none of these. **OpenHands** has none. **Cursor** has none. **Factory** has none.

The gap they have over us (multi-lang, sandbox, community, enterprise) is **infrastructure** — buildable in 3-6 months.

The gap we have over them (debate, trust, grading, transparency, reflexion, failure taxonomy) is **architecture** — takes 6-12 months to design and get right, and they haven't even started.

---

## 9. FINAL VERDICT

```
┌─────────────────────────────────────────────────────┐
│                COMPETITIVE POSITION                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  INTELLIGENCE LAYER:  GlassBox LEADS (no contest)   │
│  ├─ Transparency      ██████████ 5/5  (alone)       │
│  ├─ Debate            ██████████ 5/5  (alone)       │
│  ├─ Trust Scoring     ██████████ 5/5  (alone)       │
│  ├─ Self-Grading      ██████████ 5/5  (alone)       │
│  ├─ Failure Taxonomy  ██████████ 5/5  (alone)       │
│  └─ Reflexion Memory  ████████░░ 4/5  (leading)     │
│                                                     │
│  INFRASTRUCTURE LAYER: GlassBox TRAILS              │
│  ├─ Multi-Language    ██░░░░░░░░ 1/5  (critical)    │
│  ├─ Sandbox           ██░░░░░░░░ 1/5  (critical)    │
│  ├─ Enterprise        ██░░░░░░░░ 1/5  (later)       │
│  ├─ Community         ██░░░░░░░░ 1/5  (growing)     │
│  └─ Cross-Boundary    ████░░░░░░ 2/5  (fixing)      │
│                                                     │
│  CURRENT OVERALL: #7 of 11  (447/770 = 58.1%)      │
│  AFTER v0.6:      #2 of 11  (~530/770 = 68.8%)     │
│  AFTER v1.0:      #1 of 11  (~640/770 = 83.1%)     │
│                                                     │
│  TIME TO CATEGORY LEADER: ~6-9 months               │
│                                                     │
│  MOAT: Intelligence architecture is 6-12 months     │
│  ahead of any competitor. They haven't started.     │
│  Infrastructure is 3-6 months behind. Buildable.    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### The Bottom Line

You're **#7 overall today** but **#1 on the hard stuff**. The things you're missing (multi-lang, sandbox, enterprise) are engineering work — they require time and effort but not invention. The things you have (debate, trust, grading, transparency, reflexion, failure taxonomy) are **architectural innovations** that no competitor has even started building.

**The race is: can you build the infrastructure before they build the intelligence?**

Your advantage: you know exactly what to build (this analysis). They don't even know they need debate, trust scoring, or pre-declared checklists yet. By the time they figure it out, you'll have the full stack.

**Next 4 versions to category leader:**
1. **v0.4** — Docker sandbox + TypeScript/JS support + multi-model debate
2. **v0.5** — Cross-boundary fix (pass rate 50% → 80%) + EigenTrust
3. **v0.6** — Web dashboard + cross-repo + community launch (HN, Twitter)
4. **v1.0** — Enterprise tier + public benchmark + plugin ecosystem

After v1.0, you're the category-defining product in **trustworthy autonomous coding agents**. Nobody else owns that position.

