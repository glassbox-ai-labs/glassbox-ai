# Changelog

All notable changes to GlassBox AI are documented here.

## [v1.0.0] - 2026-02-15

### Highlights
- **TAT (Turnaround Time) reduced from 60s to 32s** (47% faster). Label-to-PR now takes ~32s on cache hit, ~42s on cache miss. See `docs/speed-optimization-report.md` for full breakdown with run-by-run proof.

### Added
- **Indent-Capture-Reapply** in `code_editor.py` - preserves original indentation on line replacement (RooCode pattern). Took agent merge rate from 10% to 88%.
- **Virtualenv caching** in CI via `actions/cache@v4` keyed on `hashFiles('requirements.txt')`. Auto-regenerates when deps change.
- **`model_classify` setting** - Manager uses `gpt-4o-mini` for classification (2-3x faster than gpt-4o).
- **`max_tokens=2048`** cap on all LLM calls to prevent runaway generation.
- **Speed optimization report** at `docs/speed-optimization-report.md` with 30 researched techniques, top 10 shortlisted, before/after proof.
- **TAT tracking** in performance dashboard - total time and stepwise breakdown per workflow run.

### Changed
- Manager classify prompt accepts bugs AND code improvements (no longer skips features).
- Source files read once and reused across Manager and JuniorDev (was read twice).
- All dependencies pinned to exact versions in `requirements.txt`.
- Removed `aider-chat` from CI pip install (not used, saved ~36s).
- Removed `mcp` from `requirements.txt` (not used by agent).
- Removed `-v` verbose flag from test runner.
- Renamed agent from v2 to v1 across workflow, PR body, and comments.

### UX/UI Improvements (9 agent-generated PRs merged)
- Professional JuniorDev prefix replaces "Got it, boss!"
- Clickable file paths in JuniorDev comments (GitHub links with line anchors)
- Collapsible hard aspects and hard challenges via `<details>` tags
- HA/HC prefix codes removed from display
- Template description shown in Manager briefing
- Failure messages truncated to 100 chars
- Ack message updated to reflect 10-30s timing

---

## [v0.3-beta] - 2026-02-15

### Added
- **GlassBox Agent v0.3-beta** with **6-message transparency protocol** — the agent posts every step as a comment on the issue thread: Message 0 acknowledges the issue instantly, Message 1 lists 12+ aspects, challenges, and edge cases *before touching code*, Message 2 shows the proposed fix as an IDE-style diff, Message 3 grades every aspect and edge case ✅/❌ via a 3-agent debate (@architect, @pragmatist, @critic), Message 4 pushes the branch and shows tests passing, Message 5 creates the PR with full reasoning chain. No other agent shows you what it's thinking before it codes, or grades its own work against a pre-declared checklist. Glass box, not black box.
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
