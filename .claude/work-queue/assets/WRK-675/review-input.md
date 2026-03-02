# WRK-675 Review Input

## Work Item
- ID: WRK-675
- Title: governance(review): align orchestrator flow & scripts
- Route: C (complex)
- Repo: workspace-hub
- Related: WRK-656, WRK-669, WRK-670, WRK-671, WRK-673

## Problem

WRK-669/670/671 showed each orchestrator running the canonical gates but with inconsistent
script usage. The central issue: cross-review outputs varied because orchestrators called
per-agent submit scripts directly instead of routing through `cross-review.sh all`. WRK-675
inventories these deviations and codifies the canonical flow.

## Implementation

### Artifacts Created

| Artifact | Path | Gate |
|----------|------|------|
| Draft plan HTML review | `.claude/work-queue/assets/WRK-675/plan-html-review-draft.md` | Plan gate |
| Final plan HTML review | `.claude/work-queue/assets/WRK-675/plan-html-review-final.md` | Plan gate |
| Spec file | `specs/wrk/WRK-675/plan.md` | Route C spec |
| Canonical flow doc | `assets/WRK-656/orchestrator-flow.md` | Deliverable 1 |
| Updated comparison HTML | `assets/WRK-656/wrk-656-orchestrator-comparison.html` | Deliverable 2 |
| Variation test results | `.claude/work-queue/assets/WRK-675/variation-test-results.md` | TDD gate |
| Legal scan | `.claude/work-queue/assets/WRK-675/legal-scan.md` | Legal gate |

### Key Finding

`cross-review.sh all` is the canonical cross-review entry point for ALL orchestrators.
It internally dispatches to `submit-to-claude.sh` (watchdog/PGID), `submit-to-codex.sh`
(timeout/INVALID_OUTPUT), and `submit-to-gemini.sh`, with 2-of-3 fallback consensus.
Direct per-agent calls = drift.

### Deliverable 1 — orchestrator-flow.md

New file at `assets/WRK-656/orchestrator-flow.md` (repo root, agent-neutral path). Contains:
- 9-stage canonical flow (Capture → RI → Triage → Plan → Claim → Execute → Review → Close → Archive)
- 6-script canonical suite + 3 internal submit scripts with their special handling
- Inventory matrix (orchestrator × script × usage)
- Deviation table (4 entries)
- Follow-on improvement candidates

### Deliverable 2 — comparison HTML updates

`assets/WRK-656/wrk-656-orchestrator-comparison.html` updated with:
- Status pill: "Canonical flow defined (WRK-675)" + link to orchestrator-flow.md
- Scripts & validators: canonical note added; submit-to-claude.sh row marked DRIFT
- Script consistency checklist: submit-to-claude.sh row updated with DRIFT/OK badges
- NEW "Canonical orchestrator flow" panel (9-stage table)
- NEW "Script alignment" panel (per-agent vs canonical)
- NEW "Deviation notes" panel (4-row table with resolution actions)

### Cross-Review Plan Gate
- Claude: NO_OUTPUT (watchdog timeout during plan review)
- Codex: REQUEST_CHANGES — P1 (stage count), P2 (paths, scripts, dependencies) — all addressed
- Gemini: REQUEST_CHANGES — P1 (WRK-656 path clarification), P2 (agent-neutral path) — all addressed

### Plan revisions made post cross-review
- Stage count corrected to 9 (added Review between Execute and Close)
- orchestrator-flow.md placed in `assets/WRK-656/` (root) not `.claude/`
- Script suite table expanded to include all 3 internal submit scripts
- WRK-673 and WRK-1000 explicitly marked informational/non-blocking

## Acceptance Criteria Status

- [x] Inventory table showing flow/scripts each orchestrator actually ran — in orchestrator-flow.md
- [x] `assets/WRK-656/orchestrator-flow.md` describes canonical flow plus script list
- [x] Comparison HTML references new canonical flow and notes ongoing improvement targets
- [x] Follow-on actions recorded (WRK-673, WRK-1000, log normalisation candidate)

## Files Changed

| File | Change |
|------|--------|
| `assets/WRK-656/orchestrator-flow.md` | NEW — canonical flow doc |
| `assets/WRK-656/wrk-656-orchestrator-comparison.html` | EDIT — 3 new sections |
| `specs/wrk/WRK-675/plan.md` | NEW |
| `.claude/work-queue/working/WRK-675.md` | UPDATE frontmatter |
| `.claude/work-queue/assets/WRK-675/*` | NEW gate artifact files |
