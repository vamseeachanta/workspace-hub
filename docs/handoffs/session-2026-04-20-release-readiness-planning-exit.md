# Session exit handoff — release-readiness planning split and narrowing

Date/time: 2026-04-20 17:49 CDT
Repo: `vamseeachanta/workspace-hub`

## What was completed

This session focused on the release-readiness planning track that started from #2399.

Main outcomes:
1. Confirmed #2399 is too broad to clear adversarial plan review as a single issue.
2. Split #2399 into narrower child issues.
3. Drafted and iteratively tightened #2408 as the first approval candidate.
4. Confirmed #2408 also needed a further boundary split: strict canonical-doc contract vs provider-entrypoint normalization.
5. Created the follow-up normalization issue #2421.

## GitHub issues created in this session chain

### Parent umbrella
- #2399 — `feat(ai-orchestration): define next-model-release readiness contract for repo ecosystem`
  - Link: https://github.com/vamseeachanta/workspace-hub/issues/2399
  - Current state: still too broad for approval; should remain a steering umbrella only.

### Child issues created from #2399 decomposition
- #2408 — `feat(release-readiness): workspace-hub-only model-release readiness contract and upgrade playbook`
  - Link: https://github.com/vamseeachanta/workspace-hub/issues/2408
  - Best current candidate for the first approval-ready plan, but not there yet.
- #2409 — `feat(release-readiness): fixture-backed golden-task corpus for model-release comparisons`
  - Link: https://github.com/vamseeachanta/workspace-hub/issues/2409
- #2410 — `feat(release-readiness): smoke-battery schema and runner contract (no runner implementation)`
  - Link: https://github.com/vamseeachanta/workspace-hub/issues/2410
- #2411 — `feat(release-readiness): tier-1 provider entrypoint and parity surface inventory`
  - Link: https://github.com/vamseeachanta/workspace-hub/issues/2411
- #2412 — `feat(release-readiness): deterministic follow-up issue creation and dedup policy`
  - Link: https://github.com/vamseeachanta/workspace-hub/issues/2412

### Follow-up boundary issue created after #2408 review convergence
- #2421 — `chore(control-plane): normalize workspace-hub provider entrypoint surfaces`
  - Link: https://github.com/vamseeachanta/workspace-hub/issues/2421
  - Purpose: isolate provider-entrypoint normalization from the narrower #2408 canonical-doc issue.

## Planning artifacts created/updated

### #2399
- Plan: `docs/plans/2026-04-20-issue-2399-next-model-release-readiness-contract.md`
- Review artifacts attempted/updated under:
  - `scripts/review/results/2026-04-20-plan-2399-claude.md`
  - `scripts/review/results/2026-04-20-plan-2399-codex.md`
  - `scripts/review/results/2026-04-20-plan-2399-gemini.md`
- Conclusion: keep as umbrella only; do not try to push it through a single approval gate.

### #2408
- Plan: `docs/plans/2026-04-20-issue-2408-workspace-hub-model-release-readiness-contract-and-upgrade-playbook.md`
- Indexed in: `docs/plans/README.md`
- Review raw artifacts created during the latest waves:
  - `.planning/quick/review-2408-codex.out`
  - `.planning/quick/review-2408-gemini.out`
  - `.planning/quick/review-2408-codex-r2.out`
  - `.planning/quick/review-2408-gemini-r2.out`
  - `.planning/quick/review-2408-codex-r3.out`
  - `.planning/quick/review-2408-gemini-r3.out`
  - `.planning/quick/review-2408-codex-r4.out`
  - `.planning/quick/review-2408-gemini-r4.out`
  - `.planning/quick/review-2408-codex-r5.out`
  - `.planning/quick/review-2408-gemini-r5.out`
- Key GitHub status comments:
  - https://github.com/vamseeachanta/workspace-hub/issues/2408#issuecomment-4283944043
  - https://github.com/vamseeachanta/workspace-hub/issues/2408#issuecomment-4284131848
  - https://github.com/vamseeachanta/workspace-hub/issues/2408#issuecomment-4284410769
  - https://github.com/vamseeachanta/workspace-hub/issues/2408#issuecomment-4284420162
  - https://github.com/vamseeachanta/workspace-hub/issues/2408#issuecomment-4284424127
- Current recommendation for #2408:
  - keep it strictly canonical-doc scoped
  - only canonical anchors should change in this issue
  - provider-entrypoint normalization must stay in #2421
  - do not request approval yet

## Current recommended issue ordering

Recommended work order remains:
1. #2408 — workspace-hub-only contract/playbook
2. #2409 — fixture-backed golden-task corpus
3. #2411 — tier-1 provider/parity surface inventory
4. #2410 — smoke-battery schema + runner contract
5. #2412 — follow-up issue creation / dedup policy
6. #2421 — provider-entrypoint normalization

## Main conclusions from this session

1. #2399 should not be forced through review as a monolith.
2. #2408 is the right first child issue, but it only becomes approval-ready if it stays narrow.
3. The right boundary is now explicit:
   - #2408 = strict canonical-doc readiness contract/playbook
   - #2421 = provider-entrypoint normalization
4. Repeated review friction on #2408 came from mixing those two concerns.
5. Future effort should avoid further scope rewrites on #2408 and instead focus on a clean review rerun when tooling is stable.

## Best next move

Primary recommendation:
1. Review/confirm the split between #2408 and #2421.
2. When ready, run a clean cross-provider review pass for #2408 only.
3. After #2408 clears, move to #2409 and #2411.

If immediate work continues later, the best next issue to actively plan is:
- #2421 if the goal is to unblock discoverability normalization explicitly, or
- #2409 if the goal is to build the reusable evidence base next.

## Working tree on exit

Working tree is dirty and intentionally not cleaned in this session.

Notable modified/untracked files at exit include:
- `docs/plans/2026-04-20-issue-2408-workspace-hub-model-release-readiness-contract-and-upgrade-playbook.md`
- `docs/plans/README.md`
- `.planning/quick/issue-2408-codex-r5-integration-comment.md`
- `.planning/quick/issue-2408-gemini-minor-integration-comment.md`
- `.planning/quick/issue-2408-strict-canonical-doc-status-comment.md`
- `.planning/quick/review-2408-codex-r5.out`
- `.planning/quick/review-2408-gemini-r5.out`
- plus unrelated pre-existing modified/untracked files shown by `git status --short`

There are also suspicious untracked entries from the broader session environment (for example literal names like `**Complexity:**`, `**Date:**`, `**Issue:**`, `**Review`, `**Source`, `**Status:**`, `Compatibility`, `This`) that should be investigated separately before any cleanup/commit activity.

## Exit readiness

This thread is documented.
The decomposition decision is now explicit in repo artifacts and GitHub issues.
The cleanest continuation is to either:
- pick up with #2421 planning, or
- run a clean review rerun for #2408 once the provider-review tooling path is stable.
