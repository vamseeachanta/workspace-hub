# Archived Skill: `closure-first-overnight-batch`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/closure-first-overnight-batch`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/closure-first-overnight-batch`
Consolidation date: 2026-04-29

---

---
name: closure-first-overnight-batch
description: Run a high-leverage overnight batch by clearing stale-open approved issues first, converting shared blockers into tracked issues, and reserving only one lane for true implementation.
version: 1.0.0
tags: [overnight, github, worktrees, backlog-reduction, blocker-conversion, workspace-hub]
---

# Closure-first overnight batch

Use this when a repo has many open `status:plan-approved` issues, but live state may be stale and only some lanes are truly ready for implementation.

## When to use
- Overnight batch with multiple Claude terminals/worktrees
- Backlog contains several `status:plan-approved` issues
- You suspect queue drift: some issues may already be implemented, others may really be blocked by shared CI/governance infrastructure
- You want maximum morning impact, not maximum overnight token burn

## Core idea
Do not spend the whole night implementing by default.
Instead, split the batch into three types of lanes:

1. verify-close lanes for stale-open issues
2. one bounded PR-repair / blocker-diagnosis lane
3. one true implementation lane

This often yields better morning outcomes than five implementation lanes, because it:
- closes stale-open issues quickly
- turns fuzzy branch failures into precise blocker issues
- preserves one lane for genuine implementation progress

## Recommended lane mix
For a 5-lane batch:
- T1 verify-close stale-open issue A
- T2 verify-close stale-open issue B
- T3 verify-close stale-open issue C
- T4 repair blocked PR / branch; if blocker is repo-wide, create a blocker issue and stop
- T5 implement one highest-confidence approved issue in an isolated worktree

## Verify-close lane checklist
Each verify-close lane should:
1. `git fetch origin --quiet`
2. confirm candidate implementation commit is ancestor of `origin/main`
3. confirm content parity for the main deliverable path(s), not just commit ancestry
4. inspect issue comments / review artifacts / acceptance criteria
5. map acceptance criteria to exact proof
6. write a local evidence report artifact
7. post a proof-rich GitHub closeout comment
8. close the issue if and only if the acceptance target is already satisfied

Important lesson:
- commit containment alone is not enough; also check content parity on `origin/main`
- comment first, then close; do not rely on `gh issue close --comment` in race-prone situations

## Blocker-conversion lane checklist
Use one lane for a live blocked PR/branch.

Goal:
- determine whether the branch is actually broken, or whether repo-wide CI/governance drift is the real blocker

Process:
1. inspect failing checks / local repro path
2. separate branch-specific failures from repo-wide infra failures
3. if the blocker is outside the branch's owned paths, stop implementation work
4. write a blocker report artifact
5. create a new GitHub issue for the shared blocker
6. comment on the originally blocked issue/PR linking the blocker issue

This keeps the queue truthful overnight and prevents random edits to the wrong branch.

## Implementation lane checklist
Reserve one lane for a real approved implementation issue.

Requirements:
- clean isolated worktree from `origin/main`
- local `.planning/plan-approved/<issue>.md` marker committed in that worktree before starting
- explicit owned/read-only/forbidden paths
- narrow TDD-first scope

If push is blocked by shared hook/governance problems after local validation:
- do not silently bypass unless explicit authorization exists
- treat that as evidence for the blocker-conversion / landing-blocker stream
- comment on the issue with exact blocker and next dependency

## What good morning output looks like
By morning, the batch should ideally produce:
- 2-3 stale-open issues closed with evidence
- 1 new blocker issue for any shared CI/hook/governance problem discovered
- 1 implementation branch advanced with real commits, or a precise blocker report

## Why this pattern works
A drifted queue often contains three kinds of work that look identical from labels alone:
- already-landed work
- blocked work
- truly executable work

This batch pattern separates them early and spends tokens accordingly.

## Pitfalls
- Do not trust `status:plan-approved` labels alone; do live eligibility checks.
- Do not assume a blocked PR needs branch edits; first test whether the real failure is repo-wide.
- Do not run all lanes as implementation lanes when file overlap or shared governance hooks make that unsafe.
- Do not close from commit ancestry alone; verify content parity and acceptance coverage.
