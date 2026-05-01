---
name: overnight-worktree-agent-waves
version: 1.0.0
category: coordination
description: Operate unattended overnight or background multi-agent waves with worktree isolation, artifact reconciliation, verification fallbacks, and closure-first batching.
tags: [overnight, worktrees, agents, verification]
---

# Overnight Worktree Agent Waves

## When to Use
Use when launching, monitoring, salvaging, or verifying overnight/background Claude/Codex/Hermes lanes across isolated worktrees.

## Class-Level Workflow
1. Partition queues by plan state and dependency risk before launch.
2. Use absolute worktree/log paths and warm required virtualenvs before unattended runs.
3. When the control checkout is dirty or worker contention is unclear, start with read-only `claude -p --permission-mode plan` scout lanes using absolute prompt/output paths before creating write-enabled worktrees; see `ai/durable-provider-throughput-dispatch` reference `references/dirty-workspace-plan-mode-scout-wave.md`.
4. Treat no-op or stalled runs as recoverable: inspect logs, cwd, prompt files, and artifacts before relaunching.
5. Reconcile artifact placement drift back to canonical issue/review locations.
6. Verify claimed commits against the actual working tree before closing issues.
7. Convert unresolved blockers into explicit follow-up issues rather than leaving stale-open work.
8. When surfacing morning/overnight status, report both live GitHub label counts and artifact-audited readiness counts; do not equate `status:plan-review` with "ready for approval" unless current plan files and review artifacts show no blocking MAJOR/FAIL/UNAVAILABLE/provider-capacity defects.

## Morning Status / Approval-Readiness Summary

Use this pattern when the user asks what happened overnight, how many issues are ready for plan approval, or how many issues were executed:

1. **Gather live GitHub state first**: query open `status:plan-review`, open `status:plan-approved`, and recent closed issues (e.g. last 24h). Preserve clickable issue URLs in the final table.
2. **Cross-check local/remote artifacts**: inspect prompt-pack `results/`, `generated/`, review artifacts, lane logs, tmux sessions, and remote ace-linux-2 result files before counting anything as complete.
3. **Separate three counts**:
   - labeled `status:plan-review` count,
   - artifact-audited approval candidates (plans + valid current review artifacts, no blocking verdicts),
   - executed/closed count (issues actually merged/closed or implementation-complete by verified commits/PRs).
4. **Call out invalid review evidence explicitly**: zero-byte review artifacts, provider capacity failures (e.g. Gemini 429/model capacity), auth failures, sandbox/tool-schema failures, or stale reviews mean "needs review rerun", not "ready".
5. **State lane side effects honestly**: if the overnight continuation was planning/review/GTM-only, report implementation/close count as zero for that lane even if broader repo issues closed during the same 24h window.
6. **End with actionable blockers**: list closest approval-prep candidates, issues needing substantive plan repair, and machine/provider constraints affecting the next wave.

## Continuous autofeed / next-wave status checks

Use this when a user asks whether long-running batches are still being tracked, whether new runs are being spun up, or for a status update after an autofeed wave.

1. **Report tracking before conclusions**: list the active monitor/cron jobs, repeat counters, last status, next run time, and delivery target. A drained tmux list is not failure if a monitor is still cycling and result artifacts are appearing.
2. **Check four surfaces, not one**:
   - tmux sessions/processes for currently running lanes,
   - lane logs for launcher/runtime errors,
   - prompt-pack `results/` and `generated/` artifacts for completed or autofed work,
   - remote worker logs/results (e.g. ace-linux-2) and rsync state.
3. **Treat runner errors as first-class status**: if logs contain launcher failures such as `claude: command not found`, `LOGDIR: unbound variable`, or `-budget-usd: command not found`, classify the original lane as failed/stale even when a monitor or follow-up artifact later produced useful output. Verify which component produced each artifact before crediting the lane.
4. **Do not count self-feeding artifacts as approval evidence until verified**: auto-generated review summaries, command packs, and follow-up prompts can advance the conveyor, but promotion readiness still requires current live issue state, valid non-stale review artifacts, and legal/provenance checks.
5. **For remote non-interactive Claude lanes**, ensure the runner exports user-local bins before invoking Claude:
   ```bash
   export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
   ```
   Prefer an SSH heredoc for remote launches when inline quoting expands local variables too early (symptom: `LOGDIR: unbound variable`).
