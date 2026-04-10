---
name: gh-work-execution-checklist
description: Compact live-execution checklist companion for approved GitHub issue work. Use during active implementation as a fast operational route; gh-work-execution remains the canonical source of truth.
version: 1.0.0
author: Hermes Agent
category: software-development
license: MIT
related_skills:
  - gh-work-execution
  - github-issues
  - github-pr-workflow
tags: [execution, checklist, github, tdd, verification, review]
---

# GH Work Execution Checklist

Compact companion skill for live execution.
`gh-work-execution` is the canonical and authoritative route. Use this checklist to stay on-track during active work, not to replace the full route.

## Trigger notes

Use when:
- the issue is already planned and approved
- you need a fast execution checklist while working
- you want to keep GitHub updates, validation, and closeout disciplined

Do not use this instead of the canonical route when scope, delegation, policy, or closeout decisions are unclear.

## Live checklist

1. Entry gate
- Confirm the issue is approved for execution.
- Confirm repo/worktree/policy context is known.
- Confirm you know the intended validation path.
- Post a concise execution-start note if execution is proceeding.
- If approval, authz, environment, or validation path is missing: stop and route back per `gh-work-execution`.

2. Already-done check first
- Inspect the deliverable surface before changing code.
- Run the most relevant targeted validator/test.
- Check issue comments, linked PRs, and recent history if it may already be landed.
- Decide explicitly: `already done`, `not done`, or `uncertain`.
- If `already done`, post evidence and close from the verification-first path.

3. Central vs delegated decision
- Default to central unless ownership boundaries are crisp.
- Delegate only when owned paths, validators, GitHub authority, and integration ownership are explicit.
- Use hybrid only when recon/slices can be delegated safely but final integration stays central.
- If the decision changes execution ownership or reporting flow, post that change to GitHub.

4. TDD loop
- Write or update the failing targeted test first.
- Implement the smallest change that should pass.
- Run the narrowest relevant test loop.
- Refactor only after green.
- Repeat until acceptance is satisfied.

5. Targeted validation gate
- Run the specific tests/validators that prove the issue is done.
- Add broader validation only where risk or repo policy requires it.
- Capture exact evidence for GitHub and commit messaging.
- If validation is incomplete or ambiguous, do not advance.

6. Adversarial review gate
- Challenge the change like a skeptical reviewer.
- Check acceptance coverage, regressions, edge cases, and policy fit.
- Check whether new work should become a future issue instead of being absorbed.
- If non-trivial concerns remain, fix them and re-run validation.

7. Commit/push gate
- Confirm the diff matches approved scope.
- Confirm tests/validators used as evidence are still green.
- Commit with a message tied to the landed work.
- Push only after validation and review are complete.
- Post the landed summary and verification evidence to GitHub.

8. Closeout
- Close only when the issue is landed, or proven already satisfied/invalid with evidence.
- Link any future issues discovered during execution.
- Post concise final verification evidence.
- Leave the issue with a clear done-state, not an implied one.

## Operating note

When in doubt, stop using the checklist as a shortcut and return to `gh-work-execution` for the full decision framework, delegation rules, GitHub posting cadence, blocker handling, and closeout requirements.
