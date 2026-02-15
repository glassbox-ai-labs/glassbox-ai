# Agent Pipeline Speed Optimization Report

## Baseline: ~60 seconds per issue (Issue #102, Run 22039735631)

| Phase | Time | % |
|-------|------|---|
| Ack job (separate runner) | ~6s | 10% |
| Git checkout | ~1s | 2% |
| Python setup | ~2s | 3% |
| **pip install (aider-chat!)** | **~25s** | **42%** |
| Git config | ~1s | 2% |
| LLM #1 Manager classify (gpt-4o) | ~5s | 8% |
| LLM #2 JuniorDev fix (gpt-4o) | ~4s | 7% |
| GitHub API (8x sequential) | ~4s | 7% |
| Test suite (52 tests) | ~2s | 3% |
| Git push + PR | ~3s | 5% |
| Source read (2x all files) | ~1s | 2% |
| Post-steps | ~6s | 10% |

## Research Sources

- **OpenAI Latency Guide** - 7 principles: faster model, fewer tokens, fewer requests, parallelize
- **uv (Astral)** - Rust pip replacement, 10-100x faster
- **GA4GC (UCL paper)** - Smaller models for classification in coding agents
- **GitHub Actions Cache** - Venv caching eliminates pip install on cache hit
- **SWE-bench** - Targeted file selection, minimal test scope
- **Adam Johnson** - Cached venvs pattern for GitHub Actions

---

## 30 Optimizations

