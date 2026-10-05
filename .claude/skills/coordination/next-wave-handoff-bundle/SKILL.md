---
name: next-wave-handoff-bundle
description: Build a docs-only execution handoff bundle after a completed implementation wave — follow-up issue drafts, scoped authorization note, deploy checklist, operator note, copy/paste command bundle, and incremental commit hygiene.
version: 1.0.0
author: Hermes Agent
category: coordination
tags: [handoff, planning, operations, github, deployment, docs-only]
---

# Next-Wave Handoff Bundle

## Zero-loss handoff and closeout

Use the existing repository handoff convention and verified claim backend/root. A handoff transfers context, not permission. Separate established authorization from proposed next work; preserve human merge review. An authorization note documents verified permission and cannot grant it. Preparing a bundle does not authorize issues, external messages, push, merge or deletion.

Record goal/approved scope; branch/worktree/base revision; owned and forbidden paths; deliverables/acceptance evidence; exact checks/outcomes; decisions, risks and dependencies; unresolved owners/dates; next actions/escalation triggers; source revisions/as-of time; and claims held/released. Distinguish complete, unverified and blocked work. Include precise resume steps and the first freshness check.

Before merge review or closeout inspect dirty files, stashes, worktrees and temporary outputs without altering unrelated work. Account for every unique artifact: verified durable destination/revision/integrity, intentionally retained local work, or unresolved disposition. Unverified retention blocks cleanup of that artifact. Cleanup requires its own applicable authorization and cannot remove another lane's work. Local save, commit, backup, receipt and publication are distinct verified states. Release only this session's claims after checking ownership; unavailable coordination blocks affected shared work.

For Spaces, read [Space context and transfer](../../business/product/stakeholder-comms/references/space-context.md).

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
Read the available governing artifacts within the task's permitted context; record missing or excluded sources rather than expanding retrieval scope:
- current plan
- review/adversarial review
- handback or implementation summary
- design/spec if referenced

Within the permitted context, also inspect:
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
Create only the docs-only coordination artifacts needed by the requested handoff and permitted task scope. The following are options:

1. `...follow-up-issues.md`
   - only the issue drafts justified by actual review findings
2. `...stage2-authorization.md`
   - evidence of existing authorization for the next task range, or an explicitly pending authorization request
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

Select the relevant artifacts; omit unsupported or unnecessary packets and scripts.

### 4. Keep scope boundaries explicit in every artifact
Each artifact should restate:
- which tasks/stage are already complete
- which next tasks have verified authorization and which remain proposals; use identifiers only when supplied
- that already-completed tasks are not being reopened
- that production actions belong on the real target checkout/host, not the feature worktree
- no hook bypass / no push unless explicitly approved

### 5. Sequence recommendations by risk reduction
When a real governance/enforcement bug was found during implementation:
1. preserve the docs handoff bundle
2. recommend promotion/cherry-pick of the narrow enforcement fix before more plan-gated implementation work
3. then draft follow-up issues from remaining review findings; create them only within established action authorization
4. then identify the deploy-topology Stage 2 readiness and authorization gates before execution

This ordering matters: fix the workflow reliability issue before asking operators to rely on it again.

### 6. Convert issue drafts into executable packets
When the user needs executable issue packets and their preparation is in scope, supplement drafted issue bodies with:
- a packet doc with exact labels, title, body, optional follow-up comment
- a shell script that writes temp body files and prints exact `gh issue create` commands

Default to explicit `--repo`, explicit labels, and `--body-file`.

### 7. Build a single operator command bundle last
When a command bundle is requested or necessary for the authorized handoff, use a script that prints the relevant:
- promotion/cherry-pick commands
- issue creation commands
- Stage 2 doctor / dry-run commands

Keep commands tied to their separate action gates; a printed execution sequence does not authorize its execution.

### 8. Commit within the established task scope
Commit only when the user's task or verified standing repository authority permits it and applicable review/check gates pass. A request for recommendations or a read-only evaluation does not itself authorize commits. If commits are authorized, group related docs proportionately; possible units are:
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
- applicable scope, authorization and repository gates passed
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

If `git push` reports a remote ref-lock/race error such as `cannot lock ref ... is at <new> but expected <old>`, do not assume the handoff failed. When remote reads are within task scope, run `git fetch origin <branch>` and compare `git rev-parse HEAD` with `git rev-parse origin/<branch>`. In concurrent/auto-sync environments the remote may already contain the just-created commit despite the non-zero push result; if hashes match, treat the push as effectively complete and avoid duplicate commits or force-pushes.

A docs-only handoff commit can still trigger repo CI/docs workflows. If CI is red for failures outside the completed stream's scope, do not reopen the completed issue by default. Instead:
- record the relevant scoped pass/fail evidence in the handoff and/or issue comment
- draft a follow-up issue for the remaining failure family; open it only within established action authorization
- explicitly state that the completed stream remains complete only if its acceptance gate stayed green

Example: after a lint-restoration stream, a handoff commit triggered CI where `Lint`, `Type Check`, and `Security Scan` passed but Python test-matrix jobs failed. Correct closeout was to preserve the lint handoff, retain its accepted status, and prepare a plan-gated follow-up for the Python test-matrix failures; issue creation required its own applicable authorization.

Report the evidence plainly.

## Output checklist
A solid handoff should usually include:
- summary of current branch state in <=8 lines if requested
- written follow-up issue drafts
- next-stage authorization evidence or explicitly pending decision, when relevant
- written deploy-readiness checklist
- written operator note on promoting a fix
- git status checked
- observed push/no-push state, or unverified state if evidence is unavailable
- optionally, exact gh commands and a single operator bundle

## Pitfalls
- Do not reopen already-completed tasks just because review found future hardening work.
- Do not mistake a worktree smoke test for production validation.
- Do not bury the real high-value recommendation (e.g. promote a narrow enforcement fix first).
- Convert issue drafts into `gh`-ready packets when executable packets are requested or needed within task scope.
- When commits are authorized and useful, preserve the handoff in a narrow commit; otherwise leave the reviewable artifacts and report their exact state. Handoff cleanliness does not expand task permission.

## Minimal verification loop
Within the permitted task context, check the following before finishing; report excluded or unavailable checks:
1. `git status --short --branch`
2. `git log --oneline -N`
3. verify all promised docs exist
4. verify whether anything remains uncommitted
5. report observed push state and its evidence; mark it unverified if the task excludes the necessary checks

## Why this is reusable
This pattern works whenever a completed implementation wave needs a safe operational handoff for the next wave, especially in plan-gated repos where docs, issue packets, and deployment sequencing must be preserved without reopening feature code.