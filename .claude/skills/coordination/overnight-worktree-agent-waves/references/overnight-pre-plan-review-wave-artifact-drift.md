# Archived Skill: `overnight-pre-plan-review-wave-artifact-drift`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/overnight-pre-plan-review-wave-artifact-drift`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/overnight-pre-plan-review-wave-artifact-drift`
Consolidation date: 2026-04-29

---

---
name: overnight-pre-plan-review-wave-artifact-drift
description: Run overnight planning-only waves for issues before status:plan-review, and reconcile cases where GitHub state advances but plan/review artifacts land in a sandbox or remote branch instead of the active local worktree.
version: 1.0.0
author: Hermes Agent
category: workspace-hub-learned
tags: [overnight, planning, github, status-plan-review, worktree, artifact-drift]
---

# Overnight pre-plan-review wave artifact drift

Use when:
- the goal is to move open issues from pre-`status:plan-review` into `status:plan-review`
- you want 4 parallel Claude planning workers overnight
- the main checkout is dirty or already carrying unrelated state
- you need planning only, not implementation

## Core workflow

1. Create a fresh planning worktree from `origin/main`.
2. Select up to 4 open issues that lack both `status:plan-review` and `status:plan-approved`.
3. Write one prompt per worker plus a master summary.
4. Restrict worker writes to planning artifacts only:
   - `docs/plans/YYYY-MM-DD-issue-NNN-*.md`
   - `scripts/review/results/*plan-NNN-*`
   - optional `.planning/quick/*NNN*`
5. Explicitly forbid `docs/plans/README.md`, source files, and tests in the worker prompt.
6. Launch Claude with:
   `PROMPT=$(< worker.md)`
   `claude -p --permission-mode acceptEdits --no-session-persistence --output-format text --max-budget-usd 20 "$PROMPT" </dev/null | tee logs/<worker>.log`
7. Each worker should:
   - inspect GH + local evidence
   - draft the canonical plan
   - run adversarial review
   - revise once if MAJOR
   - add `status:plan-review` only if approval-ready
   - otherwise post blocker comment and leave unlabeled

## Verification rule: check 3 surfaces

A worker can advance GitHub state even when artifacts do not appear in the orchestrator's active local worktree.

Always verify across these three surfaces:
1. Live GitHub state
   - issue labels
   - latest planning comments
2. Local active worktree state
   - canonical plan path under `docs/plans/`
   - expected review artifacts under `scripts/review/results/`
3. Remote branch / alternate-worktree provenance
   - `git ls-remote --heads origin <branch>`
   - `git show --stat <sha>`
   - `git show <sha>:path/to/file`

## How to classify outcomes

### Clean success
- GitHub label/comment correct
- local plan/review artifacts present where expected

### Artifact-placement drift
- GitHub `status:plan-review` is correct
- worker comments are present
- local active worktree is missing claimed artifacts
- remote branch commit or sandbox/alternate worktree contains the artifacts

Treat this as governance/artifact drift, not as worker failure.
Record it explicitly and reconcile before any downstream execution wave.

### Blocked plan
- no `status:plan-review`
- blocker comment posted
- MAJOR findings remain

## Operational lessons

- Fresh planning worktrees reduce collisions with a dirty primary checkout.
- For planning-only waves, not editing `docs/plans/README.md` is a good collision-avoidance rule.
- Worker success messages can overstate local artifact placement; trust live evidence plus git provenance, not the terminal summary alone.
- If a worker used a sandbox/in-repo alternate worktree, GitHub may already be correct while the orchestrator's external worktree stays unchanged.

## Morning handoff format

Report per issue:
- issue number
- GitHub status label verified or not
- local artifact presence verified or not
- remote-branch artifact presence verified or not
- disposition:
  - cleanly ready for approval
  - ready on GitHub but artifact reconciliation needed
  - blocked / needs rewrite
