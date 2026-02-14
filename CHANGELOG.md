# Changelog

All notable changes to GlassBox AI are documented here.

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
