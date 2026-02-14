# Changelog

All notable changes to GlassBox AI are documented here.

## [v0.3-beta] — 2026-02-15

### Added
- **GlassBox Agent v0.3-beta** — renamed from "Agent .3", externalized name/version to `config.py`
- **Code localization** via [Aider RepoMap](https://aider.chat/2023/10/22/repomap.html) — tree-sitter + PageRank replaces hardcoded `SOURCE_FILES`
- **12 core aspects** hardcoded in `config.py` — readability, modularity, no-hardcoding, test coverage, backward compat, minimal diff, error handling, cross-boundary safety, import hygiene, idempotency, type correctness, MRU
- **Message 0** — immediate "GlassBox Agent picked up #N" feedback before analysis starts
- **Marginal Return of Utility (MRU)** framework for deciding edge case count
- **`locator.py`** — `Locator` class using Aider RepoMap for dynamic code discovery
- **`data/` directory** — moved `reflections.json` out of `scripts/agent/`
- **`glassbox-agent` label** — replaces `agent` label for triggering the workflow
- **Competitor comparison** in README (Devin, SWE-agent, OpenHands, CodeRabbit, Greptile)
- **Pre-implementation checklist** — aspects → challenges → edge cases → implement → verify

### Changed
- All agent files use `AGENT_NAME`/`AGENT_VERSION`/`AGENT_LABEL` constants (no hardcoded strings)
- Analyzer prompt now includes repo map + 12 mandatory core aspects
- 6-message protocol (was 5 — added Message 0)
- Workflow triggers on `glassbox-agent` label (was `agent`)

### Fixed
- Leftover `read_sources()` reference in retry loop causing `NameError` in CI
- Issue #27 (PEP 8 E401) fixed end-to-end by the agent → PR #28 merged

---

## [0.3.0] — 2025-02-13

### Added
- **Multi-round debate engine (V2)** — 3 rounds: Position → Reaction → Convergence
- **LLM-as-judge** — detects genuine mind changes in Round 3
- **Trust auto-updates** — persuader trust goes up with before/after deltas
- **Convergence summary** — auto-generated action plan after debate
- **CI pipeline** — 3-stage: unit tests → integration tests → Docker build
- **Docker image** on GHCR (`ghcr.io/glassbox-ai-labs/glassbox-ai`)
- **Dev hot-reload** via `mcp-hmr` (Python 3.12+)
- **20 unit tests** + 5 integration tests
- **macOS Keychain** integration for API key (no .env needed)

### Changed
- Agents now reference each other by `@name` and explicitly say CHANGED/HOLDING
- Trust update formula: EMA with alpha=0.1, floor 0.30, ceiling 1.00

## [0.2.0] — 2025-02-10

### Added
- **Parallel single-shot analysis** (`analyze` tool) — all agents respond simultaneously
- **Trust-weighted consensus** — highest trust agent's response becomes consensus
- **SQLite persistence** — trust scores survive across sessions
- **`trust_scores()` tool** — view all agent scores
- **`update_trust()` tool** — manual trust adjustment

### Changed
- Moved from in-memory scores to SQLite database
- Added temperature tuning per agent

## [0.1.0] — 2025-02-08

### Added
- Initial MCP server with 3 agents: `@architect`, `@pragmatist`, `@critic`
- Basic `analyze` tool — single-round parallel responses
- PyPI package (`pip install glassbox-ai`)
- README with quickstart guide
- `.env.example` for API key configuration
