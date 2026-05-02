# Archived Skill: `large-parallel-planning-wave-environment-failure-handoff`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/large-parallel-planning-wave-environment-failure-handoff`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/large-parallel-planning-wave-environment-failure-handoff`
Consolidation date: 2026-04-29

---

---
name: large-parallel-planning-wave-environment-failure-handoff
description: Handle large pre-plan-review planning waves that succeed analytically but fail to persist artifacts due to quota exhaustion, sandbox write failures, or cancelled GitHub mutations.
version: 1.0.0
author: Hermes Agent
category: workspace-hub-learned
tags: [planning, overnight, parallel, github, handoff, environment-failure]
---

# Large Parallel Planning Wave Environment-Failure Handoff

Use when:
- running a large (4-10 lane) planning-only wave to move GitHub issues toward `status:plan-review`
- multiple workers finish with strong planning evidence, but local writes or GitHub mutations fail
- Claude quota exhaustion forces provider failover mid-wave
- you need to exit without losing which issues are substantively ready vs still incomplete

## Trigger pattern

Typical signals:
- Claude lanes exit with `You've hit your limit · resets 2pm (America/Chicago)`
- fallback Codex lanes hit sandbox/runtime failures like `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`
- safe-path writes fail (`apply_patch` / local file creation)
- GitHub issue comments / labels / branch creation are cancelled
- workers can still gather high-quality evidence and even converge on review verdicts, but nothing durable lands

## Core insight

A planning wave can succeed intellectually and still fail operationally.
Do not treat these as simple planning failures.
Classify each issue by **substantive readiness** instead of only by whether the plan file exists.

## Required classification buckets

For every affected issue, place it in exactly one bucket:

### 1. Ready in substance, not landed
Use when all or most of the following are true:
- the intended canonical plan path is known
- evidence gathering is complete enough to support a bounded plan
- review verdicts are effectively approval-ready (for example APPROVE/MINOR, or a rewritten plan that resolved prior blockers)
- the only thing missing is persistence: writing the plan/review artifacts and applying GitHub mutations

Next-session interpretation:
- do **not** restart from scratch
- materialize the plan and review artifacts in a healthy environment
- then apply `status:plan-review`

### 2. Rerun required
Use when any of the following are true:
- review state is incomplete or only partially trustworthy
- the issue still needs real cross-provider review to be honestly approval-ready
- major ambiguity remains in scope, decomposition, or file ownership
- the worker only gathered evidence and did not converge the plan content

Next-session interpretation:
- rerun planning in a healthy environment
- do not present the issue as ready for approval yet

## Required exit actions

1. Pause any continuation cron that would keep launching more broken lanes.
2. Write a handoff doc under `docs/handoffs/` summarizing:
   - wave objective
   - environment failure pattern
   - per-issue bucket assignment
   - intended canonical plan path for each blocked lane
   - whether `status:plan-review` was applied or not
   - whether a blocker comment landed or not
3. Record which issues already succeeded in earlier waves so they are not mixed into the failed-wave set.
4. If new follow-up issues were discovered during the wave, list them explicitly for the next queue partition.

## Recommended handoff structure

- session objective
- what worked (orchestration, evidence gathering, partial review convergence)
- what failed (writes, shell, GitHub mutations, quota)
- issues already in `status:plan-review` from earlier waves
- `ready in substance, not landed` bucket
- `rerun required` bucket
- recommended next move
- exact log/worktree paths for resume

## Provider-failover rule

When Claude quota is exhausted in a large planning wave:
- relaunch only the affected lanes with Codex or another provider in the same isolated worktrees
- do **not** restart the whole wave
- if the failover provider then also fails at the environment layer, stop broad escalation
- mark the lane as environment-blocked and place it into one of the two buckets above

## Stop condition

End the wave when either is true:
- enough issues have landed cleanly and remaining failures are clearly environmental, or
- the environment is no longer trustworthy for durable planning artifact creation

At that point, preserve truth in the handoff instead of pretending the queue advanced.

## Anti-patterns

- repeatedly relaunching the same broken lane under new providers without changing the environment
- calling an issue “pending review” when the plan content is actually ready but not persisted
- calling an issue “approval-ready” when review/artifact state is too incomplete to support that claim
- leaving a continuation cron active after you already know the environment is not healthy enough for unattended progress

## Minimal operator checklist on resume

1. read the handoff doc
2. pause any stale continuation cron still active
3. for `ready in substance, not landed` issues:
   - recreate canonical plan/review artifacts from logs or re-emit the saved draft content
   - apply GitHub comment + `status:plan-review`
4. for `rerun required` issues:
   - rerun planning from scratch in a healthy writable session
5. re-partition the remaining queue only after the above cleanup
