Governance cleanup:

- Removing stale `status:plan-approved` label because this issue has no local `.planning/plan-approved/2250.md` marker.
- The current cross-provider plan reviews record MAJOR findings from both Codex and Gemini, so retaining a live `status:plan-approved` signal is misleading.
- This cleanup only removes stale approval-state signaling; it does not change the issue's closed/open state by itself.

Relevant review artifacts:
- `scripts/review/results/2026-04-14-plan-2250-codex.md`
- `scripts/review/results/2026-04-14-plan-2250-gemini.md`
