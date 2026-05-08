# Tier-1 approval-state audit pattern

Use this reference when a multi-repo portfolio has many open issues labeled `status:plan-approved` and the user asks whether work can be launched.

## Purpose
A live GitHub approval label is not enough to launch workers. Verify all approval evidence surfaces before treating an issue as execution-ready.

## Evidence surfaces
For each scoped repo and approved issue, collect:
1. Live GitHub issue state/labels from `gh issue list --label status:plan-approved`.
2. No conflicting `status:plan-review` label.
3. Canonical plan file under `docs/plans/`, matched by issue number.
4. Approval marker under `.planning/plan-approved/<issue>.md`.
5. Whether the issue is already `status:working`.
6. Local repo branch and `git status --short` count to identify dirty-clone risk.

## Reusable collection sketch
```bash
for r in workspace-hub digitalmodel assetutilities worldenergydata assethold aceengineer-website; do
  gh issue list --repo "vamseeachanta/$r" \
    --state open \
    --label 'status:plan-approved' \
    --limit 1000 \
    --json number,title,url,labels,updatedAt \
    > "/tmp/${r}_plan_approved_live.json"
done
```

Then run a filesystem pass in each local clone to match issue numbers against:
- `docs/plans/*issue-<N>-*.md`
- `docs/plans/*<N>*.md` as legacy fallback
- `.planning/plan-approved/<N>.md`

## Classification
- **Executable candidate:** live approved, plan file exists, approval marker exists, no conflict, not `status:working`, and a clean issue-specific worktree can be assigned.
- **Governance drift:** live approved but missing plan file and/or approval marker.
- **Label conflict:** both `status:plan-approved` and `status:plan-review`; audit evidence before changing labels.
- **Implementation-state audit needed:** approved and `status:working`; inspect PRs, branches, planned files on main, comments, and CI before launching more work.
- **Dirty clone risk:** local repo has uncommitted/untracked state; do not launch workers in that clone directly.

## Report expectations
Write a repo-tracked report under `docs/reports/YYYY-MM-DD-tier1-approval-state-audit.md` with:
- repo-level matrix: live approved, fully evidenced, missing plan, missing marker, conflicts, working, branch/worktree state
- examples of missing plan/marker drift
- clean execution-candidate pool
- already-working pool
- multiagent launch gates and WIP cap

If a Kanban/portfolio report exists, update its action item to point at the completed audit and summarize counts.

## Guardrail
Do not launch multiagent execution from a label-only approval pool. Require plan + marker + no conflict + non-working + clean isolated worktree.

## Session-learned pitfalls
- **Separate broad approval pool from the requested wave.** A live audit may find many fully-evidenced executable issues, but if the user asked for a specific wave (for example repo-structure normalization across tier-1 repos), classify and recommend within that wave separately from the global candidate pool.
- **Governance drift is not executable.** Treat live `status:plan-approved` issues missing local plan files or `.planning/plan-approved/<issue>.md` markers as reconciliation work, not implementation work.
- **Verify durable report landing before calling the audit complete.** After writing `docs/reports/YYYY-MM-DD-tier1-approval-state-audit.md`, run `git status --short`, `git diff --check`, and confirm whether the report is tracked/committed/synced. Concurrent automation may commit the report while the session is still active, or may introduce unrelated dirty skill/session files; classify those separately and do not stage unrelated churn.
- **Do not leak auth output.** `gh auth status` can print masked token lines; keep raw logs out of durable reports and summarize auth success without copying credential-looking strings.