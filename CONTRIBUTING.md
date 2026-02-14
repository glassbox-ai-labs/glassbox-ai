# Contributing to GlassBox AI

Thanks for your interest in contributing! GlassBox AI is built by the community, for the community.

## Quick Start

```bash
# 1. Fork and clone
git clone https://github.com/<your-username>/glassbox-ai
cd glassbox-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up your API key
cp .env.example .env
# Edit .env with your OpenAI API key

# 4. Run tests
pytest tests/test_glassbox.py -v    # 20 unit tests (no API key needed)
pytest tests/ -v                     # all tests (needs API key)
```

## How to Contribute

### Found a bug?
- Open an [Issue](https://github.com/glassbox-ai-labs/glassbox-ai/issues) using the Bug Report template
- Include: what you expected, what happened, steps to reproduce

### Have an idea?
- Open an [Issue](https://github.com/glassbox-ai-labs/glassbox-ai/issues) using the Feature Request template
- Or start a [Discussion](https://github.com/glassbox-ai-labs/glassbox-ai/discussions)

### Want to write code?
1. Check [Issues](https://github.com/glassbox-ai-labs/glassbox-ai/issues) — look for `good-first-issue` and `help-wanted` labels
2. Comment on the issue to claim it
3. Fork → branch → code → test → PR

### Submitting a Pull Request
1. Create a branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests: `pytest tests/test_glassbox.py -v`
4. Commit with a clear message: `git commit -m "feat: add custom debate strategies"`
5. Push and open a PR against `main`

## Project Structure

```
src/glassbox/
├── server.py          # MCP server — 4 tools
├── orchestrator.py    # Debate engine + parallel execution
└── trust_db.py        # SQLite trust persistence
tests/
├── test_glassbox.py   # 20 unit tests
└── test_integration.py# 5 integration tests (needs API key)
```

## Code Style

- Keep it simple — the entire core is ~200 lines
- No unnecessary abstractions
- Tests for every new feature
- Type hints where practical

## Areas We Need Help

- **Debate strategies** — devil's advocate, red team, Socratic
- **Multi-model support** — Anthropic Claude, Google Gemini, local models
- **Trust visualization** — dashboard for trust score evolution
- **Documentation** — tutorials, examples, use cases
- **Domain adapters** — medical, defence, legal compliance modes

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

---

**`# TODO: agents.build(future together)`**
