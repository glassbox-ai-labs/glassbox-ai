# GlassBox Agent v2 — Eval Results

**Run date:** 2026-02-15
**Agent version:** v2 (template-driven multi-agent)
**Model:** gpt-4o-mini (Manager + JuniorDev + Tester)

## Bug Definitions

| # | ID | File | Line | Original | Mutation | Template | Catching Test |
|---|-----|------|------|----------|----------|----------|---------------|
| 1 | E08 | orchestrator.py | 12 | `gpt-4o-mini` | `gpt-4o-mni` | typo_fix | test_critic_model_name |
| 2 | E01 | trust_db.py | 32 | `else 0.85` | `else 0.50` | wrong_value | test_01, test_02 |
| 3 | E11 | trust_db.py | 59 | `max(0.3,` | `max(0.0,` | wrong_value | test_05 |
| 4 | E12 | trust_db.py | 24 | `VALUES (?, 0.85)` | `VALUES (?, 0.50)` | wrong_value | test_01 |
| 5 | E13 | orchestrator.py | 11 | `0.5` | `1.5` | wrong_value | test_16 |
| 6 | E14 | trust_db.py | 23 | `"critic"` in list | removed | wrong_name | test_01 |
| 7 | E15 | trust_db.py | 59 | `min(1.0,` | `min(0.9,` | wrong_value | test_14 |
| 8 | E16 | trust_db.py | 36 | `DESC` | `ASC` | wrong_name | test_13 |
| 9 | E17 | trust_db.py | 47 | `* 100` | `* 10` | wrong_value | test_10 |
| 10 | E18 | orchestrator.py | 10 | `design review` | `code review` | wrong_name | test_22 |

## Results

| # | Bug | Status | Attempts | Template Match | PR |
|---|-----|--------|----------|----------------|-----|
| 1 | E08 typo gpt-4o-mni | ⏳ | — | — | — |
| 2 | E01 default trust 0.50 | ⏳ | — | — | — |
| 3 | E11 floor 0.0 | ⏳ | — | — | — |
| 4 | E12 seed value 0.50 | ⏳ | — | — | — |
| 5 | E13 temp 1.5 | ⏳ | — | — | — |
| 6 | E14 missing critic seed | ⏳ | — | — | — |
| 7 | E15 ceiling 0.9 | ⏳ | — | — | — |
| 8 | E16 sort ASC | ⏳ | — | — | — |
| 9 | E17 accuracy *10 | ⏳ | — | — | — |
| 10 | E18 code review | ⏳ | — | — | — |

## Summary

| Metric | Value |
|--------|-------|
| Total bugs | 10 |
| ✅ Solved | 0 |
| ❌ Failed | 0 |
| Pass rate | 0% |
| Avg attempts | — |
