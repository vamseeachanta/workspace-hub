# WRK-1019 Stage 6 Plan Cross-Review Results

wrk_id: WRK-1019
reviewed_at: 2026-03-07T22:30:00Z
review_type: plan_cross_review

## Verdicts

| Reviewer | Verdict | P1 Findings | P2 Findings | Final |
|----------|---------|-------------|-------------|-------|
| Claude | APPROVE | 0 | 2 (P2: compute-balance.py read path, redundant test) | APPROVE |
| Gemini | APPROVE | 0 | 0 (2 non-blocking questions — answered in plan) | APPROVE |
| Codex | REQUEST_CHANGES | 1 (L3 contradiction) | 2 (compute-balance.py scope, ranking undefined) | → APPROVE after fixes |

**Final verdict: APPROVE (post-fix)**

## Findings and Resolutions

| ID | Severity | Reviewer | Finding | Resolution |
|----|----------|----------|---------|------------|
| F-01 | High | Codex | AC#8 references L3 (capability_signals_surfaced) despite L3 being deferred scope | Renamed to `test_capability_signals_compat_no_crash` — compat-only, no L3 rendering |
| F-02 | Medium | Codex | compute-balance.py described as "queue + provider parsing" — blurs L1/L2 boundary | Clarified: L1 only (INDEX.md); L2 = reads pre-computed portfolio-signals.yaml; does NOT write it |
| F-03 | Medium | Codex | "Next 3 to Fund" ranking heuristic undefined | Added: percent_complete desc → priority score desc → ID asc; absent percent_complete = 0 |
| F-04 | Low | Codex | Test count drift: AC table=11, execution step=8 | Aligned: all references now say 11 tests; TDD block has 1:1 AC mapping |
| F-05 | Non-blocking | Gemini | portfolio-signals.yaml sensitivity concern | No sensitive tokens — only WRK category counts and orchestrator names |
| F-06 | Non-blocking | Gemini | AC→test traceability | Added AC-N labels to TDD block (1:1 mapping explicit) |

## Plan Changes Applied

- plan.md AC#8: renamed test, description now "L3 compat — no crash if capability_signals present"
- plan.md Execution Step 3: compute-balance.py responsibilities explicitly bounded (L1+L2 read, no write)
- plan.md Execution Step 4: test count corrected from 8 → 11
- plan.md TDD block: `test_capability_signals_surfaced` → `test_capability_signals_compat_no_crash`; AC-N labels added
- plan.md "Next 3 Actions to Fund": ranking heuristic fully specified
- plan.md Scripts under test: `update-portfolio-signals.sh` correctly marked WRK-1020 scope only

## Stage 7 Unlocked

All P1/P2 findings resolved. Plan is internally consistent. Stage 7 user review of final plan ready.
