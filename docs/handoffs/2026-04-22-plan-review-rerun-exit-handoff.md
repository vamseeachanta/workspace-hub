# Exit handoff — plan review rerun wave (#2289, #2444, #2443)

Date
- 2026-04-22

Repo / branch
- Repo: `/mnt/local-analysis/workspace-hub`
- Current branch: `integration/runbook-main-compatible`
- HEAD at handoff time: `2b279a8013cd434fb3542a4597fc2ed9e48371d7`

High-level outcome
- Opened PR for the docs-only runbook branch:
  - PR #2466
  - https://github.com/vamseeachanta/workspace-hub/pull/2466
- Prepared rerun-review dispatch pack and prompts.
- Ran multiple external adversarial rerun-review waves.
- Patched #2289 repeatedly through v9 and #2444 through v7.
- #2443 remains at v5 and still has unresolved MAJOR findings.

Current plan-file dirty state
- Modified and not yet committed:
  - `docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md`
  - `docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md`
  - `docs/plans/README.md`
- No other targeted handoff files are currently dirty.

Artifacts created during this session

Runbook / dispatch docs
- `docs/plans/2026-04-22-plan-hardening-safe-landing-sequence.md`
- `docs/plans/2026-04-22-rerun-review-dispatch-pack-2443-2444-2289.md`
- `docs/plans/overnight-prompts/2026-04-22-rerun-review-wave/review-2443-codex-prompt.md`
- `docs/plans/overnight-prompts/2026-04-22-rerun-review-wave/review-2443-gemini-prompt.md`
- `docs/plans/overnight-prompts/2026-04-22-rerun-review-wave/review-2444-codex-prompt.md`
- `docs/plans/overnight-prompts/2026-04-22-rerun-review-wave/review-2444-gemini-prompt.md`
- `docs/plans/overnight-prompts/2026-04-22-rerun-review-wave/review-2289-codex-prompt.md`
- `docs/plans/overnight-prompts/2026-04-22-rerun-review-wave/review-2289-gemini-prompt.md`

Latest review artifacts on disk

#2289
- `scripts/review/results/2026-04-22-plan-2289-codex-v8.md`
- `scripts/review/results/2026-04-22-plan-2289-gemini-v8.md`
- `scripts/review/results/2026-04-22-plan-2289-codex-v9.md`
- `scripts/review/results/2026-04-22-plan-2289-gemini-v9.md`
- `scripts/review/results/2026-04-22-plan-2289-codex-v10.md`
- `scripts/review/results/2026-04-22-plan-2289-gemini-v10.md`

#2444
- `scripts/review/results/2026-04-22-plan-2444-codex-r4.md`
- `scripts/review/results/2026-04-22-plan-2444-gemini-r4.md`
- `scripts/review/results/2026-04-22-plan-2444-codex-r5.md`
- `scripts/review/results/2026-04-22-plan-2444-gemini-r5.md`
- `scripts/review/results/2026-04-22-plan-2444-codex-r6.md`
- `scripts/review/results/2026-04-22-plan-2444-gemini-r6.md`
- `scripts/review/results/2026-04-22-plan-2444-codex-r7.md`
- `scripts/review/results/2026-04-22-plan-2444-gemini-r7.md`

#2443
- `scripts/review/results/2026-04-22-plan-2443-codex-r4.md`
- `scripts/review/results/2026-04-22-plan-2443-gemini-r4.md`
- `scripts/review/results/2026-04-22-plan-2443-codex-r5.md`
- `scripts/review/results/2026-04-22-plan-2443-gemini-r5.md`
- `scripts/review/results/2026-04-22-plan-2443-codex-r6.md`
- `scripts/review/results/2026-04-22-plan-2443-gemini-r6.md`

Latest known review state

#2289
- Current local draft: v9
- Latest rerun verdicts:
  - Codex v10: MAJOR
  - Gemini v10: APPROVE
- Remaining blocker theme:
  - Codex still wants a more formal normative definition for:
    - what a "revision set" is
    - what exact fields/evidence bind approval to that set
    - what exactly qualifies `log_only_remediated_later`
    - related audit/TDD coverage
- Closest to approval among the three.

#2444
- Current local draft: effectively v7 (patched after r7 findings), not rerun after latest local patch
- Latest rerun verdicts before last patch:
  - Codex r7: MAJOR
  - Gemini r7: MAJOR
- Latest local patch addressed:
  - stale governance-state wording
  - review-artifact lineage / next-rerun target
  - historical `status:plan-approved` snapshot language
- Needs fresh rerun after current uncommitted v7 patch.

#2443
- Current local draft: v5
- Latest rerun verdicts:
  - Codex r6: MAJOR
  - Gemini r6: MAJOR
- Still blocked on:
  - policy disagreement around `python3` vs `uv run`
  - floor-rule / MD025 semantics
  - verifier and markdownlint command/action details
  - stale review-history / acceptance-artifact references
- This is the furthest from approval.

Recommended next move after resume
1. Decide whether to continue on branch `integration/runbook-main-compatible` or switch back to `main` before committing local plan patches.
2. Commit current local patches for:
   - `docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md`
   - `docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md`
   - `docs/plans/README.md`
3. Rerun only #2289 and #2444.
4. Reassess whether #2443 should be patched again or deferred.

Suggested exact next commands
```bash
cd /mnt/local-analysis/workspace-hub

git status --short -- \
  docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md \
  docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md \
  docs/plans/README.md

# inspect diffs

git diff -- \
  docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md \
  docs/plans/2026-04-21-issue-2444-aceengineer-admin-ci.md \
  docs/plans/README.md
```

Then either commit them together or split by issue.

Notes
- Temporary worktrees created for landing flow were cleaned up.
- PR #2466 remains open for the docs-only runbook branch.
- The current branch is not the original `main`; confirm desired landing strategy before committing the remaining plan patches.
