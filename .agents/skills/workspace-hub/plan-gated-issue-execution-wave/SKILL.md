---
name: plan-gated-issue-execution-wave
description: Execute a multi-issue architecture/planning wave in a plan-gated repo, then safely transition approved issues into implementation with file-based Codex prompts, local approval markers, subprocess monitoring, and cleanup handling for sandbox/hook edge cases.
version: 1.0.0
author: Hermes Agent
---

# Plan-Gated Issue Execution Wave

Current authority: the originating task request or established standing authority authorizes implementation after proportionate planning, TDD and adversarial review; no separate user plan approval, approval label or local marker is required. Honor explicit planning-only limits, unresolved domain decisions and blocking findings. Consequential actions require matching action/destination authority: implementation authority alone does not authorize publication, deployment, access changes, destructive actions or outreach. Reuse existing authorization and preserve owner-controlled approval history without self-labeling.


Use when:
- working in `workspace-hub` or a similar repo with strict plan gates
- a parent architecture issue must be decomposed into child issues
- the user wants Codex prompt files + subprocess launches instead of manual step-by-step orchestration
- some issues are planning-only while others later become implementation-ready

## Core pattern

1. Create/confirm the parent issue and child issue tree first.
2. For each not-yet-approved issue, generate a self-contained planning prompt file under `docs/plans/`.
3. Launch Codex in a background subprocess using the prompt file and monitor it via process polling/watch patterns.
4. When plan-review artifacts land, move issues to `status:plan-review` only.
5. Verify originating task authority, reviewed scope and blocking domain decisions; no approval label or local marker is required for implementation.
6. Generate a separate implementation prompt with strict owned paths and forbidden paths.
7. Launch implementation in a subprocess and monitor completion.
8. Review the output, verify git/GitHub state, and handle residual cleanup or sandbox-blocked follow-ups.

## File-based subprocess launch pattern

```bash
cd /mnt/local-analysis/workspace-hub
PROMPT=$(< docs/plans/<prompt-file>.md)
Codex -p --permission-mode acceptEdits --no-session-persistence --output-format text "$PROMPT" </dev/null | tee /tmp/<run>.log
```

For read-only planning dry runs:

```bash
Codex -p --permission-mode plan --no-session-persistence --output-format text "$PROMPT" </dev/null | tee /tmp/<run>-plan.log
```

## Planning wave workflow

For each issue in the architecture chain:
- read the approved parent/sibling artifacts first
- honor an explicitly planning-only task; otherwise implement reviewed scope within task authority
- tell Codex to produce:
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

## Weekly picklist / catalog-gated wave pattern

When the user wants to execute an approved plan:
1. switch GitHub label from `status:plan-review` to `status:plan-approved`
2. create `.planning/plan-approved/<issue>.md`
3. commit the marker by itself with a small commit message
4. only then launch implementation Codex prompt

1. the catalog entry exists in the durable catalog issue body;
2. the latest/current weekly picklist explicitly allocates that exact entry to this runner/provider;
3. a fresh Phase 0 preflight passes after the allocation comment, including worker-collision and git-cleanliness checks.

If the picklist is missing, post a governance-clean issue comment allocating the entry or documenting the hard stop, preferably via `gh issue comment --body-file` to avoid shell-quoting drift. After posting allocation, re-read the latest issue comment and rerun Phase 0; the allocation comment is not permission to skip collision checks.

See `references/2026-05-23-deepening-sweep-picklist-gate.md` for the session-specific pattern.

## Scope-authorized implementation transition

Verify the originating task or standing authority covers the current plan scope.
Complete adversarial plan review and resolve blocking findings/domain decisions.
Use isolated worktrees and claimed paths, then launch the TDD implementation prompt.
Approval labels/markers are historical records, never required or self-created
to make a worker run. Publication, deployment and merges retain specific authority.

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

After launching a multi-session wave, immediately produce an operator-facing launch report before ending the turn. Include: batch root, README/summary path, one row per lane with issue number, Hermes process session ID, OS PID, worktree/workdir, prompt path, log path, and max turns/budget if applicable, plus the result/artifact directory and copy/paste monitoring commands. Verify current status with `process poll` or `ps -p ...`; do not rely only on a successful launch command.

Remember that unattended `Codex -p` logs may remain 0 bytes until output flush/completion. Treat PID liveness and expected artifact creation as primary health signals, and include that caveat in the report so zero-byte logs are not mistaken for failed launches. If a context compaction/handoff happens after launch, poll the preserved Hermes process IDs first and complete the report rather than relaunching duplicate sessions.

After a watch hit, still wait for the process to exit and then inspect:
- final process output
- `gh issue view <n>`
- relevant changed files / review artifacts
- latest commit(s)

## Host-vs-sandbox execution lesson

If the implementation depends on mounted paths outside the repo (for example `/mnt/ace/...`) Codex sandbox may be unable to access them even when the host can.

Use this rule:
- planning can still proceed if the limitation is documented
- implementation should honestly stop short of completion if live filesystem access is required and unavailable
- if appropriate, follow up with direct host-side execution or a more privileged path for the blocked step

Good example:
- source registration/config changes were completed in-repo
- actual Phase A indexing against `/mnt/ace/mkt-a-codes` remained blocked by sandbox access
- issue stayed open instead of falsely claiming completion

## Hook false-positive lesson

Workspace hooks may incorrectly treat all `CLAUDE.md` files as harness adapter files.

Observed false positive:
- `.Codex/hooks/check-Codex-md-limits.sh` enforced a 20-line limit on `knowledge/wikis/*/AGENTS.md`
- wiki Codex files are generated schema/config docs, not harness adapters

Minimal fix used:

```bash
STAGED=$(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null | grep -E "$HARNESS_PATTERN" | grep -v '^knowledge/wikis/' || true)
```

Apply this only if the user approves a hook fix.

## Verification/cleanup discipline

After implementation completes:
- inspect `git show --stat <commit>` to verify only intended files landed
- inspect `gh issue view <n>` to confirm comment + close state
- check for residual working-tree edits that Codex reported but did not commit
- if a residual is tiny and well-bounded, use a cleanup prompt instead of reopening broad implementation

## Pitfalls

- launching implementation without both label and `.planning/plan-approved/*.md` marker committed
- letting one implementation prompt touch broad/unowned paths in a dirty worktree
- assuming a watch-pattern hit means the process has finished; always wait for exit
- closing an issue when a known residual edit is still only in working tree
- treating sandbox-inaccessible mounted paths as if they were successfully processed
