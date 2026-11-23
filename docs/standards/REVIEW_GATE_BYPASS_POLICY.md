# Review Gate Bypass Policy

Issue: #1711
Status: Active

## Purpose
Document when `SKIP_REVIEW_GATE=1` is acceptable and when strict review enforcement should remain in place.

## Default policy
- Default interactive behavior is strict: `REVIEW_GATE_STRICT` defaults to `1`, and pre-push review enforcement stays enabled unless a documented bypass is used.
- Commit-bound evidence is selected by `REVIEW_GATE_EVIDENCE_MODE`. The default is `warn` until 2026-10-26, when the one default assignment line in the gate is expected to change to `strict` after second-provider review.
- In `warn` evidence mode, legacy modification-time and subject-keyword evidence can still permit a push, but the gate prints `WOULD-REJECT` for each feature commit that lacks commit-bound evidence and marks the legacy evidence as deprecated.
- In `strict` evidence mode, each feature-class commit in the checked range needs a review result file under `scripts/review/results/` with `Reviewed-Commit: <full-commit-id>` or coverage by `Reviewed-Range: <oldest-full-commit-id>..<reviewed-full-commit-id>`.
- A push with no evidence of any kind is blocked in both evidence modes under the current strict default. An invalid evidence line is reported with its file and line number, does not count, and the push is judged as if that line were absent.
- Treat review bypass as an exception path, not a normal warning-only workflow.

## Acceptable bypass cases
`SKIP_REVIEW_GATE=1` is acceptable only when one of the following is true:
- emergency operational fix where restoring service is more urgent than full review sequencing
- provider outage, quota exhaustion, or infrastructure failure prevents collecting review evidence
- purely local or temporary branch push used to preserve work-in-progress
- documented clerical/doc-only maintenance where review evidence is being collected separately

## Not acceptable
Do not bypass for:
- security-sensitive changes
- production release pushes
- schema/data-migration changes
- broad multi-file behavioral changes without compensating review evidence

## Required follow-up after bypass
When bypass is used:
- capture the reason in the commit message, issue comment, or handoff note
- collect adversarial review as soon as systems are available
- do not merge or ship to production solely on the bypassed push

## Audit trail
- bypasses are logged to `logs/hooks/review-gate-bypass.jsonl`
- latency measurements are logged to `logs/hooks/review-gate-latency.jsonl`
- evidence-mode migration warnings are printed by the gate output and are not a bypass record
