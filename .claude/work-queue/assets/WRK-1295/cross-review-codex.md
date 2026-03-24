# Cross-Review: WRK-1295 — Codex

## Verdict: REVISE

## Summary
The 3-phase shape is reasonable, but the package is not yet executable as written because
budget approval does not match the stated run cost, and the workspace_spec Phase A dependency
is underspecified for a high-priority run.

## P1 Findings (blocking)
1. AC5 requires cost within approved budget, but plan says $9 budget vs $114 expected spend.
   Direct fail against acceptance before execution starts.
2. Phase A for workspace_spec is described only as "currently 0 records, blocker" but does not
   define which script, who owns it, how success is verified, or fallback if corpus size differs.

## P2 Findings (recommended)
1. No throughput/concurrency assumptions for shard counts — affects duration and real cost
2. Validation "spot-check 20 docs" lacks sampling strategy, rubric, or failure handling
3. Should run canary batch (50-100 docs) before full launch to confirm prompt fit on these corpora
4. Success metric "≥90% classified" needs explicit denominator rules (total vs attempted vs non-duplicate)

## Scope Change: No
