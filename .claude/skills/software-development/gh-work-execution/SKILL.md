---
name: gh-work-execution
description: Canonical GitHub issue execution route after plan approval — strengthened resource intelligence, TDD-first implementation, targeted validation, adversarial review, delegation controls for Claude agent teams, GitHub progress posting, future-issue capture, and commit/push with closeout discipline.
version: 1.4.0
author: Hermes Agent
category: software-development
license: MIT
related_skills:
  - github-issues
  - github-pr-workflow
tags: [execution, github, issue-workflow, tdd, review, verification]
---

# GH Work Execution

This is the canonical execution route for approved GitHub issue work.

Use it only after planning is complete and the issue is approved.

## Route summary

Canonical path:
Issue -> Plan -> User approves -> TDD implementation -> adversarial review -> commit/push -> comment/close issue

## GitHub posting rule

As execution progresses, post meaningful GitHub updates at each major step.
Do not leave the issue silent until closeout.

Minimum posting cadence during execution:
- execution start / scope confirmation
- noteworthy findings from strengthened resource intelligence or pre-checks
- if the issue is already done / invalid, post evidence before close
- if new future issues are created, post the linkage immediately
- after implementation + validation, post the landed change summary
- before close, post verification evidence

Keep updates concise and cumulative. Prefer fewer structured updates over noisy chatter.

## Future-issue capture rule

During execution, if you discover additional work that should not be silently absorbed into the current issue, capture it as a future GitHub issue.
Create it now when the split is clear, or mark it as a candidate when the orchestrator must decide timing or batching.

## Claude agent-team prompt packaging rule

When execution is best handled by multiple agents, multiple terminals, or licensed/external machines, use Claude to package the work into a self-contained prompt pack for agent team(s).
Use this when:
- work splits cleanly into non-overlapping streams
- separate agents need explicit write boundaries
- execution is overnight or unattended
- a machine without Hermes context must execute the work

Prompt packs should be:
- self-contained
- explicit about scope boundaries
- explicit about owned, read-only, and forbidden paths
- explicit about tests, validation, and GitHub check-in expectations
- explicit about GitHub authority limits
- explicit about commit/push or comment-only behavior
- explicit about future-issue capture expectations

Preferred supporting skills for this packaging:
- `overnight-parallel-agent-prompts`
- `licensed-machine-prompt-orchestration`

## Central vs delegated execution matrix

Choose the execution mode only after the entry gate and already-done pre-check are complete.
Do not delegate just because the issue is large; delegate only when ownership, validation, and GitHub reporting are all operationally clear.

| Situation | Mode | Rule |
| --- | --- | --- |
| single narrow fix, shared files, short feedback loop | central | keep execution in the main session |
| uncertain implementation surface or active design decisions | central | finish recon and decision-making centrally first |
| issue may already be satisfied and only needs verification/closure | central | keep the verification-first closure path in the main session and post evidence directly |
| multiple independent files/areas with clear acceptance slices | delegated | split into non-overlapping agent-owned streams |
| overnight/unattended work with explicit validation steps | delegated | package prompts so each stream can complete safely without live supervision |
| shared files, migration choreography, or likely merge contention | central | do not delegate concurrent writes |
| wide but mostly read-only recon feeding one final implementation | hybrid | delegate recon, keep final code integration central |
| approval/authz ambiguity, unclear write access, or missing repo/runtime prerequisites | central | stop delegation and resolve authorization/readiness before any worker starts |

Default to central execution when ownership boundaries are not crisp.

Operational checkpoint before execution:
1. Confirm the issue is approved and in execution scope
2. Finish the already-done pre-check
3. Choose exactly one mode: `central`, `delegated`, or `hybrid`
4. Post the mode decision to GitHub when it changes who will execute or how check-ins will happen
5. Only then start coding or prompt packaging

Use this decision flow:
- Choose `central` when the next best step is verification, recon, design resolution, or a tight single-threaded fix
- Choose `delegated` only when each stream has explicit owned paths, explicit validators, explicit GitHub reporting ownership, and no likely write overlap
- Choose `hybrid` only when delegated work is read-heavy or sliceable, but final integration/testing must stay central
- If you cannot prove one of those paths safely, stop and continue centrally or return for user/orchestrator decision

Required evidence for a delegated decision:
- exact issue(s) or sub-slices assigned
- owned/read-only/forbidden paths per stream
- validator/test command per stream
- orchestrator vs worker GitHub authority split
- merge/integration point and final central verification owner

If that evidence cannot be stated compactly and unambiguously, do not delegate.

