# GlassBox AI 💎

**Transparent Multi-Agent Systems with Trust Scoring**

The first production-ready framework for building auditable, trustworthy multi-agent AI systems with runtime trust distribution.

---

## 🎯 Vision

Transform AI from black boxes to glass boxes - where every decision is traceable, every agent is accountable, and trust is earned through verified outcomes.

**Problem:** Existing multi-agent frameworks (CrewAI, AutoGen) orchestrate agents but hide their reasoning. You see the final answer, not WHY it was chosen or WHO to trust.

**Solution:** GlassBox AI adds a transparent trust layer - agents debate, trust scores weight their votes, outcomes update reputations, and full provenance chains show exactly how decisions were made.

---

## 📍 Current Status

**Milestone 1 (In Progress):** MCP Server MVP  
**Target:** Feb 15, 2026  
**Status:** 🟡 Building core components

---

## 🗓️ Roadmap & Milestones

### ✅ Milestone 0: Research & Design (DONE)
- [x] Analyze competitive landscape (LIME, SHAP, CrewAI, AutoGen, Vector Institute research)
- [x] Identify unique positioning (trust scoring + claim verification + provenance)
- [x] Define architecture (MCP server → orchestrator → trust DB)

### 🟡 Milestone 1: MCP Server MVP (Feb 13-15, 2026)
**Goal:** Working multi-agent MCP server that integrates with Windsurf

**Deliverables:**
- [x] Project structure
- [ ] `server.py` - MCP protocol handlers
- [ ] `orchestrator.py` - Parallel GPT agent execution with 3 personas
- [ ] `trust_db.py` - SQLite persistence for trust scores
- [ ] `requirements.txt` and `.env.example`
- [ ] Dockerfile for GHCR deployment
- [ ] README with setup instructions
- [ ] Test with Windsurf locally

**Agents (GPT-only for MVP):**
- `@architect` - Long-term thinking, scalability focus
- `@pragmatist` - Ship fast, iterate, business value
- `@critic` - Edge cases, security, failure modes

**Trust Mechanism:**
- Initial scores: 0.85 for all agents
- Update formula: `new_trust = old_trust + 0.1 * (outcome - old_trust)`
- Weighted consensus by trust

---

### 🔲 Milestone 2: Claim Verification Layer (Feb 16-20, 2026)
**Goal:** Add fact-checking to agent responses

**Deliverables:**
- [ ] `verifier.py` - Claim extraction from agent responses
- [ ] Source grounding validation (does citation support claim?)
- [ ] Confidence scoring per claim
- [ ] Provenance chain tracking (claim → agent → source → line number)

**Example:**
```
Agent says: "Use Redis for caching." [Source: docs.redis.io]
Verifier checks: Does source actually recommend Redis for this use case?
Result: ✅ Supported (confidence: 0.92)
```

---

### 🔲 Milestone 3: Web Dashboard (Feb 21-28, 2026)
**Goal:** Visual interface for trust evolution and agent debates

**Deliverables:**
- [ ] FastAPI backend serving agent analysis API
- [ ] React frontend with:
  - Real-time agent conversation display
  - Trust score graphs over time
  - Provenance tree visualization
  - Manual trust adjustment controls
- [ ] Deployed demo at `demo.glassbox-ai.dev`

**UI Mockup:**
```
┌─────────────────────────────────────────┐
│ 🤖 Multi-Agent Analysis                │
├─────────────────────────────────────────┤
│ @architect (Trust: 0.92) 📈            │
│ "Use Postgres with materialized views" │
│                                         │
│ @pragmatist (Trust: 0.85) 📊           │
│ "Start with Redis, migrate later"      │
│                                         │
│ @critic (Trust: 0.88) ⚠️               │
│ "What's your eviction policy?"          │
├─────────────────────────────────────────┤
│ ⚖️ Weighted Consensus: Redis (0.87)    │
└─────────────────────────────────────────┘
```

---

### 🔲 Milestone 4: Multi-Model Support (Mar 1-7, 2026)
**Goal:** Support Claude + GPT + Gemini for true agent diversity

**Deliverables:**
- [ ] Anthropic API integration
- [ ] Google Gemini API integration
- [ ] Agent pool with mixed models:
  - `@architect` → Claude Opus
  - `@pragmatist` → GPT-4o
  - `@critic` → Claude Sonnet
  - `@innovator` → Gemini Pro
- [ ] Cost tracking per agent/model

---

### 🔲 Milestone 5: Production Hardening (Mar 8-15, 2026)
**Goal:** Enterprise-ready deployment

**Deliverables:**
- [ ] Rate limiting and retry logic
- [ ] Error recovery and fallbacks
- [ ] Observability (Prometheus metrics, OpenTelemetry traces)
- [ ] Security audit (API key handling, input validation)
- [ ] Load testing (100 concurrent analyses)
- [ ] Documentation site (docs.glassbox-ai.dev)

