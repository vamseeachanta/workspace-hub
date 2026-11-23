Planning update:

- Dependency mapping completed in `docs/reports/2026-04-20-refactor-knowledge-release-readiness-dependency-map.md`
- Canonical plan drafted at `docs/plans/2026-04-20-issue-2399-next-model-release-readiness-contract.md`
- Adversarial plan review attempted with Claude/Hermes + Codex + Gemini

Current review status: NOT approval-ready
- Claude/Hermes: MAJOR
- Codex: MAJOR
- Gemini: MAJOR

Convergent blockers:
1. standing contract + reusable eval battery + follow-up issue generation are not yet all concretely bound in the current real-file draft
2. technical coverage is still too abstract at the artifact level (adapter files, truncation/context safety, session/export/log schemas)
3. highest-risk gap follow-up issue generation is not yet satisfied strongly enough

Review artifacts:
- `scripts/review/results/2026-04-20-plan-2399-claude.md`
- `scripts/review/results/2026-04-20-plan-2399-codex.md`
- `scripts/review/results/2026-04-20-plan-2399-gemini.md`

Holding this issue out of `status:plan-review` until the plan is revised against these blockers.
