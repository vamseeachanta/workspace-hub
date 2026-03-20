# WRK-1005 Plan: Cross-Provider Orchestrator Assessment
date: 2026-03-05
wrk_id: WRK-1005
route: C
complexity: medium
orchestrator: claude

## Objective

Consolidate evidence from WRK-1002 (Claude), WRK-1003 (Codex), and WRK-1004 (Gemini)
into a single structured assessment report. No new implementation — purely analytical.

## Inputs (all confirmed present)

| Artifact | Status |
|----------|--------|
| WRK-1002/variation-test-results.md | ✅ |
| WRK-1003/variation-test-results.md | ✅ |
| WRK-1004/variation-test-results.md | ✅ |
| WRK-1004/cross-provider-comparison.md | ✅ |
| Gate evidence summaries (all 3) | ✅ |
| Stage evidence yamls (all 3) | ✅ |
| Claude session JSONL | ✅ session_20260304.jsonl |
| Codex session log | ✅ session_20260304.log |
| Gemini native store | ✅ (no named session log in orchestrator/gemini/) |
| parse-session-logs.sh | ✅ already run |

## Assessment Dimensions

1. **Lifecycle Completeness** — all 20 stages completed per stage-evidence.yaml?
2. **Gate Compliance** — gates PASS on first run (vs. remediation needed)?
3. **TDD Faithfulness** — execute.yaml: tests before implementation (red → green)?
4. **User-Review Integration** — plan-html-review-final.md with `decision: passed`?
5. **Tool / Skill Invocation** — `/work` invoked directly vs. script fallback?
6. **Session Log Review** — parse-session-logs.sh table (presence, events, duration)?
7. **Spec Divergence** — calculate_circle implementation matches contract?

## Execution Steps

1. Synthesize scorecard from gate summaries + stage evidence
   - Evidence: `.claude/work-queue/assets/WRK-100{2,3,4}/evidence/gate-evidence-summary.md`
2. Extract TDD evidence from execute.yaml per provider
   - Evidence: `.claude/work-queue/assets/WRK-100{2,3,4}/evidence/execute.yaml`
3. Build session log table from parse-session-logs.sh output
   - Command: `bash scripts/work-queue/parse-session-logs.sh WRK-1002 WRK-1003 WRK-1004`
   - Output: `.claude/work-queue/assets/WRK-1004/session-log-review.md` (already captured)
4. Spec Divergence check
   - Contract: `tests/unit/test_circle.py` (5 tests, canonical keys: `area`, `circumference`)
   - Implementations: `src/geometry/circle.py` (shared across all providers — same file)
   - Pass criteria: all 5 tests green under each provider's test run (confirmed in variation-test-results.md)
5. Document strengths + gaps per provider
6. Write recommended routing rules (Route A/B/C + cross-review role)
7. Capture action items as new WRK entries if needed
8. Agent cross-review of assessment draft
   - Codex: `bash scripts/review/submit-to-codex.sh --file assets/WRK-1005/orchestrator-assessment.md`
   - Gemini: `cat assessment.md | gemini -p "review" -y`
   - Record verdict in `evidence/cross-review-package.md`; block on unresolved MAJORs
9. Produce `assets/WRK-1005/orchestrator-assessment.md`
10. Produce `assets/WRK-1005/orchestrator-assessment.html` (via generate-html-review.py)
11. Run `verify-gate-evidence.py WRK-1005` — all gates must pass

## Variation Tests (analytical evidence)

- Run `parse-session-logs.sh WRK-1002 WRK-1003 WRK-1004` — already done
- Run `verify-gate-evidence.py WRK-1005 --phase claim` after claim
- Final gate run: `verify-gate-evidence.py WRK-1005` before close

## No TDD Required

This item has no code implementation. Variation tests are script-based analytical
checks. The TDD gate will be satisfied by `variation-test-results.md` documenting
the analytical evidence-gathering scripts run.

## Output Files

All paths are under `.claude/work-queue/assets/WRK-1005/`.

| File | Purpose |
|------|---------|
| `orchestrator-assessment.md` | Structured scorecard + findings |
| `orchestrator-assessment.html` | Styled HTML for user review |
| `evidence/stage-evidence.yaml` | 20-stage lifecycle evidence |
| `evidence/variation-test-results.md` | Script run evidence (parse-session-logs.sh + verify) |
| `evidence/execute.yaml` | Analytical test evidence (3-5 script checks — satisfies Integrated test gate) |
| `evidence/future-work.yaml` | Follow-up WRK entries |
| `evidence/resource-intelligence-update.yaml` | Post-work resource additions |
| `evidence/claim.yaml` | Claim gate evidence |
| `evidence/activation.yaml` | Activation gate evidence |
| `evidence/user-review-browser-open.yaml` | Browser-open stage records |
| `evidence/user-review-close.yaml` | Close user-review record |
| `evidence/cross-review-package.md` | Codex + Gemini implementation review verdicts |
| `plan-html-review-draft.html` | Plan draft HTML (Stage 5) |
| `plan-html-review-final.html` | Plan final HTML (Stage 7) |

## Workstation

dev-primary (plan + execution)