---

### 🔲 Milestone 6: CLI & PyPI Release (Mar 16-22, 2026)
**Goal:** Shareable package anyone can install

**Deliverables:**
- [ ] `glassbox` CLI tool
- [ ] PyPI package: `pip install glassbox-ai`
- [ ] Usage examples and tutorials
- [ ] Blog post: "Building Transparent Multi-Agent Systems"
- [ ] LinkedIn case study with screenshots
- [ ] GitHub Sponsors / funding model

**Usage:**
```bash
pip install glassbox-ai

# Analyze a problem
glassbox analyze "Should we use Redis or Postgres?"

# View trust dashboard
glassbox trust-dashboard

# Update trust manually
glassbox update-trust architect --correct
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│  Windsurf Chat / CLI / Web Dashboard       │
└─────────────────┬───────────────────────────┘
                  │ MCP Protocol / API
┌─────────────────▼───────────────────────────┐
│         MCP Server (server.py)              │
│  Tools: multi_agent_analyze,                │
│         get_trust_scores, update_trust      │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│      Orchestrator (orchestrator.py)         │
│  - Parallel agent execution                 │
│  - Weighted consensus                       │
│  - Provenance tracking                      │
└──┬────────────┬────────────┬────────────────┘
   │            │            │
┌──▼──┐   ┌────▼───┐   ┌───▼────┐
│GPT-4│   │GPT-4o  │   │GPT-4   │
│Opus │   │        │   │Turbo   │
└─────┘   └────────┘   └────────┘
 @arch     @pragma      @critic

┌─────────────────────────────────────────────┐
│       Trust DB (trust_db.py)                │
│  SQLite: agent → trust score → history     │
└─────────────────────────────────────────────┘
```

---

## 🎯 Success Metrics

**Technical:**
- [ ] <500ms latency for 3-agent analysis
- [ ] Trust score convergence within 10 iterations
- [ ] 95%+ uptime on demo deployment

**Adoption:**
- [ ] 100 GitHub stars by end of March
- [ ] 50 PyPI downloads/week
- [ ] 1 enterprise POC

**Validation:**
- [ ] Featured in a newsletter (e.g., TLDR AI, The Batch)
- [ ] 1 blog post or paper citing this work
- [ ] Positive feedback from 5 real users

---

## 🚀 Quick Start (After Milestone 1)

### Local Setup
```bash
git clone https://github.com/yourusername/glassbox-ai
cd glassbox-ai
pip install -r requirements.txt

# Add API key
cp .env.example .env
# Edit .env: OPENAI_API_KEY=sk-...

# Run MCP server
python server.py
```

### Windsurf Integration
Add to `~/.codeium/windsurf/mcp_servers.json`:
```json
{
  "glassbox-ai": {
    "command": "python",
    "args": ["/path/to/glassbox-ai/server.py"]
  }
}
```

Restart Windsurf, then:
```
You: "Should we use Redis or Postgres for session storage?"

[Cascade invokes multi_agent_analyze]

🤖 3 agents analyzing...
✅ Consensus ready
```

---

## 📂 Project Structure

```
glassbox-ai/
├── README.md              # This file
├── server.py              # MCP entry point
├── orchestrator.py        # Multi-agent logic
├── trust_db.py           # Trust persistence
├── verifier.py           # (Milestone 2) Claim checking
├── requirements.txt
├── Dockerfile
├── .env.example
├── .gitignore
├── tests/                # (Milestone 5) Test suite
├── docs/                 # (Milestone 5) Documentation
└── web/                  # (Milestone 3) Dashboard
    ├── backend/
    └── frontend/
```

---

## 🤝 Contributing

We're in MVP phase. Contributions welcome after Milestone 1 is complete.

**Roadmap priorities:**
1. Core MCP server stability
2. Claim verification accuracy
3. Trust evolution algorithms
4. Multi-model integration

---

## 📜 License

MIT (open source, shareable, production-ready)

---

## 📧 Contact

Built by [@yourname](https://github.com/yourname)  
LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)

**Building in public.** Follow along for updates on transparent AI systems.

---

## 🔗 Related Work

**Inspiration:**
- [Vector Institute - Agentic Transparency](https://github.com/VectorInstitute/Agentic-Transparency)
- [TrustAgent Survey](https://github.com/Ymm-cll/TrustAgent)
- [ADORE Paper (Atlassian)](https://arxiv.org/abs/2601.18267)

**Frameworks we build on:**
- [CrewAI](https://github.com/crewAIInc/crewAI) - Multi-agent patterns
- [AutoGen](https://github.com/microsoft/autogen) - Agent orchestration
- [InterpretML](https://github.com/interpretml/interpret) - Glass box models

**Our unique contribution:** First to combine trust scoring + claim verification + provenance in a production multi-agent system.

---

**💎 Glass Box over ⬛ Black Box**
