# Archived Skill: `ten-agent-pre-plan-review-wave`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/ten-agent-pre-plan-review-wave`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/ten-agent-pre-plan-review-wave`
Consolidation date: 2026-04-29

---

---
name: ten-agent-pre-plan-review-wave
description: Launch and verify a 10-agent planning-only wave that moves open GitHub issues into status:plan-review using one isolated worktree per issue, wave-specific continuation cron, and post-run artifact-reconciliation checks.
version: 1.0.0
author: Hermes Agent
category: workspace-hub-learned
tags: [overnight, github, planning, worktrees, parallel, status-plan-review]
---

# Ten-Agent Pre-Plan-Review Wave

Use when:
- the user wants a large overnight planning-only batch
- target issues are still before `status:plan-review`
- zero git contention matters more than minimizing setup cost
- a shared main checkout is already dirty or unstable

## Core pattern

1. Query the live queue for open issues without `status:plan-review` and without `status:plan-approved`.
2. Choose a bounded batch (up to 10 worked well) with one issue per worker.
3. Create one fresh worktree per issue from `origin/main`:
   - `/mnt/local-analysis/worktrees/ws-<issue>-planwave10`
   - branch `nightly/<issue>-planwave10`
4. Inside each worktree, write one self-contained prompt at:
   - `docs/plans/overnight-prompts/<wave-id>/worker.md`
5. Launch one Claude process per worktree with:
   - `claude -p --permission-mode acceptEdits --no-session-persistence --output-format text --max-budget-usd 20 "$PROMPT" </dev/null | tee logs/overnight-plan-wave/worker.log`
6. Each worker must do planning only:
   - inspect GH + local evidence
   - draft canonical plan under `docs/plans/`
   - run adversarial review and save `scripts/review/results/*plan-NNN-*`
   - revise once if MAJOR
   - add `status:plan-review` only if approval-ready
   - otherwise post blocker comment and leave unlabeled
7. Pause older continuation jobs and create a new wave-specific continuation cron tied only to the active worktree set.

## Why this pattern worked

A previous shared-worktree overnight planning wave produced shared-index races, sandbox/path confusion, and artifact-location drift. One-issue-per-worktree fixed the highest-risk concurrency problem:
- no shared file ownership
- isolated logs
- isolated prompt paths
- easier per-issue verification and cleanup
- simpler continuation logic

## Verification order after workers finish

Do NOT trust only one surface.

Check in this order:
1. Live GitHub label/comment state
2. Expected plan and review artifacts in the assigned worktree
3. If missing locally, check whether they landed in a pushed branch/commit or sandbox path instead
4. Also check the main/integration checkout for partial artifacts from later manual recovery. A handoff may say an issue is "ready in substance," while the actual repo contains a draft plan, missing review artifacts, or fresh REQUEST_CHANGES/REJECT review outputs. Treat current on-disk + live GitHub state as authoritative over the handoff summary.
5. Classify the issue as:
   - cleanly ready for approval
   - materialize-and-post only (full plan/review text is recoverable and current state does not contradict it)
   - rerun/re-review required (draft plan, missing review artifacts, or blocking latest verdicts)
   - blocked / not promoted

This matters because some workers can successfully post GitHub comments and apply `status:plan-review` even when the claimed local artifacts are not where you expected them; the opposite can also occur after recovery attempts, where local draft artifacts exist but live GitHub was never promoted.

## Post-handoff reconciliation gate

Before resuming a failed 10-agent wave or bulk-promoting "ready in substance" issues, run a short reconciliation pass and write a small status artifact, e.g. `docs/handoffs/YYYY-MM-DD-planwave10-reconciliation.md`.

Recommended columns:
- issue
- live labels/status
- local plan exists?
- local review artifacts exist?
- latest review verdict
- action: `materialize`, `rerun`, `blocked`, or `ready-to-post`
- exact next command/owner

If any issue already has a draft plan with blocking latest verdicts, start there interactively rather than launching another unattended continuation wave. Do not recreate continuation cron until writable/sandbox/GitHub mutation paths are proven healthy.

## Issue-by-issue advancement after reconciliation