## Delegated issue batch formation rules

When forming a delegated batch:
- batch only issues/subtasks that can be proven non-overlapping in write surface
- group by shared validator/test command only when that reduces risk rather than hiding scope
- keep each batch small enough that one prompt can state exact paths, commands, and closeout expectations
- isolate any migration, rename, or shared fixture work into a single owner
- if two streams would touch the same file, same generated artifact, or same lock/state surface, keep them central or serialize them

Batch package must state:
- issue numbers included in that batch
- exact goal of the batch
- owned paths for writes
- read-only paths allowed for context
- forbidden paths that must not change
- validation commands that define done

## Delegated prompt path contract

Every delegated prompt must include a path contract with these fields:
- `Owned paths:` the only files/directories the delegated team may modify
- `Read-only paths:` files/directories they may inspect for context but not edit
- `Forbidden paths:` files/directories they must not modify under any circumstance without returning control

Rules:
- owned paths must be explicit and minimal
- anything not listed as owned is read-only by default unless marked forbidden
- shared config, lockfiles, generated outputs, release metadata, and issue-tracking artifacts should be forbidden unless one batch is explicitly assigned ownership
- if delegated execution discovers a required change outside owned paths, stop, report it, and convert it to a future issue or orchestrator decision

## GitHub authority split

Default authority split during execution:
- orchestrator owns issue start notes, scope changes, blocker posts, future-issue creation/linking, final landed summary, and issue close
- delegated teams own execution evidence inside their assigned stream packet and should return checkpoints to the orchestrator unless the prompt explicitly authorizes direct GitHub posting
- if direct delegated posting is authorized, limit it to assigned issue progress updates and require the orchestrator to post the final integrated closeout

Do not let multiple delegated teams post overlapping status narratives on the same issue without an orchestrator merge point.

## Decision checkpoint rule

At the end of each major execution step, explicitly choose one:
- continue current issue
- create future issue
- stop for user decision
- stop for blocker

Do not carry ambiguity across steps.

Create a future issue when the discovered work is:
- outside the approved plan or acceptance criteria
- a separate bug, hardening task, cleanup, migration, or risk remediation
- blocked by another dependency or decision
- important enough that it should be tracked rather than left in a comment

When creating a future issue:
1. use a precise title and scope
2. describe why it was split from the current issue
3. link back to the current issue
4. mention the new issue number in the current issue comments and final closeout note

When a delegated team surfaces future work, return it in a compact handoff block:
- `Future issue candidate:` <proposed title>
- `Why split:` <scope/risk/dependency reason>
- `Evidence:` <file/test/behavior proving it>
- `Suggested owner/path:` <who should handle it or what area it belongs to>
- `Blocks current issue?:` yes/no

The orchestrator decides whether to create the GitHub issue immediately or queue it for the next batch.

## Blocker protocol

If execution is blocked, post a GitHub update immediately with:
- blocker summary
- impact on scope, delivery, or verification readiness
- missing dependency/decision/input
- whether a future issue was created
- whether execution is paused or rerouted

If the blocker is substantial and not resolvable inside current scope, create a future issue or dependency-tracking issue instead of letting the current issue absorb it silently.

## Entry condition

Only start execution when the issue is already labeled `status:plan-approved`.
If the issue is still unplanned or only in `status:plan-review`, route back to `gh-work-planning` first.

Treat execution entry as a hard gate, not a soft preference.
Before any code change, branch creation, or delegation package, confirm all of the following:
1. approval/authz: the issue has explicit plan approval and you are authorized to execute in this repo/worktree/environment
2. scope: the approved plan and acceptance target are identifiable enough to verify against
3. workspace readiness: the intended repo/worktree, branch context, and required policy files are known
4. validation readiness: you know the primary test/validation path or know that closure will rely on deterministic inspection evidence
5. GitHub readiness: you can post the required execution/check-in/closure updates, or the orchestrator for doing so is explicitly defined

Entry decisions:
- if approval is missing, stop and route back to planning/approval
- if authorization or execution environment is not safe/available, stop and post a blocker or hand back to the orchestrator
- if validation cannot yet be identified, stay in central recon until a verification path exists
- if the issue appears already satisfied, do not begin implementation; follow the already-done pre-check to a verification-first closeout decision

GitHub check-in at entry:
- when execution is allowed to proceed, post a concise start note with scope boundary, execution mode if already known, and immediate validation intent
- when execution cannot proceed, post the stop reason and next route (`planning`, `blocker`, or `orchestrator decision`)

