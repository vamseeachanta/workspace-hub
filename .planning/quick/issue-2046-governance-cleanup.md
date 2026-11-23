Governance cleanup:

- Removing stale `status:plan-approved` because this issue currently has no local `.planning/plan-approved/2046.md` marker.
- External cross-provider plan reviews now record MAJOR findings from both Codex and Gemini, so the plan is not currently approval-ready.
- Moving the live issue state back to `status:plan-review` so GitHub state matches the current review evidence.

Relevant review artifacts:
- `scripts/review/results/2026-04-14-plan-2046-codex.md`
- `scripts/review/results/2026-04-14-plan-2046-gemini.md`
