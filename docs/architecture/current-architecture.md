# GlassBox AI — Current Architecture (v0.3.0)

## Overview

GlassBox AI is a multi-agent MCP server with trust scoring and multi-round debate. Three AI agents debate any topic, reference each other by name, agree/disagree, converge on a plan, and trust scores update based on who persuades whom.

## System Diagram

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

## Files

| File | Responsibility | Lines |
|------|---------------|-------|
| `src/glassbox/__init__.py` | Package metadata, `__version__` | 4 |
| `src/glassbox/server.py` | MCP server, 4 tools (debate, analyze, trust_scores, update_trust) | 55 |
| `src/glassbox/orchestrator.py` | Multi-agent orchestrator, debate engine, parallel execution | 88 |
| `src/glassbox/trust_db.py` | SQLite trust persistence, EMA updates, floor/ceiling | 69 |

## Agents

| Agent | Model | Temperature | Role |
|-------|-------|-------------|------|
| @architect | GPT-4o | 0.3 | Long-term, scalability, breaks at scale |
| @pragmatist | GPT-4o | 0.5 | Ship fast, iterate, cut scope |
| @critic | GPT-4o-mini | 0.4 | Edge cases, security, failure modes |

## Debate Protocol (V2)

| Round | Instruction |
|-------|-------------|
| Round 1 | State your position. Be direct, no bullet points. |
| Round 2 | React to others. Say "I agree with @X" or "I disagree with @X because". |
| Round 3 | Final position. CHANGED: who influenced you. HOLDING: why. |

After Round 3:
- LLM-as-judge (architect) analyzes transcript for genuine mind changes
- Trust scores update: persuader goes ↑ via EMA
- Convergence summary generated as action plan

## Trust System

- **Persistence:** SQLite (`trust_scores.db`)
- **Initial score:** 0.85 for all agents
- **Update formula:** `new = old + 0.1 * (outcome - old)` (EMA)
- **Floor:** 0.30, **Ceiling:** 1.00
- **Triggers:** Debate persuasion (auto) or manual `update_trust` call

## Key Design Decisions

1. **SQLite over Redis/Postgres** — Zero-config, file-based, sufficient for single-instance
2. **EMA over simple average** — Recent outcomes weigh more, agent reputation is adaptive
3. **LLM-as-judge over rule-based** — Catches nuanced mind changes, not just keyword matching
4. **3 rounds fixed** — Simple, predictable, enough for convergence without token waste
5. **MCP over REST API** — Direct integration with IDE AI assistants
