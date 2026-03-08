# WRK-1035 Skill Pruning Scorecard

Generated: 2026-03-08 | Session: WRK-1035 Phase 5

## Skills Evaluated

| Skill | Before | After | Reduction | Utility Score | Recommendation |
|-------|--------|-------|-----------|--------------|----------------|
| coordination/workspace/work-queue | 279L | 237L | 15% | 75/100 | Keep — primary lifecycle reference |
| workspace-hub/work-queue-workflow | 352L | 237L | 33% | 85/100 | Keep — key entrypoint + stage contracts |
| workspace-hub/workflow-gatepass | 210L | 200L | 5% | 80/100 | Keep — no-bypass rules are unique |
| workspace-hub/workflow-html | 572L | 399L | 30% | 65/100 | Keep — lifecycle HTML model documented here |
| workspace-hub/wrk-lifecycle-testpack | ~150L | no change | 0% | 60/100 | Keep — test harness spec |

## Pruning Rules Applied
1. Redundant content (verbatim duplicate elsewhere): deleted outright
2. Script-enforced rules (start_stage.py, exit_stage.py, verify-gate-evidence.py): replaced with one-line pointer
3. Verbose narrative prose: condensed to bullets
4. Version history: kept last 5 entries only
5. Inline CSS/JS blocks: replaced with token-list summary + pointer to generator script

## Findings
- 3 skills were over their target line limits; all reduced below limit after pruning
- No unique content was lost — key topics (stage contracts, routes, gate evidence, compliance checklist) preserved
- workflow-html/SKILL.md had ~130 lines of inline CSS examples — replaced with 10-line token summary; full CSS lives in generate-html-review.py where it is enforced
- work-queue-workflow/SKILL.md had verbose Stage 5 multi-step narrative — condensed to 3 tight bullets preserving all behavioral requirements
- Operational Lessons sections condensed from multi-line bullets to single-line bullets

## Retirement Candidates
None — all 5 skills score ≥60/100 utility.
