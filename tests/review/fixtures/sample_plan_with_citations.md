# Sample plan for attestation tests (fixture for #2405)

> Fixture consumed by `tests/review/test_attest_plan_claims.py`. Do not edit without updating test expectations.

## Resource Intelligence Summary

Prior cross-review work relates to #2208 (retrieval contract), #2206 (conformance), and #2405 itself. Also tracking #2403 for embedding decisions.

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/review/cross-review.sh` | orchestrator |
| Create | `scripts/review/attest-plan-claims.sh` | new attestation script |
| Modify | `tests/review/test_attest_plan_claims.py` | tests |
| Update | `pyproject.toml` | optional dep |
| Reference | `docs/plans/_template-issue-plan.md` | template |

Skill contract lives in `.claude/skills/coordination/issue-planning-mode/SKILL.md`.

## Non-backticked mentions (should NOT be extracted)

The file docs/plans/foo.md should not appear in extracted paths. Neither should plain scripts/review/cross-review.sh written without backticks.

## Partial-failure sentinel

High-number non-existent issue: #9999999 (fake placeholder to exercise gh-lookup-failed fallback).