6. **When auto-feed launches follow-ups**, include bounded dedupe rules: no duplicate session/log/artifact names, no `status:plan-approved`, no outreach, no unapproved implementation, and at most the configured safe number of follow-ups per monitor pass.
7. **Harden Claude `-p` runners with argv arrays** when relaunching follow-up waves. If a log shows `-budget-usd: command not found`, treat it as likely shell line-wrap or stale-runner parsing drift around `--max-budget-usd`. Replace long single-line invocations with an array runner that uses an absolute/validated Claude binary, closes stdin, and smoke-checks the flag before launch:
   ```bash
   export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/bin:/bin:$PATH"
   CLAUDE_BIN="${CLAUDE_BIN:-$HOME/.npm-global/bin/claude}"
   "$CLAUDE_BIN" --version >/dev/null
   "$CLAUDE_BIN" --help | grep -q -- '--max-budget-usd'
   cmd=(
     "$CLAUDE_BIN" -p
     --permission-mode "$MODE"
     --no-session-persistence
     --output-format text
     --max-budget-usd "20"
     "$PROMPT"
   )
   "${cmd[@]}" </dev/null 2>&1 | tee -- "$LOG_FILE"
   ```
8. **For scoped artifact commits in dirty control-plane repos**, stage only the verified prompt/result/docs paths, then stash unrelated dirty telemetry/provider churn with `git stash push --keep-index ...` before running `legal-sanity-scan.sh --diff-only`. This prevents unrelated Claude session telemetry containing deny-list terms from falsely blocking a safe planning-artifact commit. Restore the stash only after commit/push verification.
9. **For user-requested nightly batches that should begin immediately**, create both the durable scheduled jobs and manual background Hermes sessions with prompt/log files, then report them separately. Scheduled `every 24h` cron jobs may not run until the next interval; immediate manual sessions prove work is running now. See `references/cron-plus-immediate-hermes-batch-launch.md`.
10. **Validate skill IDs before recurring + immediate launch**: if a lane uses `hermes -s ...`, verify each skill name against `skills_list`/`skill_view` or a known-good loaded skill before creating cron jobs or background sessions. If an immediate lane exits with `Error: Unknown skill(s): ...`, fix the scheduled cron job too (not just the manual rerun) using `hermes cron`/cronjob update, then relaunch the failed lane with the valid class-level skill name. Common drift example: use `software-development/test-driven-development`, not `development/test-driven-development`. See `references/skill-id-validation-for-recurring-and-immediate-lanes.md`.
11. **For over-saturated provider autofeed monitors**, do not jump from patching to cron resume. Keep the recurring job paused, run one controlled live tick, then classify provider health from durable output rather than process count. If Claude/Codex produce 0-byte logs/results and Gemini returns capacity/critical signatures, clean up the tick and switch to provider-health probes. Details live in `ai/durable-provider-throughput-dispatch` reference `references/provider-autofeed-health-recovery.md`.

## Consolidated Session Learnings

The `references/` directory contains archived narrow skills absorbed during the 2026-04-29 umbrella consolidation pass. Use the subsections below as the class-level index, then open the named reference when a case-specific recipe is needed.
## Absorbed Narrow Skills (2026-04-29)

### `cron-plus-immediate-hermes-batch-launch`

- Session reference: `references/cron-plus-immediate-hermes-batch-launch.md`.
- Preserved insight: When the user asks for nightly/continuous batches and immediate progress, create scheduled cron jobs plus manual background Hermes sessions, then verify/report both surfaces separately with prompt/log paths and process IDs.

### `background-claude-worktree-absolute-path-launch`

- Former skill demoted to `references/background-claude-worktree-absolute-path-launch.md`.
- Preserved insight: Prevent overnight/background Claude worker launch failures in git worktrees by using absolute prompt/log paths and immediate post-launch polling.

### `claude-quota-failover-to-codex-for-overnight-plan-lanes`

- Former skill demoted to `references/claude-quota-failover-to-codex-for-overnight-plan-lanes.md`.
- Preserved insight: Recover an overnight multi-worktree planning wave when some Claude lanes hit quota by relaunching only the failed lanes with Codex in the same isolated worktrees and prompt files.

### `closure-first-overnight-batch`

- Former skill demoted to `references/closure-first-overnight-batch.md`.
- Preserved insight: Run a high-leverage overnight batch by clearing stale-open approved issues first, converting shared blockers into tracked issues, and reserving only one lane for true implementation.

### `large-parallel-planning-wave-environment-failure-handoff`

- Former skill demoted to `references/large-parallel-planning-wave-environment-failure-handoff.md`.
- Preserved insight: Handle large pre-plan-review planning waves that succeed analytically but fail to persist artifacts due to quota exhaustion, sandbox write failures, or cancelled GitHub mutations.

