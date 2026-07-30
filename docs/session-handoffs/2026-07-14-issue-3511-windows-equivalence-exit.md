# #3511 Windows machine-equivalence implementation handoff

Date: 2026-07-14  
Machine: ace-win-2  
Branch: `chore/3511-windows-equivalence-plan`  
Pull request: [#3540](https://github.com/vamseeachanta/workspace-hub/pull/3540)  
Issue: [#3511](https://github.com/vamseeachanta/workspace-hub/issues/3511)

## Current state

- Implementation, adversarial review fixes, governance evidence, and CI remediation are committed and pushed.
- PR #3540 is open and mergeable but `UNSTABLE` because `strict-scan / authority` receives an empty `AUTH_ENVELOPE`. The repository-level blocker is recorded on [#3522](https://github.com/vamseeachanta/workspace-hub/issues/3522#issuecomment-4971559657).
- Every branch-controlled hosted check is green: Client-PII, GitGuardian, Run Tests, Code Quality, Governance, Scheduler Mutation Surface Guard, review/plan evidence, model/skill/stage guards, and hosted Claude review.
- Local focused verification: 78 Python tests, fingerprint 9/9, isolated sentinel 4/4, 65-task schedule validation, Bash/PowerShell parsing, scheduler mutation inventory/HTML, and legal diff scan all pass.
- Full collector suite has four Windows-only baseline failures that reproduce on fresh `origin/main`; follow-on [#3539](https://github.com/vamseeachanta/workspace-hub/issues/3539) owns module splitting and hermetic test repair.

## Live machine evidence

Read-only Task Scheduler audit on ace-win-2:

| Task | Live state |
|---|---|
| `EcosystemReconcile` | absent |
| `EquivalenceSentinel` | absent |
| `SessionCuration` | absent |
| `EqualityReport` | Ready; last run 2026-07-13 04:30; result 1; next run 2026-07-20 04:30 |

The canonical catalog declares `EcosystemReconcile` daily at 05:15 and `EquivalenceSentinel` every six hours at minute 17. Declaration is now tested; live materialization intentionally waits for merge.

The current 2026-07-14 matrix still reports ace-win-2 gaps for scheduler, session curation, memory freshness, and publish health. It was not republished from an unmerged branch.

## Exact continuation

1. Resolve/provision the Legal Rule Authority `AUTH_ENVELOPE` under #3522 and rerun the failed job on PR #3540.
2. Merge PR #3540 only after the PR is stable under repository policy.
3. From a clean/current canonical ace-win-2 checkout, preview then install:

   ```bash
   bash scripts/windows/schedule-equivalence-tasks.sh --machine ace-win-2 --what-if
   bash scripts/windows/schedule-equivalence-tasks.sh
   ```

4. Run `EquivalenceSentinel` once and verify: nonempty exact-schema fingerprint, `machine_id=ace-win-2`, exact `ace-win-2.json` ref entry with no carriage-return suffix, publish-health rc 0, and Task Scheduler last result 0.
5. Run the equality report with matrix refresh only after valid publish evidence lands; verify ace-win-2 publish health becomes green in the regenerated HTML.
6. Post live evidence to #3506 and #3511. Close #3506 only when its live condition passes; close #3511 only after its completeness gate passes.

## Preserved state

- No live Task Scheduler mutation was performed.
- No production `equivalence-state` publish was performed from the feature worktree.
- PR branch and review artifacts are pushed; the isolated worktree is clean.
- The current matrix HTML remains truthful pre-rollout evidence rather than a speculative green report.

