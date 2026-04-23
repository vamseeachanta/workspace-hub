We are in `/mnt/local-analysis/worktrees/workspace-hub-issue-2348-nightly` on branch `issue-2348-nightly`.

Mission: execute the approved plan for GitHub issue #2348 tonight, focused on the still-open #1707 ToS / robots / unpause-governance implementation. Keep the work bounded and evidence-driven.

Issue: https://github.com/vamseeachanta/workspace-hub/issues/2348
Plan: `docs/plans/2026-04-19-issue-2348-scanner-tos-triage.md`
Local approval marker already exists and is committed: `.planning/plan-approved/2348.md`

Owned paths:
- `scripts/gtm/job-market-scanner.py`
- `docs/strategy/gtm/job-market-scan/`
- `tests/gtm/`
- `config/scheduled-tasks/schedule-tasks.yaml` only if all unpause criteria are genuinely satisfied tonight
- `.planning/plan-approved/2348.md`
- `.nightly-results/2026-04-20-issue-2348.md`

Read-only paths:
- issue/plan docs for #2348 and #1707
- `scripts/gtm/weekly-scan-refresh.sh`
- existing dashboard/readme/history artifacts under `docs/strategy/gtm/job-market-scan/`

Forbidden paths:
- `scripts/skills/`
- `docs/document-intelligence/`
- `tests/skills/`
- issue surfaces for #2206, #2207, #2209, #2320
- `digitalmodel/`

Required execution pattern:
1. Post a concise GitHub execution-start comment on #2348.
2. Reconfirm current live state from the plan before editing.
3. TDD first: create or tighten targeted tests for the required #1707 behavior before implementation.
4. Implement the approved plan only:
   - robots.txt respect in `safe_request()` with fail-closed behavior
   - dead-source removal per Q9
   - owner-signoff / override doc-driven behavior per the plan
   - README / operator doc updates required by the unpause checklist
5. Keep cron PAUSED unless you can prove every U1-U5 criterion is satisfied tonight. If any criterion is not fully satisfied, leave schedule unpaused and document the exact blocker.
6. Run targeted validation and then a brief adversarial self-review against the issue acceptance criteria.
7. Write `.nightly-results/2026-04-20-issue-2348.md` with:
   - summary of changes
   - commands run
   - tests/validation results
   - whether cron remained paused or was safely unpaused, with proof
   - residual risks / blockers
8. Commit if the owned-scope validation is green.
9. `git fetch origin --quiet && git rebase origin/main` before push.
10. Push the branch.
11. Post a GitHub progress comment summarizing landed work and evidence. Close only if the issue is fully satisfied; otherwise leave open with the exact remaining gap.

Execution rules:
- do not ask the user questions
- do not broaden to #2346 or other GTM work
- if you discover a necessary follow-up outside the approved scope, create or recommend a follow-up issue instead of silently absorbing it
- prefer precise, minimal changes over sweeping rewrites