### Local plan-marker gate in worktrees

In workspace-hub-style repos, a GitHub `status:plan-approved` label may still be insufficient for implementation if local hooks enforce `.planning/plan-approved/` markers.

Before launching implementation in a fresh worktree, verify all of the following in that same worktree:
- `.planning/plan-approved/<issue>.md` exists locally
- the marker text uses neutral/operator approval wording (not `Worker session`, `auto-approved`, or `self-approved`)
- the marker is committed in that worktree before write-capable Claude execution begins

Safe sequence for approved issue execution in a worktree:
1. create the worktree from `main`
2. write `.planning/plan-approved/<issue>.md` inside the worktree
3. commit the marker locally in that worktree
4. only then launch Claude/Codex for implementation

Why this matters:
- the plan-approval hook evaluates the local worktree state, not just GitHub labels
- a marker created only in another checkout, or created but not committed yet, may still be treated as missing or self-approved
- committing the marker first avoids Claude getting blocked mid-run by the local plan gate

## Applies to

- a single approved GitHub issue
- a batch of approved GitHub issues

## Hard constraints

1. Read repo policy files first
2. Respect the approved plan
3. Strengthen resource intelligence before changing code when uncertainty remains
4. Use TDD for code/script changes
5. Validate before commit
6. Use adversarial review for non-trivial changes
7. Commit/push with verification evidence
8. Close the issue only when landed or proven invalid/already satisfied

## Pre-check: is the issue already done?

Before writing code, run a verification-first closure check.
Do not treat "looks done" as enough; require evidence that would justify closing the issue right now.

Minimum pre-check sequence:
1. inspect the expected deliverable surface: files, flags, config, docs, behavior, or output named by the issue/plan
2. run the most relevant targeted tests/validators if they exist
3. read issue comments/linked PRs for prior implementation or landing evidence
4. inspect recent commits/history when comments or repo state suggest the work may already have landed partially or fully
5. compare current repo behavior against the approved acceptance target, not just against changed files
6. make an explicit decision: `already done`, `not done`, or `uncertain`

Evidence required to conclude `already done`:
- at least one direct proof of the deliverable in the current repo state
- at least one verification artifact: passing test output, deterministic inspection result, or runtime/CLI evidence
- enough linkage to explain why this issue is satisfied now: commit hash, merged PR, landed file path, or issue comment reference when available
- acceptance-criteria coverage sufficient to justify closure, not just partial progress

Decision outcomes:
- `already done` -> post a GitHub update with the evidence bundle, state that implementation is already satisfied, and close the issue from the verification-first path
- `not done` -> post a concise note only if the pre-check revealed meaningful findings, then continue to execution mode selection
- `uncertain` -> do not start broad implementation yet; stay in central recon until you can prove `already done` or `not done`

GitHub posting for this stage:
- if the issue is already done, the comment must include what was checked, what passed or was observed, and what artifact proves the work landed
- if the pre-check changes implementation understanding materially, post that finding before coding or delegation
- if uncertainty remains after reasonable checks, post the uncertainty and next verification step instead of pretending execution has started cleanly

This avoids wasting an execution cycle on already-complete work and prevents premature closure without proof.

## Strengthened resource intelligence during execution

Execution is not blind implementation. Re-open intelligence work when needed.

Strengthen resource intelligence whenever you hit uncertainty about:
- where the real implementation surface is
- whether a validator/runtime/docs mismatch already exists elsewhere
- whether the approved plan missed an adjacent dependency
- whether another issue/PR/comment already solved part of the problem
- whether an upstream/external dependency constrains the fix

Resource intelligence during execution may include:
- broader code/test/doc search
- GitHub issue/PR/comment history review
- recent commit inspection
- session recall
- upstream or package/API verification
- searching for alternate or legacy terminology

Post a short GitHub note when this changes the implementation understanding materially.

## Execution pattern per issue

### 1. Post execution start
Comment that execution has started for the approved issue only after the entry gate, already-done pre-check, and execution-mode decision are complete.
Include:
- scope boundary for this execution pass
- chosen mode: `central`, `delegated`, or `hybrid`
- who owns GitHub check-ins if workers are delegated
- immediate validation target or first failing test to be used

### 2. TDD-first loop
Do not start implementation until there is a failing proof for the requirement or a documented reason why deterministic inspection is the only valid path.

