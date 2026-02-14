# GlassBox AI 💎

**Multi-agent MCP server with trust scoring and multi-round debate.**

[![PyPI](https://img.shields.io/pypi/v/glassbox-ai)](https://pypi.org/project/glassbox-ai/)
[![Tests](https://img.shields.io/badge/tests-20%2F20-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-green)]()

<!-- mcp-name: io.github.glassbox-ai-labs/glassbox-ai -->

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
│   ├── server.py          # MCP server — 4 tools
│   ├── orchestrator.py    # Debate engine + parallel execution
│   └── trust_db.py        # SQLite trust persistence
├── tests/
│   ├── test_glassbox.py   # 20 unit tests
│   └── test_integration.py# 5 integration tests (needs API key)
├── scripts/
│   ├── run_local.sh       # Dev: Keychain + mcp-hmr hot reload
│   ├── run_mcp.sh         # Docker runner
│   └── hmr_entry.py       # mcp-hmr wrapper for relative imports
├── pyproject.toml         # PyPI config (v0.3.0)
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🧪 Tests

```bash
pytest tests/ -v   # 20 passed, 5 skipped (integration needs API key)
```

---

## 🗺️ Roadmap

### ✅ Done
- [x] Multi-agent MCP server with 3 personas
- [x] Multi-round debate engine (3 rounds)
- [x] Trust scoring with SQLite persistence
- [x] LLM-as-judge mind-change detection
- [x] PyPI package (`pip install glassbox-ai`)
- [x] Docker image (GHCR)
- [x] CI pipeline (tests + Docker build)
- [x] Dev hot-reload via mcp-hmr
- [x] 20 unit tests passing

### 🔲 Next
- [ ] Pluggable debate protocols
- [ ] Confidence scores per agent response
- [ ] Bidirectional trust (agents rate each other)
- [ ] Early convergence detection (skip Round 3 if unanimous)
- [ ] Dynamic agent hiring (add specialist agents per topic)
- [ ] Web dashboard for trust evolution
- [ ] Multi-model support (Claude, Gemini)
- [ ] Claim verification layer

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

## 🔗 Related Work

- [Du et al. — "Improving Factuality and Reasoning via Multi-Agent Debate"](https://composable-models.github.io/llm_debate/)
- [Anthropic — Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)
- [DebateLLM — Benchmarking Multi-Agent Debate](https://github.com/instadeepai/DebateLLM)
- [ICLR Blog — Multi-Agent Debate Frameworks](https://iclr-blogposts.github.io/2025/blog/mad/)

---

## 📜 License

MIT

---

## 📧 Contact

Built by [Sourabh Gupta](https://github.com/sourabharsh) · [GlassBox AI Labs](https://github.com/glassbox-ai-labs)

**💎 Glass Box over ⬛ Black Box**
