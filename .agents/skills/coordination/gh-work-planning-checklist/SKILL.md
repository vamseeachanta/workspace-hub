---
name: gh-work-planning-checklist
description: Compact live-execution checklist companion for the canonical gh-work-planning route. Use for fast operational tracking during issue planning without replacing the full route.
version: 1.0.0
author: Hermes Agent
category: coordination
triggers:
  - When user says "gh work planning checklist"
  - When running the canonical gh-work-planning flow live and a compact checklist is needed
  - When you need a short issue-planning execution checklist without rewriting the full route
related_skills:
  - gh-work-planning
  - github-issues
  - overnight-parallel-agent-prompts
  - licensed-machine-prompt-orchestration
tags: [planning, github, checklist, coordination, approval-gate, delegation]
---

# GH Work Planning Checklist

Use this as the compact operational checklist during live execution.
`gh-work-planning` remains the canonical and authoritative source of truth.
If this checklist conflicts with the full route, follow `gh-work-planning`.

## Trigger notes

Use when:
- work starts from a GitHub issue
- you need Issue -> Plan -> Approval -> Execution discipline
- you want a short runbook while posting progress live

Do not use this as a substitute for the full planning route.

## Live checklist

1. Intake
- Read the full issue, acceptance criteria, references, and labels.
- Classify T1/T2/T3.
- Post planning-start comment before any implementation.
- Decision gate: continue, blocker, or future issue.

2. Resource intelligence
- Stay read-only.
- Check code, tests, docs, issue/PR history, standards or upstream constraints, and prior session context.
- Record proof: exact files, docs, issue/PR numbers, commits, commands.
- Identify implementation surface, gaps, risks, and artifact locations.
- Capture out-of-scope discoveries as future-issue candidates immediately.
- Confidence gate: High/Medium can proceed; Low means keep investigating or stop and post blocker.

3. Draft the plan
- Write the canonical plan artifact under `docs/plans/YYYY-MM-DD-issue-NNN-<slug>.md`.
- Include deliverable, file map, tests, acceptance criteria, risks, scope boundaries, and follow-up issues.
- Separate required now vs later work.
- Delegation gate: explicitly decide yes/no on Claude agent-team packaging.

4. Claude prompt-pack delegation check
- Delegate only if work splits cleanly into non-overlapping streams.
- Assign explicit owned paths, forbidden paths, dependencies, validation, and GitHub authority limits per stream.
- Enforce zero git contention: no shared files, branches, or worktrees across streams.
- If delegating, prepare stable prompt-pack structure:
  - `master-plan.md`
  - `stream-<id>.md`
  - `execution-readme.md`
- If boundaries are fuzzy, do not delegate yet.

5. Adversarial review
- Run independent plan review via Claude + Codex + Gemini.
- Compare verdicts, synthesize findings, revise plan, and re-review if changes are material.
- Review gate: no silent downgrade of major concerns.
- Mark residual risk and whether plan is ready for approval.

6. GitHub posting cadence
- Post meaningful cumulative updates at major planning steps:
  - after intake/classification
  - after resource intelligence
  - after draft-plan readiness if useful
  - after review synthesis
  - with final plan + label update
- Combine rapid sub-steps into one factual update instead of spamming.
- Post blockers immediately.

7. Future-issue capture
- Do not silently absorb adjacent work.
- Create or clearly stage future issues for out-of-scope work, follow-up optimizations, blocked dependencies, separate bugs, or institutional knowledge worth tracking.
- Link future issues back to the current issue and mention them in the plan.
- Decision gate at each major step: continue current issue, create future issue, stop for user decision, or stop for blocker.

8. Approval gate
- Before stopping: save the plan, update planning index if used, ensure follow-up issues are created or called out, post final plan comment, add `status:plan-review`, remove stale conflicting labels.
- Final plan comment should include deliverable, scope boundaries, likely files/tests, review synthesis, residual risk, future issues, and explicit approval request.
- Hard stop: do not implement while awaiting approval.
- On approve: move to `status:plan-approved` and hand off execution package.
- On revise/reject/hold: keep execution blocked and follow the canonical route.

## One-screen reminder

Issue -> Intake -> Intelligence -> Plan -> Review -> Plan Comment -> `status:plan-review` -> Wait for approval -> Execute only after approval.

Canonical authority: `gh-work-planning`.
