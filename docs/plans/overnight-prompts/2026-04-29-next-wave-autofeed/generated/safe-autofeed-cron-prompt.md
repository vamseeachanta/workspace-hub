Global rules for this autofeed cron worker (every 20 min):

- Workspace: /mnt/local-analysis/workspace-hub. cd there before any operation.
- Treat ace-linux-1 as the control plane; ace-linux-2 is overflow only.
- Do NOT send outreach. Do NOT expose private contact details. Do NOT hardcode or print secrets.
- Do NOT apply status:plan-approved to any GitHub issue. The user-in-loop gate is load-bearing.
- Do NOT run any of: gh issue edit, gh issue comment, gh issue close, gh pr create, gh pr review, gh pr merge, scripts/review/plan-review-fanout.sh, codex exec, gemini, hermes (any state-mutating subcommand), git push --force.
- Do NOT create or edit .planning/plan-approved/* markers.
- Do NOT implement code on any issue. Plan-only / review-only / synthesis-only lanes are allowed.
- Use unique tmux session names, unique log file names, and unique result file names. Never overwrite a result file produced by another lane.
- If unsure, write a blocker note and stop. Bias toward inaction.

Mission: inspect filesystem and live-state signals, then **at most one** safe follow-up lane per pass, drawn from the priority-ordered queue at docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/autofeed-policy-and-next-queue.md §6. Multiple passes accumulate naturally because each pass re-evaluates state.

## Step 0 — short-circuit checks (each must PASS before continuing)

Run these and exit 0 immediately if any short-circuits fire. Write a brief skip note to results/<utc-stamp>-cron-skipped-<reason>.md before exit so operators can audit.

```bash
ROOT=/mnt/local-analysis/workspace-hub
WAVE_DIR="$ROOT/docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed"
STAMP=$(date -u +%Y%m%d-%H%M)

# A. Operator stop flag — highest precedence
test -f "$ROOT/.planning/cron-stop.flag" && exit 0

# B. Hermes / git-mutation operation in flight — defer
if pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)' >/dev/null 2>&1; then
  echo "deferred: git mutation in flight" \
    > "$WAVE_DIR/results/${STAMP}-cron-skipped-hermes.md"
  exit 0
fi

# C. Lock file — only one autofeed pass at a time. The cron registration
#    should already wrap with `flock -n /tmp/safe-autofeed-cron.lock`,
#    but double-check here in case the registration was loosened.
exec 9>/tmp/safe-autofeed-cron.lock
flock -n 9 || { echo "deferred: another autofeed pass holds the lock" \
  > "$WAVE_DIR/results/${STAMP}-cron-skipped-locked.md"; exit 0; }
```

The Claude session executing this prompt does not need to run those bash blocks itself — they belong in the cron wrapper. The session's job is the **decide-and-launch** logic in the steps below. But the session MUST verify each precondition exists in the wrapper before it dispatches, by reading this prompt's first lines aloud in its own output and stopping if it cannot confirm.

## Step 1 — gather state (read-only)

The session executes these read-only commands and records each output in its working buffer:

```bash
cd /mnt/local-analysis/workspace-hub

# 1. tmux sessions live (local)
tmux ls 2>/dev/null || true

# 2. Result files in this wave (so far)
ls -lt docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/ 2>/dev/null

# 3. Cross-review artifacts written today
ls -lt scripts/review/results/2026-04-29-plan-*.md 2>/dev/null

# 4. Live status:plan-review issues
gh issue list --state open --label status:plan-review --json number,title,updatedAt --limit 30

# 5. Live status:plan-approved issues (read-only — DO NOT mutate)
gh issue list --state open --label status:plan-approved --json number,title,updatedAt --limit 30

# 6. Recently-touched plan files
ls -lt docs/plans/2026-04-2[789]-issue-*.md 2>/dev/null | head -20
```

If `gh` is unauthorized in the cron sandbox, fall back to reading the latest `results/approval-synthesis-10.md` for label snapshots. Mark every label-derived decision as `(stale snapshot)` in any artifact you write — never silently accept the snapshot as live.

## Step 2 — classify each known lane (deterministic)

For each tmux session name found in step 1.1, AND for each prior lane discoverable from `results/*.md` filenames in step 1.2, compute the classification using exactly these rules. Use the `classify(...)` pseudocode from autofeed-policy-and-next-queue.md §3:

- RUNNING — tmux session present.
- COMPLETED_WITH_RESULT — tmux absent AND result file exists AND result_size ≥ 200 bytes.
- STUB_RESULT — tmux absent AND result file exists AND result_size < 200 bytes.
- FAILED_NO_RESULT — tmux absent AND log file ≥ 200 bytes AND result file missing.
- ABORTED_EARLY — tmux absent AND 0 < log_size < 200 bytes AND result file missing.
- ABORTED_NO_OUTPUT — tmux absent AND log_size == 0 AND result file missing.
- STALE_RUNNING — tmux present AND log mtime > 90 min ago AND log_size == 0. Treat as needs-human; do NOT relaunch and do NOT consider the slot free.
- NEVER_STARTED — neither tmux nor log nor result.

Write the classification table inline in the cron pass's result artifact (see step 5).

## Step 3 — decide candidate lane (at most one per pass)

Walk the priority-ordered queue from autofeed-policy-and-next-queue.md §6. For each row in queue order:

1. Check the row's "Trigger condition" against the state gathered in step 1.
2. Verify the row's expected result-file path does NOT already exist (no overwrite).
3. Verify the row's expected tmux session name does NOT collide with any RUNNING session.
4. Verify capacity: count RUNNING lanes on the row's host. If host is `ace-linux-1`, capacity is `MAX_LOCAL_LANES=3`; if `ace-linux-2`, capacity is `MAX_REMOTE_LANES=2`. If at capacity, skip to the next row.
5. Verify guardrails: confirm the row's lane is plan-only / review-only / synthesis-only per §5. If it touches any of the unsafe transitions in §5, skip and write a `cron-skipped-unsafe.md` note.

The first row that passes all five checks is the candidate. If no row passes, write a `cron-idle-<utc-stamp>.md` note and stop. Do NOT cycle the same chain twice in a row — if the most recent COMPLETED lane was on issue #N, skip any queue row also targeting #N and try the next one. Diversity beats throughput.

## Step 4 — draft the lane prompt and launch

If a candidate row is selected, write the lane's prompt file under `generated/<lane-name>.md` using the template in autofeed-policy-and-next-queue.md §7. Each prompt MUST embed:

- The full Global rules block from this cron prompt (verbatim copy).
- The lane-specific Inputs to read first list (paths from queue row).
- The lane-specific Do steps (3-5 numbered steps, no implementation).
- The lane-specific Hard guardrails block (verbatim copy of §5 unsafe transitions).
- The expected result file path.

Then launch via the existing runner script with unique session/log names:

```bash
SESSION="autofeed-${LANE_NAME}-${STAMP}"
LOG="$ROOT/logs/night-runs/${SESSION}.log"
PROMPT="$WAVE_DIR/generated/${LANE_NAME}.md"

# Re-check the session does not exist (defense in depth)
if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "skip: session collision $SESSION" \
    > "$WAVE_DIR/results/${STAMP}-cron-skipped-collision.md"
  exit 0
fi

# Re-check the prompt is git-tracked, smaller than 200 KB, and starts with "Global rules"
git ls-files --error-unmatch "$PROMPT" || { echo "skip: prompt not git-tracked" \
  > "$WAVE_DIR/results/${STAMP}-cron-skipped-untracked.md"; exit 0; }
[ "$(wc -c < "$PROMPT")" -lt 204800 ] || { echo "skip: prompt > 200KB" \
  > "$WAVE_DIR/results/${STAMP}-cron-skipped-oversized.md"; exit 0; }
head -1 "$PROMPT" | grep -q '^Global rules' || { echo "skip: prompt missing Global rules header" \
  > "$WAVE_DIR/results/${STAMP}-cron-skipped-bad-header.md"; exit 0; }

# Launch
tmux new-session -d -s "$SESSION" \
  "bash '$WAVE_DIR/run-claude-prompt.sh' '$PROMPT' '$LOG' acceptEdits"
```

If the candidate row's host is `ace-linux-2`, do not ssh from this cron pass. Instead, write a one-line dispatch directive to `generated/<lane-name>.dispatch-ace2.md` containing the rsync+ssh command, and let the wave dispatcher handle 2 it on its next fire. The autofeed cron is local-only by policy — keeps the lock and the host context simple.

## Step 5 — write the cron-pass result artifact (always)

Whether the pass launched a lane, skipped, or idled, it writes exactly one artifact at:

`docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/cron-pass-${STAMP}.md`

Format:

```markdown
# Autofeed cron pass ${STAMP}

| Field | Value |
|---|---|
| Started | <UTC ISO> |
| Finished | <UTC ISO> |
| Decision | LAUNCHED / SKIPPED / IDLE |
| Selected lane | <name from queue, or `none`> |
| Generated prompt | <path, or `none`> |
| Tmux session | <name, or `none`> |
| Log file | <path, or `none`> |
| Result expected at | <path, or `none`> |

## Lane classifications observed
<table from step 2>

## Queue evaluation trace
<one row per §6 queue position: row #, trigger met?, capacity OK?, collision OK?, guardrails OK?, decision>

## Boundary compliance
- No GitHub mutations.
- No approval markers created.
- No source-file edits.
- Exactly one result file written by this pass (this file).
- Exactly zero or one new prompt file written under generated/.
- Exactly zero or one tmux session launched, with unique session name.
```

## Step 6 — exit

Release the flock. Exit 0 (even on skip) so the cron registration does not retry.

## Recovery / failure modes

- **Codex / Gemini CLIs called accidentally**: this prompt forbids them; if any sub-step would invoke them, replace with a write-only blocker note.
- **codex-cli 0.124+ stdin-hang**: not relevant here because this cron is Claude-only. Ignore.
- **Hermes runs preempt git**: handled in step 0.B.
- **Worktree gitlink pollution**: this cron does not create worktrees. All launches use the main checkout.
- **Sparse-checkout overlay blindness**: this cron does not invoke Gemini, so the overlay-blind issue from `feedback_gemini_sandbox_overlay_blindness.md` does not apply.
- **Auto-sync race**: this cron does not commit. The cron-pass result artifact is left uncommitted; the operator decides whether to add it to a sync.
- **Lane explosion**: bounded by `MAX_LOCAL_LANES=3` and the one-launch-per-pass rule. If the operator wants to increase parallelism, edit those constants and re-deploy.

## Audit checklist (read by operator after each pass)

```bash
WAVE=docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed
ls -lt "$WAVE/results/cron-pass-"*.md | head -10
ls -lt "$WAVE/generated/" | head -10
ls -lt logs/night-runs/autofeed-* 2>/dev/null | head -10
tmux ls 2>/dev/null | grep '^autofeed-' || echo "no autofeed sessions running"
```

If any cron-pass-*.md row shows `Decision = LAUNCHED` for a lane the operator did not expect, inspect immediately by reading the corresponding `generated/<lane>.md` and `logs/night-runs/<lane>.log`. Then add a one-line `cron-stop.flag` if the launch was unsafe.

## End of cron prompt

The session's final user-facing output should be the path to the `cron-pass-${STAMP}.md` it wrote, plus the decision verdict, plus the launched session name (if any). No further chatter.
