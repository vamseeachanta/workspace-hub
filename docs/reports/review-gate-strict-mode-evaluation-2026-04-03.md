# Review Gate Strict Mode Evaluation

Issue: #1711
Date: 2026-04-03

## Summary
Implemented two improvements to the pre-push review gate:
- hook latency measurement written to `logs/hooks/review-gate-latency.jsonl`
- path-based low-risk classification supplement for docs-only / low-risk changes

Also documented bypass policy in:
- `docs/standards/REVIEW_GATE_BYPASS_POLICY.md`

## Latency Measurements
Measured on this machine using `scripts/enforcement/require-review-on-push.sh` against a temporary git repo.

| Commit batch | Real time |
|--------------|-----------|
| 10 feature commits | 0.230s |
| 50 feature commits | 0.819s |

Interpretation:
- interactive latency is acceptable for normal developer pushes
- strict mode is operationally feasible for interactive pushes on this machine
- 50-commit batches remain under 1 second in the measured local scenario

## Strict Mode Evaluation
Recommendation:
- keep warning mode available as the default for general local iteration
- enable `REVIEW_GATE_STRICT=1` for high-risk pushes, release work, and branches intended for merge/shipping

Reasoning:
- bypass remains technically possible in local clones, so strict mode is a workflow control, not an absolute security boundary
- the new latency measurements show strict blocking is cheap enough for interactive use
- warning mode is still useful for low-friction local iteration when a user intentionally wants softer enforcement

## Path-Based Classification Supplement
Added low-risk path handling so feature-labeled commits that only touch documentation or other low-risk paths do not trigger unnecessary review failures.

Current low-risk paths include:
- `docs/*`
- `*.md`
- `*.rst`
- `LICENSE`
- `README*`
- `CHANGELOG*`
- `config/ai-tools/*`
- `config/user-profile.yaml`

## Bypass Policy
`SKIP_REVIEW_GATE=1` is allowed only for documented emergency or infrastructure-exception cases.
See:
- `docs/standards/REVIEW_GATE_BYPASS_POLICY.md`

## Validation
Commands run:
- `bash scripts/enforcement/tests/test_require_review_on_push.sh`
- measured 10-commit and 50-commit temporary-repo batches with `time bash scripts/enforcement/require-review-on-push.sh ...`