After the reconciliation artifact is written, advance issues one at a time in priority order instead of restarting the whole wave:
1. For the top issue, inspect live issue body/comments, local plan, README row, review artifacts, `.planning/quick` reruns, and child issue bodies if the plan is a parent/umbrella.
2. If review findings are concrete, revise the plan and any dependent child issue bodies first; do not label `status:plan-review` while the latest valid finding is `REQUEST_CHANGES`, `REJECT`, or `MAJOR`.
3. Run a focused re-review against the fully inlined/local latest plan. If a provider wrapper fails or times out, record that explicitly; do not let a failed wrapper overwrite a valid artifact.
4. If the only remaining finding is stale live GitHub wording (for example the issue body contradicts the updated plan), post a superseding comment using `gh issue comment --body-file` before applying `status:plan-review`. Do not rely on the local plan alone to override the visible GitHub thread.
5. Only then sync the plan header, README row, review artifacts, GitHub comment, and label. The issue is still not implementation-ready until explicit user approval moves it to `status:plan-approved`.
6. If fresh review finds new structural blockers (for example an implementation plan misses the real build/deploy source-of-truth), revise the local plan, post a concise planning update, leave the issue in draft, and move to a fresh re-review later.

Example outcomes from planwave10 recovery:
- `#2452` advanced to `status:plan-review` only after child issue closure semantics were aligned, r4 review returned Codex MINOR/Gemini APPROVE, and a superseding GitHub comment resolved stale parent-body wording about Black/isort vs flake8.
- `#2438` stayed draft because adversarial review found source/build/test-surface blockers (`content/` -> `dist/`, Vercel deploys `dist/`, site-wide `A&CE` footprint, exact test harness paths). The correct move was to revise the plan and post an update, not apply `status:plan-review`.

### Reconciliation red flags

Treat an issue as `rerun/re-review required` rather than `materialize-and-post` when any of these are true:
- the main checkout contains a newer draft plan whose status says not approval-ready, even if worker logs claim APPROVE/MINOR
- `.planning/quick/` contains a newer rerun output with `REQUEST_CHANGES`, `REJECT`, or `MAJOR`
- GitHub issue comments record an earlier MAJOR/blocker that contradicts a later short recovery summary
- worker logs contain only a summary of intended verdicts, not the full canonical plan body plus full provider findings
- a parent plan depends on child issue closure semantics that have drifted (for example `main` vs `branch/main`, or allowing workflow quarantine when the parent requires exact current CI gate green)
- a required durable evidence artifact is named in the plan but no child issue or implementation lane clearly owns creating it

When red flags exist, write a reconciliation handoff first and advance the single most concrete blocker interactively. In the observed planwave10 recovery, `#2452` had a local draft plus fresh Codex r2 `REQUEST_CHANGES` findings, so it outranked nominally "ready in substance" lanes for the next operator move.

## Prompt contract per worker

Every worker prompt should include:
- exact worktree path and branch
- exact issue number/title
- planning-only instruction
- explicit write boundaries:
  - allowed: assigned `docs/plans/YYYY-MM-DD-issue-NNN-*.md`, assigned `scripts/review/results/*plan-NNN-*`, optional `.planning/quick/*NNN*`
  - forbidden: `docs/plans/README.md`, source code, sibling issue artifacts
- requirement to rerun once on MAJOR
- requirement to leave the issue unlabeled if still blocked

## Continuation cron pattern

Wave-specific continuation jobs are better than reusing an older generic monitor.

The cron should:
1. inspect only the active worktree set for that wave
2. avoid relaunching issues already in flight or already promoted
3. launch the next batch only after current workers finish
4. report promotions, blockers, and any artifact drift

## Pitfalls

- Reusing one shared worktree for many planning agents
- Leaving an older continuation cron active while starting a new wave
- Treating `status:plan-review` as proof that local artifacts are cleanly placed
- Letting workers edit `docs/plans/README.md` concurrently
- Re-running a blocked issue in the same generic wave without first narrowing the known MAJOR findings

## Heuristic for blocked items

If one issue in the batch already has converged MAJOR findings, do not assume it belongs in the same generic flow as fresh issues. Give it either:
- a dedicated rewrite lane, or
- a later targeted rerun after the simpler issues are moved to `status:plan-review`.