Loop:
1. choose the smallest test or validator that can fail for the approved requirement
2. write or update that test first
3. run it in targeted mode and capture the failure evidence
4. if it passes unexpectedly, stop and choose one:
   - `already done` -> return to the verification-first closure path
   - `wrong test` -> tighten the test until it proves the real gap
   - `wrong scope` -> stop and re-check the approved plan before coding
5. make the minimal change that should turn the test green
6. re-run the same targeted validator immediately
7. repeat until the requirement turns green without widening scope

Evidence required before leaving the loop:
- test/validator name or command
- failing result was observed at least once unless deterministic inspection is the approved proof path
- final targeted pass result after the fix

Stop/continue rule:
- continue only while each loop iteration reduces the known gap to the approved acceptance target
- stop when the next change would require unapproved scope, touching forbidden paths, or guessing about missing acceptance details

For scripts/config/docs:
- use the narrowest executable or static assertion available
- if no executable test exists, require deterministic inspection evidence and name exactly what artifact proves the requirement

### 3. Minimal implementation pass
Implement the smallest change that satisfies the approved plan and the failing proof.
Rules:
- prefer one requirement slice at a time over broad rewrites
- keep unrelated cleanup out unless it is required for correctness or safety
- if adjacent work is necessary, state why it is inseparable from the approved fix
- if adjacent work is useful but not required, create a future issue instead of expanding scope

### 4. Targeted validation gate
Run validation in escalating order and stop at the first failing gate:
1. fast local correctness checks relevant to the changed surface
   - syntax/type/lint/unit target directly affected by the change
2. requirement proof
   - the exact test(s)/validator(s) used in the TDD loop
3. safe behavior confirmation when applicable
   - dry run, CLI invocation, deterministic output check, or manual inspection with explicit expected result
4. broader regression check only when risk justifies it
   - nearby test file, package-level suite, or other bounded regression pass

Validation discipline:
- start with the smallest command that can reject the change
- broaden only when the risk surface justifies it
- do not substitute a broad green suite for missing targeted proof
- if a validator flakes or is environment-blocked, do not wave it through; either stabilize it, document the blocker, or stop

Required evidence bundle:
- exact commands run
- whether each command was targeted or broader regression coverage
- pass/fail result and any deterministic inspection artifact
- explicit note for anything intentionally not run and why

## Acceptance-criteria traceability

Before closeout, map each acceptance criterion to explicit proof:
- acceptance criterion -> test name(s)
- acceptance criterion -> validation command(s)
- acceptance criterion -> deterministic inspection evidence when tests are not sufficient

If any criterion lacks proof, the issue is not ready to close.

Post a GitHub progress update after validation when the issue spans meaningful implementation work.

## Multi-agent verification gate

When work was delegated across agents or terminals, do not close on per-agent success alone.

Before commit/closeout, the orchestrator must run a unified verification gate:
- confirm each delegated stream stayed inside owned paths
- review diffs for hidden overlap, missing integration, or conflicting assumptions
- run the agreed validation commands from the main session/environment
- map acceptance criteria across the combined result, not just per-stream outputs
- decide whether any cross-stream discovery must become a future issue before closeout

Required integration evidence:
- per-stream completion status: `done`, `partial`, `blocked`, or `rejected`
- per-stream validator result and any path-contract deviation
- final integrated validation output from the orchestrator session
- explicit statement of whether new future issues were created from cross-stream findings

If unified verification is incomplete, keep the issue open and post the remaining gap.
Do not commit/push/close on worker-local evidence alone.

### 5. Adversarial review gate
For non-trivial changes, run a review pass focused on:
- correctness vs issue acceptance criteria
- hidden behavior mismatches
- shell safety / state handling / regression risk
- adequacy of tests
- whether discovered extra work should become future issues instead of expanding scope

Classify the result explicitly:
- `PASS` -> no material objections remain
- `MINOR` -> optional improvements only; can continue if documented
- `MAJOR` -> correctness, safety, scope, or validation gap remains; must fix before commit/push

Required review evidence:
- what was challenged
- what failed or almost failed under adversarial reasoning
- what was changed or consciously accepted as non-blocking

Stop/continue rule:
- if review returns `MAJOR`, return to the TDD/validation loop
- if review returns `MINOR`, record the residual risk level, residual risk, or future-issue candidate
- continue only on `PASS` or documented `MINOR`

Post a GitHub update if review materially changed the solution.

### 6. Commit/push gate
Do not commit or push just because the code looks done.

Commit is allowed only when all are true:
1. the TDD proof is green
2. targeted validation evidence is recorded
3. acceptance-criteria traceability is complete
4. adversarial review is `PASS` or documented `MINOR`
5. artifact hygiene check is complete
6. for delegated/hybrid work, the orchestrator integration gate is complete

