# Archived Skill: `next-wave-handoff-bundle`

Original path: `/home/vamsee/.hermes/skills/coordination/next-wave-handoff-bundle`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/next-wave-handoff-bundle`
Consolidation date: 2026-04-29

---

---
name: next-wave-handoff-bundle
description: Build a docs-only execution handoff bundle after a completed implementation wave — follow-up issue drafts, scoped authorization note, deploy checklist, operator note, copy/paste command bundle, and incremental commit hygiene.
version: 1.0.0
author: Hermes Agent
category: coordination
tags: [handoff, planning, operations, github, deployment, docs-only]
---

# Next-Wave Handoff Bundle

Use when a feature/workstream has completed one stage and the user wants execution artifacts for the next wave, not more generic advice.

Typical trigger phrases:
- "produce execution artifacts for the next wave"
- "continue this stream/worktree"
- "draft follow-up issues / authorization note / deploy checklist"
- "operator handoff"
- "prepare notes; document and prepare to exit"
- "handover this info to parallel Hermes terminal"
- "no push, no bypass, avoid code churn"

## Goal
Convert review findings and current branch state into a self-contained docs-first handoff bundle that another operator can execute safely.

## When this skill fits
Use this when:
1. A branch/worktree already contains completed implementation work.
2. The user wants concrete operational artifacts rather than more coding.
3. There are explicit constraints like no push, no hook bypass, and no reopening already-completed tasks.
4. You need to preserve execution context in-repo under `docs/plans/` or similar coordination paths.

## Core pattern

### 1. Read the governing artifacts first
Always read:
- current plan
- review/adversarial review
- handback or implementation summary
- design/spec if referenced

Also inspect:
- `git status --short --branch`
- recent relevant commits (`git log --oneline -N`)
- remote/upstream state if user wants explicit confirmation that no push happened

### 2. Anchor the handoff to verified facts
Before writing anything, extract and keep visible:
- what stage is complete
- what must NOT be redone
- what was actually validated vs only smoke-tested
- any known blockers already fixed
- any pending production-topology validation

Important: distinguish "feature-worktree smoke test" from real deploy-topology validation.

### 3. Prefer docs/plans artifacts over code changes
For this pattern, create docs-only coordination artifacts first. Typical bundle:

1. `...follow-up-issues.md`
   - 3+ GitHub-ready issue drafts from review findings
2. `...stage2-authorization.md`
   - scoped authorization for only the next task range
3. `...deploy-readiness-checklist.md`
   - concrete operator gate for the real target topology
4. `...enforcement-fix-note.md` or similar operator note
   - recommendation on whether a discovered fix should be promoted repo-wide
5. `...operator-runbook.md`
   - concise ordered next steps with stop conditions
6. `...gh-issue-packets.md`
   - copy/paste-ready titles, labels, bodies, optional comments
7. `...gh-create-commands.sh`
   - exact `gh issue create` commands using temp body files
8. `...enforcement-promotion-procedure.md`
   - exact cherry-pick/promotion procedure for a high-value fix
9. `...operator-command-bundle.sh`
   - one copy/paste bundle combining promotion, issue creation, and Stage-2 validation

Not every engagement needs all 9, but this is the full bundle pattern.

### 4. Keep scope boundaries explicit in every artifact
Each artifact should restate:
- which tasks/stage are already complete
- which task numbers are authorized next
- that already-completed tasks are not being reopened
- that production actions belong on the real target checkout/host, not the feature worktree
- no hook bypass / no push unless explicitly approved

### 5. Sequence recommendations by risk reduction
When a real governance/enforcement bug was found during implementation:
1. preserve the docs handoff bundle
2. recommend promotion/cherry-pick of the narrow enforcement fix before more plan-gated implementation work
3. then create follow-up issues from remaining review findings
4. then move to deploy-topology Stage 2 execution

This ordering matters: fix the workflow reliability issue before asking operators to rely on it again.

### 6. Convert issue drafts into executable packets
After drafting issue bodies, make them operator-usable by also creating:
- a packet doc with exact labels, title, body, optional follow-up comment
- a shell script that writes temp body files and prints exact `gh issue create` commands

Default to explicit `--repo`, explicit labels, and `--body-file`.

### 7. Build a single operator command bundle last
Once the docs are stable, create a single shell script that prints:
- promotion/cherry-pick commands
- issue creation commands
- Stage 2 doctor / dry-run commands

This becomes the safest final handoff artifact because it compresses all earlier docs into an execution sequence.

### 8. Commit docs incrementally as low-risk handoff units
If the user asks to continue with recommendations, a good conservative progression is:
1. commit the main handoff bundle
2. commit issue packets doc
3. commit gh-create command script
4. commit promotion-procedure doc
5. commit final operator-command bundle

Use docs-only commit messages such as:
- `docs(plans): ecosystem-sync next-wave handoff bundle`
- `docs(plans): add ecosystem-sync issue creation packets`
- `docs(plans): add ecosystem-sync gh issue create commands`
- `docs(plans): add enforcement fix promotion procedure`

After each commit, verify:
- plan gate passed
- auto-push did not occur unexpectedly
- branch status is clean or only contains the next expected artifact
- the intended handoff file is actually tracked in the expected commit (`git log --oneline -- <file>` and `git show --stat -- <file>`), especially if hooks/tooling return confusing output such as `nothing to commit` after a commit attempt

If a commit command returns non-zero or says `nothing to commit` after you just added a handoff file, do not assume failure. Immediately check:
```bash
git status --short --branch
git ls-files <handoff-file> --stage
git log --oneline -- <handoff-file> -3
git show --stat --oneline -- <handoff-file> | head -80
```
Some workspace automation/hooks may have already staged/committed the file or cleaned unrelated state; verify by file-specific git history before retrying or rewriting.

### 9. Explicitly verify push/no-push state and post-push CI
Do not merely assert whether a push happened. Check using git/remote evidence, for example:
- `git branch -vv`
- `git ls-remote --heads origin <branch>`
- `git rev-parse HEAD` and `git rev-parse origin/main` after `git fetch origin`
- post-commit output indicating no upstream configured / no auto-push

If the user chooses the exit path of "commit/push, document, and prepare to exit":
1. commit the handoff artifact as a narrow docs-only commit
2. push it
3. verify local `HEAD` equals the pushed remote ref
4. inspect the CI run triggered by the handoff commit
5. separate scoped-success evidence from unrelated CI failures

If `git push` reports a remote ref-lock/race error such as `cannot lock ref ... is at <new> but expected <old>`, do not assume the handoff failed. Immediately run `git fetch origin <branch>` and compare `git rev-parse HEAD` with `git rev-parse origin/<branch>`. In concurrent/auto-sync environments the remote may already contain the just-created commit despite the non-zero push result; if hashes match, treat the push as effectively complete and avoid duplicate commits or force-pushes.

A docs-only handoff commit can still trigger repo CI/docs workflows. If CI is red for failures outside the completed stream's scope, do not reopen the completed issue by default. Instead:
- record the relevant scoped pass/fail evidence in the handoff and/or issue comment
- open or draft a new follow-up issue for the remaining failure family
- explicitly state that the completed stream remains complete only if its acceptance gate stayed green

Example: after a lint-restoration stream, a handoff commit triggered CI where `Lint`, `Type Check`, and `Security Scan` passed but Python test-matrix jobs failed. Correct closeout was to preserve the lint handoff, keep the lint issue closed, and create a new plan-gated follow-up issue for the Python test-matrix failures.

Report the evidence plainly.

## Output checklist
A solid handoff should usually include:
- summary of current branch state in <=8 lines if requested
- written follow-up issue drafts
- written next-stage authorization note
- written deploy-readiness checklist
- written operator note on promoting a fix
- git status checked
- explicit statement that no push happened
- optionally, exact gh commands and a single operator bundle

## Pitfalls
- Do not reopen already-completed tasks just because review found future hardening work.
- Do not mistake a worktree smoke test for production validation.
- Do not bury the real high-value recommendation (e.g. promote a narrow enforcement fix first).
- Do not leave issue drafts as prose only; convert them into `gh`-ready packets when possible.
- Do not stop after creating docs if a simple docs-only commit would materially improve handoff cleanliness.

## Minimal verification loop
Before finishing:
1. `git status --short --branch`
2. `git log --oneline -N`
3. verify all promised docs exist
4. verify whether anything remains uncommitted
5. explicitly state whether a push occurred

## Why this is reusable
This pattern works whenever a completed implementation wave needs a safe operational handoff for the next wave, especially in plan-gated repos where docs, issue packets, and deployment sequencing must be preserved without reopening feature code.