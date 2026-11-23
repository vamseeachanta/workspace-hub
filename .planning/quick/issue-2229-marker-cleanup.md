Governance cleanup:

- Local approval marker `.planning/plan-approved/2229.md` has become stale relative to the live issue state.
- The issue is currently in `status:plan-review` after fresh external adversarial reviews returned blocking findings.
- Removing the stale local marker so local state no longer implies approval that the live queue has already rolled back.

Relevant review artifacts:
- `scripts/review/results/2026-04-14-plan-2229-codex.md`
- `scripts/review/results/2026-04-14-plan-2229-gemini.md`
