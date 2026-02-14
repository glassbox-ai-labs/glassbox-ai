# Research Papers

All foundational and cutting-edge research papers that inform GlassBox AI's design decisions.

Papers are organized by topic. PDFs should be placed in this directory. Links to arXiv/ACM/etc. are listed below.

---

## Multi-Agent Debate & Collaboration

| Paper | Venue | Link |
|-------|-------|------|
| Improving Factuality and Reasoning in LLMs through Multi-Agent Debate — Du et al. | NeurIPS 2024 | [arXiv:2305.14325](https://arxiv.org/abs/2305.14325) |
| ChatEval: Better LLM-based Evaluators through Multi-Agent Debate — Chan et al. | ICLR 2024 | [arXiv:2308.07201](https://arxiv.org/abs/2308.07201) |
| Exploring Collaboration Mechanisms for LLM Agents — Zhang et al. | ACL 2024 | [OpenReview](https://openreview.net/forum?id=ueqTjOcuLc) |
| Tree of Thoughts: Deliberate Problem Solving with LLMs — Yao et al. | NeurIPS 2023 | [arXiv:2305.10601](https://arxiv.org/abs/2305.10601) |

## Trust, Reputation & Calibration

| Paper | Venue | Link |
|-------|-------|------|
| The EigenTrust Algorithm for Reputation Management in P2P Networks — Kamvar et al. | WWW 2003 | [ACM DL](https://dl.acm.org/doi/10.1145/775152.775242) |
| Trust and Reputation Models for Multiagent Systems — Pinyol & Sabater-Mir | ACM Computing Surveys 2013 | [ACM DL](https://dl.acm.org/doi/10.1145/2816826) |
| Trusting Your AI Agent Emotionally and Cognitively — Shang et al. | AAAI/ACM AIES 2024 | [AIES 2024](https://dl.acm.org/doi/10.5555/3716662.3716779) |
| A Survey on LLM-as-a-Judge — Li et al. | arXiv 2024 | [arXiv:2411.15594](https://arxiv.org/abs/2411.15594) |

## Grounding & Fact-Checking

| Paper | Venue | Link |
|-------|-------|------|
| FACTS Grounding: Evaluating Factuality of LLMs — Google DeepMind | DeepMind 2024 | [DeepMind Blog](https://deepmind.google/blog/facts-grounding-a-new-benchmark-for-evaluating-the-factuality-of-large-language-models/) |
| MiniCheck: Efficient Fact-Checking of LLMs on Grounding Documents — Tang et al. | EMNLP 2024 | [arXiv:2404.10774](https://arxiv.org/abs/2404.10774) |

## Self-Correction & Iterative Refinement

| Paper | Venue | Link |
|-------|-------|------|
| Self-Refine: Iterative Refinement with Self-Feedback — Madaan et al. | NeurIPS 2023 | [arXiv:2303.17651](https://arxiv.org/abs/2303.17651) |
| Reflexion: Language Agents with Verbal Reinforcement Learning — Shinn et al. | NeurIPS 2023 | [arXiv:2303.11366](https://arxiv.org/abs/2303.11366) |
| Training Language Models to Self-Correct via RL — Google DeepMind | ICLR 2025 | [ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/file/871ac99fdc5282d0301934d23945ebaa-Paper-Conference.pdf) |
| Code Repair with LLMs gives an Exploration-Exploitation Tradeoff | NeurIPS 2024 | [NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/d5c56ec4f69c9a473089b16000d3f8cd-Paper-Conference.pdf) |

## AI Safety & Scalable Oversight

| Paper | Venue | Link |
|-------|-------|------|
| AI Safety via Debate — Irving, Christiano & Amodei | arXiv 2018 | [arXiv:1805.00899](https://arxiv.org/abs/1805.00899) |
| Constitutional AI: Harmlessness from AI Feedback — Bai et al. (Anthropic) | arXiv 2022 | [arXiv:2212.08073](https://arxiv.org/abs/2212.08073) |
| Scalable Oversight with Weak LLMs Judging Strong LLMs — Kenton et al. | NeurIPS 2024 | [NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/899511e37a8e01e1bd6f6f1d377cc250-Paper-Conference.pdf) |

## Agent Bug Fixing & Software Engineering

| Paper | Venue | Link |
|-------|-------|------|
| SWE-Bench Pro: Can AI Agents Solve Long-Horizon SE Tasks? | arXiv 2025 | [arXiv:2509.16941](https://arxiv.org/abs/2509.16941) |
| SWE-agent: Agent-Computer Interfaces Enable Automated SE — Yang et al. | NeurIPS 2024 | [NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/5a7c947568c1b1328ccc5230172e1e7c-Paper-Conference.pdf) |
| An Empirical Study on LLM-based Agents for Automated Bug Fixing | arXiv 2024 | [arXiv:2411.10213](https://arxiv.org/abs/2411.10213) |

---

## How to add a paper

1. Download the PDF and place it in this directory: `docs/research/<short-name>.pdf`
2. Add the entry to the relevant table above
3. If the paper directly influenced a design decision, note it in `docs/architecture/`