| # | Optimization | Impact | Complexity | Effort | Known Pattern | Stability | Risk | Value-Add | Emoji |
|---|-------------|--------|------------|--------|---------------|-----------|------|-----------|-------|
| 1 | **Remove aider-chat from pip install** - not used, adds ~20s of deps | ⚡⚡⚡ ~20s | 🟢 Trivial | 1 line | pip best practice | 🛡️ Rock solid | 🟢 0% | 🟢 33% faster | 🗑️ |
| 2 | **Remove MCP from requirements.txt** - agent doesn't use it | ⚡⚡ ~3s | 🟢 Trivial | 1 line | Dep pruning | 🛡️ Rock solid | 🟢 0% | 🟢 5% faster | 🗑️ |
| 3 | **Remove python-dotenv** - not used in CI agent | ⚡ ~1s | 🟢 Trivial | 1 line | Dep pruning | 🛡️ Rock solid | 🟢 0% | 🟢 2% faster | 🗑️ |
| 4 | **Pin exact versions in requirements.txt** - skip resolution | ⚡ ~2s | 🟢 Easy | 5 lines | pip best practice | 🛡️ Rock solid | 🟢 0% | 🟢 3% faster | 📌 |
| 5 | **Use uv instead of pip** - 10-100x faster install | ⚡⚡⚡ ~20s | 🟡 Medium | 3 lines | Astral uv | ⚠️ New tool | 🟡 10% | 🟢 33% faster | 🚀 |
| 6 | **Cache virtualenv in GH Actions** - skip install on hit | ⚡⚡⚡ ~24s | 🟡 Medium | 10 lines | actions/cache | 🛡️ Proven | 🟡 5% | 🟢 40% faster | 💾 |
| 7 | **Merge ack + agent into single job** - skip 2nd runner | ⚡⚡ ~5s | 🟡 Medium | 15 lines | GHA best practice | ⚠️ Moderate | 🟡 10% | 🟢 8% faster | 🔗 |
| 8 | **Use gpt-4o-mini for Manager classify** - faster model | ⚡⚡ ~3s | 🟢 Trivial | 1 line | OpenAI latency guide | 🛡️ Proven | 🟡 5% | 🟢 5% faster | 🧠 |
| 9 | **Don't read sources twice** - pass sources from manager to junior | ⚡ ~0.5s | 🟢 Easy | 3 lines | DRY principle | 🛡️ Rock solid | 🟢 0% | 🟢 1% faster | ♻️ |
| 10 | **Send only issue-referenced files** - not ALL src/glassbox/ | ⚡⚡ ~2s | 🟡 Medium | 15 lines | SWE-bench pattern | ⚠️ Moderate | 🟡 15% | 🟢 3% faster | 🎯 |
| 11 | **Set max_tokens on LLM calls** - cap runaway generation | ⚡ ~1s | 🟢 Trivial | 1 line | OpenAI latency guide | 🛡️ Rock solid | 🟢 0% | 🟢 2% faster | 🔒 |
| 12 | **Skip redundant syntax check** - tests already catch this | ⚡ ~0.5s | 🟢 Trivial | 1 line | Test optimization | 🛡️ Rock solid | 🟢 2% | 🟢 1% faster | ⏭️ |
| 13 | **Reduce test verbosity** - remove -v flag | ⚡ ~0.3s | 🟢 Trivial | 1 line | pytest best practice | 🛡️ Rock solid | 🟢 0% | 🟢 0.5% faster | 🔇 |
| 14 | **Parallel LLM calls (speculative)** - start fix while classifying | ⚡⚡ ~4s | 🔴 Hard | 30 lines | OpenAI parallelize | 💣 High | 🔴 30% | 🟡 7% faster | ⚡ |
| 15 | **Use Predicted Outputs** - OpenAI feature for code edits | ⚡⚡ ~2s | 🟡 Medium | 10 lines | OpenAI feature | ⚠️ Moderate | 🟡 10% | 🟡 3% faster | 🔮 |
| 16 | **Use httpx instead of gh CLI** - skip subprocess per API call | ⚡ ~2s | 🟠 Significant | 50 lines | HTTP best practice | ⚠️ Moderate | 🟡 15% | 🟡 3% faster | 🌐 |
| 17 | **Sparse git checkout** - only src/ and tests/ | ⚡ ~0.5s | 🟢 Easy | 3 lines | GHA optimization | 🛡️ Proven | 🟢 2% | 🟢 1% faster | 📂 |
| 18 | **Pre-built Docker image** - eliminate pip install entirely | ⚡⚡⚡ ~25s | 🔴 Hard | 30 lines | Docker CI pattern | ⚠️ Maintenance | 🟡 10% | 🟢 42% faster | 🐳 |
| 19 | **Shorter prompts** - trim boilerplate from classify/fix prompts | ⚡ ~1s | 🟡 Medium | 10 lines | OpenAI: fewer input tokens | ⚠️ Moderate | 🟡 10% | 🟢 2% faster | ✂️ |
| 20 | **Rule-based template selection** - regex not LLM for obvious issues | ⚡⚡ ~5s | 🟠 Significant | 30 lines | SWE-bench pattern | 💣 High | 🟡 20% | 🟡 8% faster | 📏 |
| 21 | **Combine Manager+JuniorDev into 1 LLM call** - classify+fix together | ⚡⚡ ~4s | 🟠 Significant | 40 lines | OpenAI: fewer requests | 💣 High | 🔴 25% | 🟡 7% faster | 🔄 |
| 22 | **Cache LLM responses** - hash prompt, cache for identical issues | ⚡⚡ ~8s | 🟠 Significant | 25 lines | LLM caching pattern | ⚠️ Moderate | 🟡 10% | 🟡 13% faster | 🗄️ |
| 23 | **Async GitHub API calls** - concurrent.futures for parallel calls | ⚡ ~2s | 🟡 Medium | 20 lines | asyncio pattern | ⚠️ Moderate | 🟡 10% | 🟡 3% faster | 🔀 |
| 24 | **Run only affected tests** - not all 52 | ⚡ ~1s | 🟡 Medium | 10 lines | pytest -k pattern | ⚠️ Moderate | 🟡 15% | 🟢 2% faster | 🎯 |
| 25 | **Prefetch issue in ack job** - pass to agent, skip API call | ⚡ ~1s | 🟡 Medium | 10 lines | GHA outputs | 🛡️ Proven | 🟢 5% | 🟢 2% faster | 📨 |
| 26 | **Use gpt-4o-mini for BOTH calls** - fastest model | ⚡⚡ ~5s | 🟢 Trivial | 1 line | OpenAI latency guide | ⚠️ Quality risk | 🟡 20% | 🟡 8% faster | 🧠 |
| 27 | **Stream LLM + process early** - start parsing as tokens arrive | ⚡ ~1s | 🟠 Significant | 25 lines | OpenAI streaming | ⚠️ Moderate | 🟡 10% | 🟢 2% faster | 📡 |
| 28 | **Remove pytest from agent deps** - use lightweight checker | ⚡ ~1s | 🟡 Medium | 5 lines | Dep pruning | 💣 High | 🔴 25% | 🟢 2% faster | 🧹 |
| 29 | **Use --no-compile for pip** - skip bytecode compilation | ⚡ ~1s | 🟢 Trivial | 1 line | pip optimization | 🛡️ Rock solid | 🟢 0% | 🟢 2% faster | ⏩ |
| 30 | **Warm pip cache with lockfile** - pip freeze > lockfile | ⚡ ~2s | 🟡 Medium | 5 lines | pip best practice | 🛡️ Proven | 🟢 2% | 🟢 3% faster | 🔐 |

---

## Shortlisted Top 10

Selected by: highest (impact x stability) / (complexity x risk)

| Rank | # | Optimization | Saved | Agent-fixable? |
|------|---|-------------|-------|---------------|
| 1 | 1 | Remove aider-chat from pip install | ~20s | Yes (1 line in YAML) |
| 2 | 2 | Remove MCP from requirements.txt | ~3s | Yes (1 line) |
| 3 | 8 | Use gpt-4o-mini for Manager classify | ~3s | Yes (1 line in settings.py) |
| 4 | 9 | Don't read sources twice in cli.py | ~0.5s | Yes (3 lines) |
| 5 | 11 | Set max_tokens on LLM calls | ~1s | Yes (1 line in base_agent.py) |
| 6 | 12 | Skip redundant syntax check | ~0.5s | Yes (1 line) |
| 7 | 6 | Cache virtualenv in GH Actions | ~24s | Manual (workflow change) |
| 8 | 4 | Pin exact versions in requirements.txt | ~2s | Yes (5 lines) |
| 9 | 29 | Use --no-compile for pip | ~1s | Yes (1 line in YAML) |
| 10 | 13 | Remove test verbosity -v flag | ~0.3s | Yes (1 line) |

**Projected total savings: ~55s (from ~60s to ~5-8s on cache hit, ~20-25s on cache miss)**