Before push, verify:
- the commit message is issue-linked and accurately scoped
- no unrelated files are staged
- the pushed state matches the validated state
- if repo policy requires PR flow, route to that flow instead of silent direct push

Push behavior:
- push immediately after a completed issue or tightly related approved pair
- if push fails, resolve the Git problem without weakening the validation standard
- if the validated tree changes after commit but before push, re-run the affected validators before pushing

## Recovery / rollback rule

If validation or review fails after implementation:
- do not push a weak or unverified fix
- revise the change and re-run validation, or
- revert/reset the local change if the approach is wrong, then post a GitHub update describing the recovery path

### 7. Unified closeout + issue comment
Post one final structured GitHub closeout comment before closing the issue.

Standard closeout block:
- `Result:` landed / already satisfied / invalid / blocked-rerouted
- `Change summary:` concise description of what changed or what was proven
- `Acceptance criteria:` criterion -> proof mapping
- `Validation:` exact commands/results and deterministic inspection evidence
- `Adversarial review:` PASS / MINOR and any residual risk
- `Residual risk level:` Low / Medium / High
- `Git evidence:` commit hash(es), push status, and PR link if applicable
- `Future issues:` created numbers or `none`
- `Residual risks:` explicit list or `none`

GitHub posting rule for closeout:
- if landed, post after validation/review and after the change is committed/pushed or otherwise landed per repo policy
- if already satisfied or invalid, post the proof bundle used to justify closure
- if blocked-rerouted, post why the issue remains open or what successor issue now tracks the work

Close only when one of these is true:
- the fix is landed with evidence
- the issue is already satisfied with evidence
- the issue is invalid/obsolete with evidence

Keep the issue open when:
- push/landing is incomplete
- acceptance traceability has a gap
- validation or review evidence is missing
- a blocker was identified without a resolved reroute path

### 8. Multi-agent closeout/integration reporting
When delegated or hybrid execution was used, append a compact integration block to the final closeout comment:
- `Execution mode:` delegated or hybrid
- `Streams:` list each stream/batch and status: done / partial / blocked / rejected
- `Path contract check:` confirm compliance or list deviations
- `Integration verification:` commands/results run by orchestrator in the final environment
- `Cross-stream findings:` future issues created or `none`
- `Closeout owner:` confirm orchestrator posted the final summary and performed the close/no-close decision

If any stream is partial, blocked, or rejected, do not present the issue as complete.
State exactly what remains and whether it stays on this issue or moved to a future issue.

## Useful batching heuristic
Combine issues only when they truly share the same code path or tests.
Do not combine unrelated issues just to reduce commit count.

For broader waves:
1. finish the active issue cleanly
2. use read-only recon for next candidates if needed
3. decide whether to implement centrally or package as Claude prompts for agent team(s)
4. if packaged to agent teams, enforce zero git contention with explicit owned/read-only/forbidden path boundaries
5. close false positives directly when evidence supports it
6. create future issues instead of letting discoveries disappear between waves

## Execution patterns worth keeping

### Large test coverage issues
Use research first, then parallel implementation only when many files are involved and fixture/context is clear.
Always finish with unified verification in the main session.

### Library integration issues
Use a compact pattern:
1. check installed/version
2. install if needed
3. smoke test the API
4. add evaluation script + tests
5. verify
6. commit
7. close issue with specifics
8. create follow-up issues for deferred hardening or broader adoption work

### Verify-and-close issues
Some issues are best solved by verification rather than code changes.
If evidence shows the requested state already exists, comment with proof and close.

## Git pitfalls

If push fails due to remote mismatch after a valid local commit:
- pull --rebase
- push again

If unrelated edits block the push, stash them temporarily, finish the current issue push, then restore.

## Artifact hygiene

Before commit, check for runtime artifacts and temporary outputs.
Do not stage them unless the issue explicitly requires them.

## Recommended progress report

After each wave or checkpoint, report:
- issues completed
- new work vs verified-already-done
- commit hashes pushed
- validation/review gate status
- future issues created
- what remains feasible next
- whether anything is only local vs already pushed
- running totals when helpful

## Preferred companion skills

- `github-issues` for issue comment/close/create actions
- `github-pr-workflow` only when the repo or user explicitly wants PR-first execution

## Legacy compatibility

Older guidance may reference `workspace-hub-batch-issue-execution`.
Treat that as a deprecated alias/reference for this route, not the primary route name.
