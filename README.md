# GlassBox AI 💎

**Multi-agent MCP server with trust scoring and multi-round debate.**

[![PyPI](https://img.shields.io/pypi/v/glassbox-ai)](https://pypi.org/project/glassbox-ai/)
[![Tests](https://img.shields.io/badge/tests-20%2F20-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-green)]()
[![Performance Tracking](https://img.shields.io/badge/performance-tracking-blueviolet)](https://agentic-trust-labs.github.io/glassbox-ai/)

<!-- mcp-name: io.github.glassbox-ai-labs/glassbox-ai -->

> **Watching this repo?** Use **Watch > Custom > Pull requests + Releases** to avoid email noise from the autonomous agent's issue comments.

3 AI agents debate any topic, reference each other by name, agree/disagree, converge on a plan, and **trust scores update based on who persuades whom**.

```
━━ ROUND 3 ━━
🔵 @architect: HOLDING — scalability concerns remain valid.
🟢 @pragmatist: CHANGED — @critic's security points convinced me.
🟡 @critic: HOLDING — my edge cases stand.

━━ TRUST UPDATES ━━
📊 @critic 0.85 → 0.86 ↑ (persuaded @pragmatist)
📊 @architect — HELD position (no trust change)
```

---

## 🚀 Install

### Option 1: pip (recommended)
```bash
pip install glassbox-ai
```

### Option 2: From source
```bash
git clone https://github.com/glassbox-ai-labs/glassbox-ai
cd glassbox-ai
pip install -r requirements.txt
```

---

## ⚡ Quick Start — Windsurf / Cursor / Claude Desktop

Add to your MCP config (`~/.codeium/windsurf/mcp_config.json`):

### Production (auto-updates from PyPI):
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

### Dev (hot-reload, no restart needed):
Requires Python 3.12+ and `pip install mcp-hmr`:
```json
{
  "mcpServers": {
    "glassbox-ai": {
      "command": "mcp-hmr",
      "args": ["path/to/scripts/hmr_entry.py:mcp"],
      "env": { "OPENAI_API_KEY": "sk-..." }
    }
  }
}
```

Then ask your AI assistant anything — it will automatically use GlassBox tools.

---

## �️ Tools

| Tool | Description |
|---|---|
| `debate(task)` | 3-round multi-agent debate with trust updates |
| `analyze(task, agents?)` | Parallel single-shot analysis with trust-weighted consensus |
| `trust_scores()` | View current trust scores for all agents |
| `update_trust(agent, was_correct)` | Manually adjust trust based on outcome |

---

## 🤖 Agents

| Agent | Model | Role | Style |
|---|---|---|---|
| 🔵 `@architect` | GPT-4o | Long-term, scalability | Direct, opinionated |
| 🟢 `@pragmatist` | GPT-4o | Ship fast, iterate | Cuts scope, pushes back |
| 🟡 `@critic` | GPT-4o-mini | Edge cases, security | Challenges assumptions |

---

## 🔄 Debate Engine (V2)

3 rounds where agents talk **to each other**:

| Round | Instruction |
|---|---|
| **Round 1** | State your position |
| **Round 2** | React to others — agree/disagree with @names |
| **Round 3** | Final position — say CHANGED or HOLDING and why |

After Round 3:
- **LLM-as-judge** analyzes the transcript for genuine mind changes
- Trust scores update: persuader goes ↑, with before/after deltas
- **Convergence summary** generated as an action plan

---

## � Trust System

- **Persistence:** SQLite — scores survive across sessions
- **Initial score:** 0.85 for all agents
- **Update formula:** Exponential moving average: `new = old + 0.1 * (outcome - old)`
- **Floor/ceiling:** 0.30 – 1.00
- **Triggers:** Debate persuasion (auto) or manual `update_trust` call

---

## 📂 Project Structure

```
glassbox-ai/
├── src/glassbox/
│   ├── server.py          # MCP server - 4 tools
│   ├── orchestrator.py    # Debate engine + parallel execution
│   └── trust_db.py        # SQLite trust persistence
├── scripts/
│   ├── agent/             # GlassBox Agent v0.3-beta
│   │   ├── main.py        # Pipeline orchestrator (6-message protocol)
│   │   ├── locator.py     # Code localization (Aider RepoMap + tree-sitter)
│   │   ├── models.py      # Pydantic types (Aspect, Challenge, EdgeCase, Fix, Grade)
│   │   ├── analyzer.py    # Phase 1: aspects, challenges, edge cases
│   │   ├── coder.py       # Phase 2: generate code approach
│   │   ├── reviewer.py    # Phase 3: debate + grade against checklist
│   │   ├── runner.py      # Apply fix, syntax check, run tests
│   │   ├── messenger.py   # Format 6 GitHub messages
│   │   ├── memory.py      # Reflexion memory (learn from failures)
│   │   ├── github.py      # GitHubClient class (read/write issues, PRs)
│   │   └── config.py      # Constants, 12 core aspects, model config
│   ├── run_local.sh       # Dev: Keychain + mcp-hmr hot reload
│   ├── run_mcp.sh         # Docker runner
│   └── hmr_entry.py       # mcp-hmr wrapper for relative imports
├── tests/
│   ├── test_glassbox.py   # Unit tests
│   └── test_integration.py# Integration tests (needs API key)
├── docs/
│   ├── research/          # Paper explainer HTML + README
│   └── architecture/      # Failure analysis, feedback flywheel
├── github-app/
│   ├── manifest.json      # GitHub App definition (permissions, events)
│   ├── setup.py           # One-time setup: create app, store secrets
│   └── README.md          # App architecture + setup guide
├── data/
│   └── reflections.json   # Reflexion memory (agent learnings)
├── pyproject.toml         # PyPI config (v0.3.0)
├── requirements.txt
├── Dockerfile
├── CHANGELOG.md
└── README.md
```

---

## 🧪 Tests

```bash
pytest tests/ -v   # 23 passed, 5 skipped (integration needs API key)
```

---

## 🤖 GlassBox Agent v0.3-beta

GlassBox Agent takes a GitHub issue and fixes it autonomously. Every step is posted as a comment on the issue thread so you can watch it think, code, debate, test, and ship in real time. This is the **6-message transparency protocol** — no other agent shows you this:

- **Message 0 (ACK):** The moment you label an issue `glassbox-agent`, the agent responds instantly: *"GlassBox Agent picked up #N — creating aspects, challenges, and edge cases..."* You know it's working.
- **Message 1 (THINK):** Before touching any code, the agent lists 12+ aspects it will check (readability, modularity, no-hardcoding, test coverage, backward compatibility, minimal diff, error handling, cross-boundary safety, import hygiene, idempotency, type correctness, MRU), plus challenges that could go wrong, plus edge cases ranked by Marginal Return of Utility. **No other agent shows you what it's thinking before it codes.**
- **Message 2 (CODE):** The proposed fix as an IDE-style diff — what changed, what was intentionally NOT changed, and why. Full context, not just a patch.
- **Message 3 (GRADE):** Every single aspect, challenge, and edge case from Message 1 is graded ✅/❌ with remarks. Three agents (@architect, @pragmatist, @critic) debate the fix and vote. **No other agent grades its own work against a pre-declared checklist.**
- **Message 4 (TEST):** Branch pushed, syntax verified, tests passing, CI pipeline started. You see the proof.
- **Message 5 (SHIP):** Pull request created with a link, summary, and the full reasoning chain. Click merge when you're satisfied.

Every PR is fully traceable: you can see what the agent considered, what it rejected, and why it chose what it chose. **Glass box, not black box.**

**Trigger:** Add the `glassbox-agent` label to any issue.

**Run locally:** `python -m scripts.agent.main <issue_number>`

### How it finds relevant code

Uses [Aider's RepoMap](https://aider.chat/2023/10/22/repomap.html) (tree-sitter + PageRank) to dynamically discover the most important files, classes, and functions in the repo. No hardcoded file lists.

### How it learns

Failures are stored as **Reflexion memory** ([Shinn et al., 2023](https://arxiv.org/abs/2303.11366)) — verbal failure reflections are read before the next attempt. The agent gets smarter over time.

---

## 🏆 How GlassBox Compares

### vs. Autonomous Agents

| Capability | Devin ($500/mo) | SWE-agent | OpenHands | **GlassBox** |
|-----------|----------------|-----------|-----------|-------------|
| Takes GitHub issue, fixes it | ✅ | ✅ | ✅ | ✅ |
| Multi-agent debate | ❌ | ❌ | ❌ | ✅ |
| Trust scoring per agent | ❌ | ❌ | ❌ | ✅ |
| Think-before-code (aspects, edge cases) | ❌ | ❌ | ❌ | ✅ |
| Graded performance checklist | ❌ | ❌ | ❌ | ✅ |
| Reflexion memory (learns from failures) | ❌ | ❌ | Partial | ✅ |
| 5-message transparency protocol | ❌ | ❌ | ❌ | ✅ |
| MCP server (works in any IDE) | ❌ | ❌ | ✅ | ✅ |
| Open source | ❌ | ✅ | ✅ | ✅ |
| Code localization (tree-sitter + PageRank) | ❌ | Partial | Partial | ✅ (via Aider RepoMap) |
| Sandboxed execution | ✅ | ✅ | ✅ | 🔲 Planned |
| Multi-language | ✅ | ✅ | ✅ | 🔲 Python only |

**Sources:** Devin pricing and $73M ARR (June 2025) per [Sacra](https://sacra.com/c/cognition/), [TechCrunch](https://techcrunch.com/2025/09/08/cognition-ai-defies-turbulence-with-a-400m-raise-at-10-2b-valuation/). SWE-agent is [open source from Princeton NLP](https://github.com/SWE-agent/SWE-agent). OpenHands is [open source](https://github.com/All-Hands-AI/OpenHands).

### vs. PR Review Bots

| Capability | CodeRabbit | Greptile | Cursor BugBot | **GlassBox** |
|-----------|------------|---------|---------------|-------------|
| Reviews PRs | ✅ | ✅ | ✅ | ✅ (via debate) |
| **Generates fixes** | ❌ | ❌ | ❌ | ✅ |
| **Creates PRs** | ❌ | ❌ | ❌ | ✅ |
| Multi-agent review | ❌ | ❌ | ❌ | ✅ (3 agents) |

### What makes GlassBox different

1. **Transparency over black-box** - every PR shows the full reasoning chain: what aspects were considered, what edge cases were checked, what was intentionally NOT changed
2. **Debate over single-agent** - 3 agents argue, not 1 agent guessing
3. **Trust over vibes** - agent reliability is measured and tracked, not assumed
4. **Learning over retry** - failures are stored as Reflexion memory, not just retried blindly

---

## 📊 Agent v2 Eval Results

**7/7 bugs solved on first attempt · 100% first-try rate**

👉 [**View the live performance tracker →**](https://agentic-trust-labs.github.io/glassbox-ai/)

---

## ��️ Roadmap

### ✅ Done
- [x] Multi-agent MCP server with 3 personas
- [x] Multi-round debate engine (3 rounds)
- [x] Trust scoring with SQLite persistence
- [x] LLM-as-judge mind-change detection
- [x] PyPI package (`pip install glassbox-ai`)
- [x] Docker image (GHCR)
- [x] CI pipeline (tests + Docker build)
- [x] Dev hot-reload via mcp-hmr
- [x] GlassBox Agent v0.3-beta (6-message protocol)
- [x] Reflexion memory (learns from past failures)
- [x] 12 core aspects hardcoded (readability, modularity, no-hardcoding, test coverage, etc.)
- [x] Marginal Return of Utility (MRU) framework for edge case generation
- [x] Code localization via Aider RepoMap (tree-sitter + PageRank)
- [x] Message 0 immediate feedback ("agent started")

### 🔲 Next
- [ ] Complexity-driven routing (easy/medium/hard pipelines)
- [ ] Cross-repo bug fixing (fork any public repo, fix, PR)
- [ ] Agent performance ledger (track pass/fail across issues)
- [ ] Pluggable debate protocols
- [ ] Bidirectional trust (agents rate each other - EigenTrust)
- [ ] Multi-model support (Claude, Gemini - heterogeneous debate)
- [ ] Claim verification layer
- [ ] Sandboxed execution (Docker runner)
- [ ] Web dashboard for trust evolution

---

## 🏗️ Architecture

```
┌──────────────────────────────────────┐
│  Windsurf / Cursor / Claude Desktop  │
└──────────────┬───────────────────────┘
               │ MCP (stdio)
┌──────────────▼───────────────────────┐
│  server.py — 4 tools                │
│  debate | analyze | trust | update   │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│  orchestrator.py                     │
│  3-round debate · LLM judge · V1    │
└──┬───────────┬───────────┬───────────┘
   │           │           │
 🔵GPT-4o   🟢GPT-4o   🟡GPT-4o-mini
 @architect  @pragmatist @critic
               │
┌──────────────▼───────────────────────┐
│  trust_db.py — SQLite                │
│  EMA updates · floor 0.30 · cap 1.0 │
└──────────────────────────────────────┘
```

---

## 🔗 Research References

GlassBox AI builds on foundational and cutting-edge research across multi-agent debate, trust systems, grounding, and AI safety. We study these papers to inform every design decision.

### Multi-Agent Debate & Collaboration

| Paper | Venue | What It Contributes | Link | Impact |
|-------|-------|---------------------|------|--------|
| **Improving Factuality and Reasoning in LLMs through Multi-Agent Debate** — Du et al. | NeurIPS 2024 | Foundational proof that multi-agent debate improves factual accuracy and reasoning over single-agent baselines. Multiple LLMs debate, converge on better answers. | [arXiv:2305.14325](https://arxiv.org/abs/2305.14325) | ⭐⭐⭐⭐⭐ |
| **ChatEval: Better LLM-based Evaluators through Multi-Agent Debate** — Chan et al. | ICLR 2024 | Multi-agent debate for *evaluation* — different LLM personas debate quality of generated text, producing human-level judgments. | [arXiv:2308.07201](https://arxiv.org/abs/2308.07201) | ⭐⭐⭐⭐ |
| **Exploring Collaboration Mechanisms for LLM Agents: A Social Psychology View** — Zhang et al. | ACL 2024 | Society of Mind for LLMs — tests debate, reflection, and collaboration mechanisms with easy-going vs. overconfident agent traits. | [OpenReview](https://openreview.net/forum?id=ueqTjOcuLc) | ⭐⭐⭐⭐ |
| **Tree of Thoughts: Deliberate Problem Solving with LLMs** — Yao et al. | NeurIPS 2023 | System-2 deliberation — LLMs explore and evaluate multiple reasoning paths via tree search instead of single-pass generation. | [arXiv:2305.10601](https://arxiv.org/abs/2305.10601) | ⭐⭐⭐⭐⭐ |

### Trust, Reputation & Calibration

| Paper | Venue | What It Contributes | Link | Impact |
|-------|-------|---------------------|------|--------|
| **The EigenTrust Algorithm for Reputation Management in P2P Networks** — Kamvar et al. | WWW 2003 | The original distributed trust algorithm — peers compute global trust via eigenvector of local trust matrix. Foundation for all reputation systems. | [ACM DL](https://dl.acm.org/doi/10.1145/775152.775242) | ⭐⭐⭐⭐⭐ |
| **Trust and Reputation Models for Multiagent Systems** — Pinyol & Sabater-Mir | ACM Computing Surveys 2013 | Comprehensive survey of trust models in MAS — cognitive, game-theoretic, and probabilistic approaches. Defines the design space. | [ACM DL](https://dl.acm.org/doi/10.1145/2816826) | ⭐⭐⭐⭐ |
| **Trusting Your AI Agent Emotionally and Cognitively** — Shang et al. | AAAI/ACM AIES 2024 | Develops a validated scale for measuring human trust in AI agents — cognitive (capability) vs. emotional (comfort) dimensions. | [AIES 2024](https://dl.acm.org/doi/10.5555/3716662.3716779) | ⭐⭐⭐⭐ |
| **A Survey on LLM-as-a-Judge** — Li et al. | arXiv 2024 | Comprehensive survey on using LLMs to evaluate other LLMs — scoring methods, bias, calibration, and reliability. | [arXiv:2411.15594](https://arxiv.org/abs/2411.15594) | ⭐⭐⭐⭐ |

### Grounding & Fact-Checking

| Paper | Venue | What It Contributes | Link | Impact |
|-------|-------|---------------------|------|--------|
| **FACTS Grounding: Evaluating Factuality of LLMs** — Google DeepMind | DeepMind 2024 | Industry benchmark for measuring how accurately LLMs ground responses in source material. Multi-judge evaluation methodology. | [DeepMind Blog](https://deepmind.google/blog/facts-grounding-a-new-benchmark-for-evaluating-the-factuality-of-large-language-models/) | ⭐⭐⭐⭐⭐ |
| **MiniCheck: Efficient Fact-Checking of LLMs on Grounding Documents** — Tang et al. | EMNLP 2024 | 770M parameter model achieves GPT-4-level fact-checking at 400× lower cost. LLM-AggreFact benchmark unifies 11 datasets. | [arXiv:2404.10774](https://arxiv.org/abs/2404.10774) | ⭐⭐⭐⭐ |

### Self-Correction & Iterative Refinement

| Paper | Venue | What It Contributes | Link | Impact |
|-------|-------|---------------------|------|--------|
| **Self-Refine: Iterative Refinement with Self-Feedback** — Madaan et al. | NeurIPS 2023 | LLMs generate output, critique it, and refine — 5-40% improvement across tasks. No training needed, just prompting. | [arXiv:2303.17651](https://arxiv.org/abs/2303.17651) | ⭐⭐⭐⭐⭐ |
| **Reflexion: Language Agents with Verbal Reinforcement Learning** — Shinn et al. | NeurIPS 2023 | Agents learn from verbal failure reflections stored in memory — reaches 91% pass@1 on HumanEval (vs. 80% baseline). No weight updates. | [arXiv:2303.11366](https://arxiv.org/abs/2303.11366) | ⭐⭐⭐⭐⭐ |
| **Training Language Models to Self-Correct via Reinforcement Learning** — Google DeepMind | ICLR 2025 | First method that trains intrinsic self-correction into LLMs via RL — model improves answers without external feedback. | [ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/file/871ac99fdc5282d0301934d23945ebaa-Paper-Conference.pdf) | ⭐⭐⭐⭐ |
| **Code Repair with LLMs gives an Exploration-Exploitation Tradeoff** — NeurIPS 2024 | NeurIPS 2024 | Frames LLM code repair as a tree search with exploration-exploitation tradeoff. Better expansion policies → better fixes. | [NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/d5c56ec4f69c9a473089b16000d3f8cd-Paper-Conference.pdf) | ⭐⭐⭐⭐ |

### AI Safety & Scalable Oversight

| Paper | Venue | What It Contributes | Link | Impact |
|-------|-------|---------------------|------|--------|
| **AI Safety via Debate** — Irving, Christiano & Amodei | arXiv 2018 | Foundational paper — two AI agents debate to help a human judge, even on tasks too complex for the human alone. Zero-sum debate as alignment mechanism. | [arXiv:1805.00899](https://arxiv.org/abs/1805.00899) | ⭐⭐⭐⭐⭐ |
| **Constitutional AI: Harmlessness from AI Feedback** — Bai et al. (Anthropic) | arXiv 2022 | AI self-improvement via constitutional principles — no human labels for harmlessness. RLAIF replaces RLHF for safety. | [arXiv:2212.08073](https://arxiv.org/abs/2212.08073) | ⭐⭐⭐⭐⭐ |
| **Scalable Oversight with Weak LLMs Judging Strong LLMs** — Kenton et al. | NeurIPS 2024 | Empirical test of debate for scalable oversight — weaker judges can supervise stronger AI agents when agents debate. | [NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/899511e37a8e01e1bd6f6f1d377cc250-Paper-Conference.pdf) | ⭐⭐⭐⭐ |

---

## 📜 License

MIT

---

## 📧 Contact

Built by [Sourabh Gupta](https://github.com/sourabharsh) · [GlassBox AI Labs](https://github.com/glassbox-ai-labs)

**💎 Glass Box over ⬛ Black Box - transparency is the product.**