### `live-state-aware-overnight-implementation-prompts`

- Former skill demoted to `references/live-state-aware-overnight-implementation-prompts.md`.
- Preserved insight: Design overnight implementation prompts that begin with a live repo/CI precheck so workers continue from partial progress instead of replaying stale handoffs.

### `overnight-plan-artifact-placement-drift-reconciliation`

- Former skill demoted to `references/overnight-plan-artifact-placement-drift-reconciliation.md`.
- Preserved insight: Reconcile overnight planning waves where Claude workers advance GitHub issue state but the expected plan/review artifacts are missing from the designated external worktree because the worker wrote from a sandbox/in-repo worktree and pushed directly to the branch.

### `overnight-plan-wave-artifact-drift-reconciliation`

- Former skill demoted to `references/overnight-plan-wave-artifact-drift-reconciliation.md`.
- Preserved insight: Reconcile overnight planning waves when Claude workers move GitHub issues to status:plan-review but local artifacts are missing, split across sandbox worktrees, or only present on a pushed remote branch.

### `overnight-planning-noop-run-salvage`

- Former skill demoted to `references/overnight-planning-noop-run-salvage.md`.
- Preserved insight: Recover when unattended overnight Claude planning runs exit 0 but produce no required artifacts; salvage the wave by auditing existing plan state, generating missing summary artifacts manually, and preserving morning monitoring surfaces.

### `overnight-pre-plan-review-wave-artifact-drift`

- Former skill demoted to `references/overnight-pre-plan-review-wave-artifact-drift.md`.
- Preserved insight: Run overnight planning-only waves for issues before status:plan-review, and reconcile cases where GitHub state advances but plan/review artifacts land in a sandbox or remote branch instead of the active local worktree.

### `overnight-verify-close-and-blocker-conversion`

- Former skill demoted to `references/overnight-verify-close-and-blocker-conversion.md`.
- Preserved insight: Use overnight Claude lanes to clear stale-open GitHub issues by verification-first closure, and convert blocked PR-repair attempts into dedicated blocker issues instead of speculative edits.

### `overnight-verify-close-batch`

- Former skill demoted to `references/overnight-verify-close-batch.md`.
- Preserved insight: Build overnight parallel batches that close stale-open GitHub issues by proving landed work already satisfies the issue, instead of wasting implementation lanes on redoing completed work.

### `overnight-wave-pack-worktree-isolation`

- Former skill demoted to `references/overnight-wave-pack-worktree-isolation.md`.
- Preserved insight: Safely launch overnight multi-terminal workspace-hub planning packs from isolated worktrees when the main checkout is dirty or prompts share planning/index files.

### `overnight-worktree-claude-noop-recovery`

- Former skill demoted to `references/overnight-worktree-claude-noop-recovery.md`.
- Preserved insight: Recover overnight Claude worktree batches that appear to succeed but produce no artifacts; harden rerun prompts and launch commands.

### `overnight-worktree-uv-warmup-and-log-path-guardrails`

- Former skill demoted to `references/overnight-worktree-uv-warmup-and-log-path-guardrails.md`.
- Preserved insight: Prevent false stalls and missing-log failures in overnight Claude worktree batches by pre-warming uv environments, using exact log-path directory creation, and interpreting buffered logs correctly.

### `overnight-worktree-verification-fallback`

- Former skill demoted to `references/overnight-worktree-verification-fallback.md`.
- Preserved insight: Verify overnight multi-worktree Claude batches when auto-sync, duplicate-lane convergence, and sandbox-blocked review create misleading local state or review provenance.

### `workspace-hub-overnight-plan-monitor`

- Former skill demoted to `references/workspace-hub-overnight-plan-monitor.md`.
- Preserved insight: Monitor and reconcile workspace-hub overnight planning or implementation batches, including process status, result artifacts, issue/commit verification, and controlled failed-lane recovery.

### `plan-gated-overnight-queue-partition`

- Former skill demoted to `references/plan-gated-overnight-queue-partition.md`.
- Preserved insight: Partition a plan-gated GitHub queue before launching overnight work so ineligible pre-approval issues are routed to planning/review lanes and only approved issues are used for merge-capable execution.

### `verify-claude-run-commit-vs-working-tree-before-closing`

- Former skill demoted to `references/verify-claude-run-commit-vs-working-tree-before-closing.md`.
- Preserved insight: After a Claude implementation run, verify the claimed file set against the actual commit and working tree before treating the issue as fully complete.
