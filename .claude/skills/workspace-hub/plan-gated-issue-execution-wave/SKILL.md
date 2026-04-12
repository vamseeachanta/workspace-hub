---
name: plan-gated-issue-execution-wave
description: Execute a multi-issue architecture/planning wave in a plan-gated repo, then safely transition approved issues into implementation with file-based Claude prompts, local approval markers, subprocess monitoring, and cleanup handling for sandbox/hook edge cases.
version: 1.0.0
author: Hermes Agent
---

# Plan-Gated Issue Execution Wave

Use when:
- working in `workspace-hub` or a similar repo with strict plan gates
- a parent architecture issue must be decomposed into child issues
- the user wants Claude prompt files + subprocess launches instead of manual step-by-step orchestration
- some issues are planning-only while others later become implementation-ready

## Core pattern

1. Create/confirm the parent issue and child issue tree first.
2. For each not-yet-approved issue, generate a self-contained planning prompt file under `docs/plans/`.
3. Launch Claude in a background subprocess using the prompt file and monitor it via process polling/watch patterns.
4. When plan-review artifacts land, move issues to `status:plan-review` only.
5. After explicit user approval, convert the issue to `status:plan-approved`, create `.planning/plan-approved/<issue>.md`, and commit that marker before any implementation run.
6. Generate a separate implementation prompt with strict owned paths and forbidden paths.
7. Launch implementation in a subprocess and monitor completion.
8. Review the output, verify git/GitHub state, and handle residual cleanup or sandbox-blocked follow-ups.

## File-based subprocess launch pattern

```bash
cd /mnt/local-analysis/workspace-hub
PROMPT=$(< docs/plans/<prompt-file>.md)
claude -p --permission-mode acceptEdits --no-session-persistence --output-format text "$PROMPT" </dev/null | tee /tmp/<run>.log
```

For read-only planning dry runs:

```bash
claude -p --permission-mode plan --no-session-persistence --output-format text "$PROMPT" </dev/null | tee /tmp/<run>-plan.log
```

## Planning wave workflow

For each issue in the architecture chain:
- read the approved parent/sibling artifacts first
- keep the prompt planning-only unless the issue is already approved for execution
- tell Claude to produce:
  - plan file in `docs/plans/`
  - review artifacts in `scripts/review/results/`
  - GitHub summary comment
  - `status:plan-review` only if the plan is actually ready

Recommended architecture order used successfully:
1. parent operating model
2. provenance/reuse contract
3. durable-vs-transient boundary
4. accessibility map
5. canonical entry points
6. accessibility registry
7. retrieval contract
8. conformance checks

## Approval transition pattern

When the user wants to execute an approved plan:
1. switch GitHub label from `status:plan-review` to `status:plan-approved`
2. create `.planning/plan-approved/<issue>.md`
3. commit the marker by itself with a small commit message
4. only then launch implementation Claude prompt

Example commit:

```bash
git add .planning/plan-approved/2104.md
git commit -m "chore(planning): approve issue #2104 for execution"
```

## Implementation prompt design

Every implementation prompt should include:
- approved issue number and plan path
- review artifact paths
- owned implementation paths only
- explicit forbidden paths
- instruction to stage only owned files, never `git add .`
- exact success criteria from the approved plan
- exact verification checklist
- GitHub closeout instructions

## When a planned issue should split further

If an approved plan still mixes multiple concerns, split into child implementation issues before coding.

A reusable example from this session:
- source registration + initial indexing/dedup
- ledger/provenance backfill
- wiki promotion
- accessibility/entry-point updates

This worked better than forcing one T3 implementation issue.

## Monitoring pattern

Use subprocess monitoring with watch patterns like:
- `APPROVED`
- `status:plan-review`
- `What changed`
- `Verification performed`
- `GitHub comment URL`
- `issue was closed`

After a watch hit, still wait for the process to exit and then inspect:
- final process output
- `gh issue view <n>`
- relevant changed files / review artifacts
- latest commit(s)

## Host-vs-sandbox execution lesson

If the implementation depends on mounted paths outside the repo (for example `/mnt/ace/...`) Claude sandbox may be unable to access them even when the host can.

Use this rule:
- planning can still proceed if the limitation is documented
- implementation should honestly stop short of completion if live filesystem access is required and unavailable
- if appropriate, follow up with direct host-side execution or a more privileged path for the blocked step

Good example:
- source registration/config changes were completed in-repo
- actual Phase A indexing against `/mnt/ace/acma-codes` remained blocked by sandbox access
- issue stayed open instead of falsely claiming completion

## Hook false-positive lesson

Workspace hooks may incorrectly treat all `CLAUDE.md` files as harness adapter files.

Observed false positive:
- `.claude/hooks/check-claude-md-limits.sh` enforced a 20-line limit on `knowledge/wikis/*/CLAUDE.md`
- wiki CLAUDE files are generated schema/config docs, not harness adapters

Minimal fix used:

```bash
STAGED=$(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null | grep -E "$HARNESS_PATTERN" | grep -v '^knowledge/wikis/' || true)
```

Apply this only if the user approves a hook fix.

## Verification/cleanup discipline

After implementation completes:
- inspect `git show --stat <commit>` to verify only intended files landed
- inspect `gh issue view <n>` to confirm comment + close state
- check for residual working-tree edits that Claude reported but did not commit
- if a residual is tiny and well-bounded, use a cleanup prompt instead of reopening broad implementation

## Pitfalls

- launching implementation without both label and `.planning/plan-approved/*.md` marker committed
- letting one implementation prompt touch broad/unowned paths in a dirty worktree
- assuming a watch-pattern hit means the process has finished; always wait for exit
- closing an issue when a known residual edit is still only in working tree
- treating sandbox-inaccessible mounted paths as if they were successfully processed
