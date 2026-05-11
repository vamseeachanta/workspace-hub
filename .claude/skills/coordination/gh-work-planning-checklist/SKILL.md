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
- After every material plan patch, refresh the synthesis artifact and scan the plan for stale review wording before posting: old verdicts, old round numbers, mutable runner outputs (for example `claude.md`), conditional language contradicted by newer acceptance criteria, and stale occurrence counts.
- If a provider is unavailable after a documented workaround/retry, save a concise Markdown stub with the raw failure excerpt and classify it as `UNAVAILABLE`; do not cite raw `.err` files or treat unavailable providers as approval signals.
- When preserving round-numbered review artifacts, verify the cited round is the highest-numbered non-empty artifact at posting time.
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

7b. Blocker revalidation after child/prep closeout
- When a blocked parent issue has child governance, input-readiness, or prep issues that just closed, do not equate child closure with parent unblocked status.
- Inspect the child closeout comments and linked artifacts to distinguish "checklist/input artifact exists" from "all required fields/evidence/approval values are completed."
- If fields/gates remain incomplete, keep the parent open with `status:blocked` and post a parent comment naming the cleared prerequisite plus remaining gates.
- For high-risk raw/private/vendor/client-source lanes, use an independent read-only provider review and explicitly prohibit edits, issue comments, and raw extraction in the prompt.
- See `references/blocker-revalidation-after-child-closeout.md` for the detailed checklist and comment template.

8. Approval gate
- Before stopping: save the plan, update planning index if used, ensure follow-up issues are created or called out, post final plan comment, add `status:plan-review`, remove stale conflicting labels.
- If context or tool-call budget is running low, prioritize transactional posting/label/commit verification over additional polish; do not leave the plan in an unposted draft state after review is already complete unless a blocker is explicit.
- Final plan comment should include deliverable, scope boundaries, likely files/tests, review synthesis, residual risk, future issues, and explicit approval request.
- Hard stop: do not implement while awaiting approval.
- On approve: move to `status:plan-approved` and hand off execution package.
- On revise/reject/hold: keep execution blocked and follow the canonical route.

## One-screen reminder

Issue -> Intake -> Intelligence -> Plan -> Review -> Plan Comment -> `status:plan-review` -> Wait for approval -> Execute only after approval.

Canonical authority: `gh-work-planning`.
