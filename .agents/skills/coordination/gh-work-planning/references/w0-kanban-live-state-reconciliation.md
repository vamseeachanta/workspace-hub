# W0 Kanban Live-State Reconciliation Pattern

Use after generating repo/domain Kanban boards or 5-hour swarm recommendations, before launching a new execution wave.

## Session signal

A generated board/recommendation packet mixed several states:
- `status:working` issues with landed commits still open
- `status:working` issues where the last worker found a no-code/dependency blocker
- a closed issue still appearing in a plan-review/live-drift queue

Launching directly from the board would have duplicated work and wasted provider quota.

## Required reconciliation checks

For each W0 candidate issue:
1. `gh issue view N --repo OWNER/REPO --json state,labels,comments,updatedAt,url,title`
2. Search canonical plans flexibly:
   - `find docs/plans -maxdepth 1 -type f -name '*issue-N-*'`
   - if filenames vary, search file content for the issue number too.
3. Check approval markers against the remote tree, not only the possibly-dirty checkout:
   - `git ls-tree -r --name-only origin/main -- .planning/plan-approved/N.md`
4. Check referenced worker branches/worktrees:
   - `git ls-remote --heads origin <branch>`
   - `test -e <worktree>` then `git status --short` if present.
5. For commits mentioned in comments, verify whether they landed:
   - `git merge-base --is-ancestor <sha> origin/main; echo $?`
6. For closed cross-repo issues, exclude them from active plan-review/execution lanes on the next board refresh.

## Classification

- **Closeout candidate**: issue is open/working, worker commit is already ancestor of `origin/main`, branch/worktree are gone. Next action is scoped verification + transactional issue closeout, not implementation.
- **Blocked/no-op candidate**: issue is open/working but comments report no-code/dependency blocker and no live worker branch remains. Next action is blocker conversion or plan revision, not relaunch.
- **Board drift only**: issue is closed or labels changed after board generation. Next action is board refresh/exclusion, not work launch.

## Output

Write a short durable report under `docs/reports/kanban/YYYY-MM-DD-w0-live-state-approval-audit.md` with:
- issue URL/title
- live state/labels
- plan/marker/branch/worktree/commit evidence
- classification
- recommended next action

Then link it from the Kanban board index so later swarms consume the reconciliation state.

## Post-reconciliation sweep and closeout hygiene

After writing board/reconciliation artifacts, finish with a transactional repository sweep before claiming the board is ready:

1. Re-read `git status --short --branch` and `git rev-parse HEAD origin/main` immediately before staging. Do not rely on an earlier clean-state check; concurrent Claude/Codex/Gemini workers may have pushed or written generated state while the board was being prepared.
2. If another worker commits/pushes during the sweep, pull/rebase or otherwise reconcile first, then make the smallest follow-up commit for remaining generated state. Report the concurrent commit separately instead of hiding it inside the board work.
3. Stage only the intended board/report/skill artifacts plus inspected generated state. Treat surprise root files or hook-generated dirt as evidence to inspect, not as automatically safe clutter.
4. Let pre-commit hooks run normally. If a generated skill/reference trips a critical scanner or denylist, fix the content and recommit; do not bypass the hook for library updates.
5. Push in the same window and verify:
   - `git rev-parse HEAD`
   - `git rev-parse origin/main`
   - `git rev-list --left-right --count origin/main...HEAD`
   - `git status --short`
6. Final board/exit status should name the pushed commit(s), state whether any external action was performed, and include clean/synced proof.

This prevents a planning board from becoming stale immediately after generation and matches the user's transactional closeout expectation for repo-sync and planning artifacts.
