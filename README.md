# GlassBox AI 💎

> **Trust is earned, not assumed.**

[![PyPI](https://img.shields.io/pypi/v/glassbox-ai)](https://pypi.org/project/glassbox-ai/)
[![Tests](https://img.shields.io/badge/tests-25%20passed-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-green)]()
[![Live Tracker](https://img.shields.io/badge/live-performance%20tracker-blueviolet)](https://agentic-trust-labs.github.io/glassbox-ai/)

Multi-agent debate engine + autonomous coding agent, powered by trust scores that evolve with every interaction. 3 AI agents argue, converge, and ship — and you see every step.

```
━━ ROUND 3 ━━
🔵 @architect [gpt-4o] (trust:0.87): HOLDING — scalability concerns remain valid.
🟢 @pragmatist [gpt-4o] (trust:0.82): CHANGED — @critic's security points convinced me.
🟡 @critic [gpt-4o-mini] (trust:0.85): HOLDING — my edge cases stand.

━━ TRUST UPDATES ━━
📊 @critic 0.85 → 0.86 ↑ (persuaded @pragmatist)
📊 @architect — HELD position (no change)
```

---

## 🏗️ Architecture

```
                  ┌─────────────────────────────────────────────┐
                  │    Windsurf / Cursor / Claude Desktop        │
                  └──────────────────┬──────────────────────────┘
                                     │ MCP (stdio)
                  ┌──────────────────▼──────────────────────────┐
                  │  🔌 MCP Server — 4 tools                    │
                  │  debate · analyze · trust_scores · update    │
                  └──────────────────┬──────────────────────────┘
                                     │
          ┌──────────────────────────▼──────────────────────────┐
          │                  🔄 Debate Engine                    │
          │          3 rounds · LLM-as-judge · convergence       │
          └───┬──────────────────┬──────────────────┬───────────┘
              │                  │                  │
        🔵 @architect      🟢 @pragmatist     🟡 @critic
          GPT-4o              GPT-4o           GPT-4o-mini
        scalability         ship fast         edge cases
              │                  │                  │
          ┌───▼──────────────────▼──────────────────▼───────────┐
          │              🛡️ Trust Database (SQLite)              │
          │    adaptive EMA · floor 0.30 · ceiling 1.00          │
          └──────────────────────┬──────────────────────────────┘
                                 │
          ┌──────────────────────▼──────────────────────────────┐
          │              🤖 GlassBox Agent v2                    │
          │  🎯 Manager → 🔧 JuniorDev → 🧪 Tester              │
          │  template-driven · line-number editing · auto-PR     │
          └──────────────────────┬──────────────────────────────┘
                                 │
          ┌──────────────────────▼──────────────────────────────┐
          │              🧠 Reflexion Memory                     │
          │  verbal failure reflections · full-title retrieval   │
          └─────────────────────────────────────────────────────┘

          ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
                           PLANNED (future)
          │                                                     │
            🔀 Complexity routing (easy/med/hard pipelines)
          │ 🌐 Cross-repo fixing (fork → fix → PR)             │
            🤝 Bidirectional trust (EigenTrust)
          │ 🔒 Sandboxed execution (Docker runner)              │
            🧬 Multi-model debate (Claude, Gemini)
          │                                                     │
          └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
```

**Solid lines** = built and shipping today. **Dotted lines** = planned.

---

## 🚀 Install

```bash
pip install glassbox-ai
```

Add to your MCP config:
```json
{
  "mcpServers": {
    "glassbox-ai": {
      "command": "glassbox-ai",
      "args": [],
      "env": { "OPENAI_API_KEY": "sk-..." }
    }
  }
}
```

Then ask your AI assistant anything — it will use GlassBox tools automatically.

---

## 🛠️ Tools

| Tool | What it does |
|---|---|
| `debate(task)` | 3-round multi-agent debate with live trust updates |
| `analyze(task, agents?)` | Parallel analysis with trust-weighted consensus |
| `trust_scores()` | View current trust scores for all agents |
| `update_trust(agent, was_correct)` | Manually adjust trust based on outcome |

---

## 🔄 How Debate Works

| Round | What happens |
|---|---|
| **Round 1** | Each agent states their position — direct, opinionated, no fluff |
| **Round 2** | Agents react to each other by `@name` — agree or disagree sharply |
| **Round 3** | Final stance: `CHANGED` or `HOLDING` with reasoning |
| **Judge** | LLM-as-judge detects genuine mind changes vs. lip service |
| **Trust** | Persuader's score ↑ via adaptive EMA; model name shown for transparency |

---

## 🛡️ Trust System

| Property | Value |
|----------|-------|
| **Persistence** | SQLite — survives across sessions |
| **Initial score** | 0.85 for all agents |
| **Update** | Adaptive EMA: `α = 1/(1+total)` — new agents learn fast, established agents stabilize |
| **Bounds** | Floor 0.30, ceiling 1.00 |
| **Triggers** | Debate persuasion (auto) or manual `update_trust` |

Backed by [EigenTrust (Kamvar et al. 2003)](https://dl.acm.org/doi/10.1145/775152.775242) and Bayesian decay principles.

---

## 🤖 GlassBox Agent v2

Autonomous coding agent that takes a GitHub issue and ships a fix. Every step is visible on the issue thread — **glass box, not black box.**

**Trigger:** Label any issue `glassbox-agent`.

### How it works

```
Issue created → 🎯 Manager classifies (template + edge cases)
             → 🔧 JuniorDev generates fix (line-number editing)
             → 🧪 Tester validates (syntax + tests + diff size)
             → ✅ PR created with full reasoning chain
```

### Agent v2 features
- **4 templates:** `typo_fix` · `wrong_value` · `wrong_name` · `swapped_args`
- **Line-number editing** — no more "string not found" errors
- **MRU edge cases** — T1 happy path → T2 input variation → T3 error → T4 boundary
- **Reflexion memory** — learns from past failures ([Shinn et al. 2023](https://arxiv.org/abs/2303.11366))
- **Full-title retrieval** — memory queries the actual issue content, not just `[Bug]`
- **Test-grounded fixes** — agent sees test files alongside source code

---

## 📊 Eval Results

**9/11 agent PRs merged · 2 rejected (indentation issues)**

| Run | Type | Result | PRs Merged |
|-----|------|--------|------------|
| Bug eval (7 bugs) | Bug fixes | ✅ 7/7 first-try | #53 #55 #57 #59 #61 #63 #65 |
| Feature eval (5 features) | New features | ✅ 4/5 solved, 2/4 merged | #71 #72 |

👉 [**Live performance tracker →**](https://agentic-trust-labs.github.io/glassbox-ai/)

---

## 🏆 How GlassBox Compares

| Capability | Devin | SWE-agent | OpenHands | **GlassBox** |
|-----------|-------|-----------|-----------|-------------|
| Issue → PR | ✅ | ✅ | ✅ | ✅ |
| Multi-agent debate | ❌ | ❌ | ❌ | ✅ |
| Trust scoring | ❌ | ❌ | ❌ | ✅ |
| Think-before-code | ❌ | ❌ | ❌ | ✅ |
| Reflexion memory | ❌ | ❌ | Partial | ✅ |
| MCP server (any IDE) | ❌ | ❌ | ✅ | ✅ |
| Open source | ❌ | ✅ | ✅ | ✅ |

**What makes GlassBox different:**
1. **Transparency** — every PR shows the full reasoning chain
2. **Debate** — 3 agents argue, not 1 agent guessing
3. **Trust** — earned through outcomes, not assumed
4. **Learning** — failures become Reflexion memory, not just retries

---

## 🔗 Research

Built on peer-reviewed research across multi-agent debate, trust systems, and AI safety:

- **Multi-Agent Debate** — [Du et al. NeurIPS 2024](https://arxiv.org/abs/2305.14325) · [ChatEval, ICLR 2024](https://arxiv.org/abs/2308.07201)
- **Trust & Reputation** — [EigenTrust, WWW 2003](https://dl.acm.org/doi/10.1145/775152.775242) · [LLM-as-Judge Survey 2024](https://arxiv.org/abs/2411.15594)
- **Self-Correction** — [Reflexion, NeurIPS 2023](https://arxiv.org/abs/2303.11366) · [Self-Refine, NeurIPS 2023](https://arxiv.org/abs/2303.17651)
- **AI Safety** — [AI Safety via Debate, 2018](https://arxiv.org/abs/1805.00899) · [Constitutional AI, 2022](https://arxiv.org/abs/2212.08073) · [Scalable Oversight, NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/899511e37a8e01e1bd6f6f1d377cc250-Paper-Conference.pdf)
- **Grounding** — [FACTS, DeepMind 2024](https://deepmind.google/blog/facts-grounding-a-new-benchmark-for-evaluating-the-factuality-of-large-language-models/) · [MiniCheck, EMNLP 2024](https://arxiv.org/abs/2404.10774)

---

## 📜 License

MIT

---

Built by [Sourabh Gupta](https://github.com/sourabharsh) · [Agentic Trust Labs](https://github.com/agentic-trust-labs)

**💎 Trust is earned, not assumed.**
