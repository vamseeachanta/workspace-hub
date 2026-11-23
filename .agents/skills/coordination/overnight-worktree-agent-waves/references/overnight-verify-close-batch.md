# Archived Skill: `overnight-verify-close-batch`

Original path: `/home/vamsee/.hermes/skills/software-development/overnight-verify-close-batch`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/software-development/overnight-verify-close-batch`
Consolidation date: 2026-04-29

---

---
name: overnight-verify-close-batch
description: Build overnight parallel batches that close stale-open GitHub issues by proving landed work already satisfies the issue, instead of wasting implementation lanes on redoing completed work.
version: 1.0.0
author: Hermes Agent
category: software-development
tags: [overnight, github, issue-triage, verify-close, worktrees, claude]
---

# Overnight Verify-Close Batch

Use this when an overnight batch should spend some lanes on proving open issues are already done, rather than re-implementing them.

## When to use
- repo has many open `status:plan-approved` issues
- some issues have comments claiming implementation landed or PRs/worktrees exist
- labels look execution-ready, but live state may be stale
- you want safe overnight progress with low git contention

## Core idea
A stale-open issue can be one of the best overnight targets if the remaining work is:
- verify landed commit(s)
- inspect deliverables
- run narrow validation
- post evidence-rich closeout comment
- close issue if satisfied

This is often better than launching a write-capable implementation lane against an issue whose code already exists on `origin/main`.

## Eligibility rules
Put an issue in verify-close mode when most of these are true:
1. the issue is still open
2. labels imply it is ready or active (`status:plan-approved`, similar)
3. issue comments mention implementation, a worktree branch, or a PR
4. a candidate implementation commit can be identified
5. that commit is already contained in `origin/main`
6. expected deliverable paths exist on disk now
7. remaining work is mostly proof + closeout, not feature building

## Exclusion rules
Do NOT use verify-close mode when:
- comments explicitly say the issue is not actually approval-ready despite stale labels
- required runtime/data/secrets are missing and you cannot prove satisfaction from the current machine
- the acceptance target still clearly requires fresh implementation
- the issue is umbrella/planning-only and cannot be closed from repo evidence alone

Important lesson:
- live comments and repo state outrank stale labels for overnight dispatch decisions

## Recommended triage sequence
1. `gh issue view <n>` and inspect recent comments
2. identify any mentioned PR, branch, or commit hash
3. `git fetch origin --quiet`
4. verify candidate commit is in `origin/main`:
   - `git branch -r --contains <commit>`
5. inspect expected artifact paths from the issue/plan
6. run the narrowest validator available
7. decide exactly one of:
   - `already done`
   - `not done`
   - `uncertain`

## Worktree pattern
Use a fresh read-mostly worktree from `origin/main` per verify-close issue.

Why:
- avoids dirty-main confusion
- gives a clean environment for deterministic inspection
- isolates any accidental edits from true implementation lanes

## Prompt shape for each lane
Each verify-close prompt should include:
- issue number and URL
- candidate landed commit hash if known
- expected artifact paths
- owned path for exactly one result artifact such as:
  - `.nightly-results/<date>-issue-<n>.md`
- explicit rule: do not broaden into implementation if not satisfied
- explicit rule: if satisfied, post closeout comment and close issue
- explicit rule: if not satisfied, leave open and post exact blocker

## Output artifact contract
Each lane writes one result file containing:
- verdict
- evidence checked
- commands run
- acceptance-criteria coverage
- exact reason for close or non-close

This artifact is the morning triage surface and a safer progress signal than stdout logs.

## GitHub closeout pattern
If verdict is `already done`, post a concise structured comment with:
- result: already satisfied / landed
- commit hash proving landing
- artifact paths checked
- validation command(s) or deterministic inspection proof
- note that the issue stayed open after landing and is now being closed from a verification-first path

If verdict is `not done` or `uncertain`, post:
- what was checked
- what acceptance target is still missing
- why no implementation was attempted in this lane

## Batch composition guidance
A strong overnight mixed batch can combine:
- 2-3 verify-close lanes for stale-open issues
- 1 implementation-repair lane for a live failing PR
- 1 true implementation lane for a bounded approved issue

This gives safe parallelism with low directory overlap and avoids wasting tokens on duplicate implementation.

## Pitfalls
- trusting labels over comments
- assuming a commit mention means the issue is satisfied without checking `origin/main`
- performing broad implementation after the verify-close check fails; stop and report instead
- using the dirty main checkout for verification
- skipping a result artifact and relying only on CLI logs

## Reusable insight from live use
In workspace-hub-style repos, multiple open `status:plan-approved` issues may already be satisfied by landed commits while still remaining open on GitHub. Overnight capacity is often best spent verifying and closing those, while reserving only one or two lanes for true implementation work.
