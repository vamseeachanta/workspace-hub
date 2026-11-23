# Follow-up lane feed7 — #2510 plan-patch / loop-collapse (planning only)

Run on ace-linux-1 before the 2026-04-29 09:45 CDT stop target.

## Purpose
Consume the completed C3 hardener result and do exactly one bounded, non-destructive planning pass for issue #2510. The C3 result classified #2510 as MAJOR due to: duplicated r13 review-summary rows, ambiguous per-layer round-trip semantics, ambiguous layer-key encoding, failure-path report ordering, planning artifact paths mixed into implementation scope, and sustained-MAJOR loop governance risk.

## Hard constraints
- Planning/review only. Do **not** implement code.
- Do **not** mutate GitHub: no issue comments, labels, PRs, closes, merges, force-pushes, or `gh` writes.
- Do **not** create `.planning/plan-approved/*` markers.
- Do **not** launch implementation.
- Allowed writes only:
  - `docs/plans/2026-04-26-issue-2510-python-layout-cad-automation-demo.md`
  - `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-patch-2510-feed7.md`
  - optional review note under `scripts/review/results/2026-04-29-plan-2510-feed7-loop-collapse.md`

## Required work
1. Read the #2510 plan and the C3 hardener result section for #2510.
2. Apply only targeted plan-text edits to address C3 findings A1/A2/A4/A5/A6 and the sustained-MAJOR governance note:
   - Collapse duplicated r13 rows to one canonical per-provider set.
   - Pin per-layer round-trip semantics deterministically, including which named layers require exact equality and any bounded range caps.
   - Pin one layer-key JSON encoding and make the test expectation match it.
   - Reorder/clarify pseudocode so failed import/round-trip blocks report generation.
   - Move review-artifact paths out of implementation `Files to Change` into a planning-artifacts section.
   - Add a clear r14/parking decision rule consistent with the existing sustained-MAJOR governance note; do not self-approve.
3. Re-read edited sections and write a concise result file with: edits made, line references, verification observations, constraints honored, and next human-gated steps.

## Stop conditions
- If the plan has changed materially since C3 and the findings no longer apply, do not patch blindly. Write a result summary explaining what changed and what remains.
- If any required edit would require implementation evidence or GitHub mutation, stop and record the blocker.
