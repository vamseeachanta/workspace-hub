# Archived Skill: `overnight-worktree-claude-noop-recovery`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/overnight-worktree-claude-noop-recovery`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/overnight-worktree-claude-noop-recovery`
Consolidation date: 2026-04-29

---

---
name: overnight-worktree-claude-noop-recovery
description: Recover overnight Claude worktree batches that appear to succeed but produce no artifacts; harden rerun prompts and launch commands.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Overnight worktree Claude no-op recovery

Use this when an unattended multi-worktree Claude batch is launched correctly, exits with code 0, but expected planning/report artifacts are missing.

## Trigger pattern

- Background `claude -p` jobs in separate worktrees
- `process poll` shows `exit_code: 0`
- stdout/log output is empty or unhelpful
- expected result files under `docs/reports/` / `docs/plans/` / `scripts/review/results/` were not created

## What happened in the learned case

A 3-worktree overnight planning wave was launched safely from isolated worktrees. All three Claude runs exited successfully, but two produced no expected outputs and one only preserved pre-existing artifacts. The initial prompts were too easy for Claude to effectively no-op while still returning success. A first rerun also failed because the launcher used relative prompt-file paths that the shell did not resolve as expected.

## Recovery workflow

1. Verify the run really no-op'd
- Check the expected artifacts directly, not just process exit code.
- For each worktree, inspect:
  - required summary/report file
  - target `docs/plans/*issue*` files
  - target `scripts/review/results/*issue*` files
- If none exist, treat the run as failed even if Claude exited 0.

2. Keep the worktree isolation
- Do NOT rerun in the dirty main checkout.
- Reuse or create one worktree per terminal/lane.
- Preserve zero-overlap write boundaries.

3. Harden the prompt before rerunning
- Make the FIRST mandatory action the creation of a unique summary/result file.
- Require a STARTED section immediately.
- Require a COMPLETED or BLOCKED section before exit.
- State explicitly: do not exit without writing this file.
- Reduce ambition: even if deeper plan edits fail, the summary file must still be produced.

Example requirement block:
- `docs/reports/2026-04-23-terminal-N-...summary.md`
- MUST include STARTED timestamp
- MUST include issues in scope
- MUST include blockers
- MUST append COMPLETED/BLOCKED before exit

4. Use absolute prompt paths in the launcher
- Avoid `PROMPT=$(< docs/plans/.../prompt.md)` in reruns.
- Prefer:
  - `PROMPT=$(< /abs/path/to/prompt.md)`
- This removes cwd/path ambiguity in copied worktree setups.

5. Relaunch as background jobs
- Same `claude -p --permission-mode acceptEdits --no-session-persistence ...`
- Keep one process per worktree.
- Poll after launch to ensure the shell found the prompt file.

6. Morning interpretation rule
- `exit 0 + no artifacts` = failed/no-op run
- `exit nonzero due to prompt path` = launcher failure
- only artifact existence counts as success

## Recommended launch pattern

```bash
wt=/mnt/local-analysis/worktrees/ws-tier1-knowledge-overnight-t2
prompt=$wt/docs/plans/overnight-prompts/2026-04-22-tier1-knowledge-beef-up/rerun-terminal-2-engineering-core-and-utilities.md
cd "$wt"
mkdir -p logs
PROMPT=$(< "$prompt")
claude -p \
  --permission-mode acceptEdits \
  --no-session-persistence \
  --output-format text \
  --max-budget-usd 20 \
  "$PROMPT" </dev/null > logs/claude-tier1-terminal-2-rerun.log 2>&1
```

## Checks to run after a suspicious success

```bash
python - <<'PY'
from pathlib import Path
root=Path('/path/to/worktree')
for pat in [
    'docs/reports/expected-summary.md',
    'docs/plans/*2461*',
    'scripts/review/results/*2461*',
]:
    print(pat, list(root.glob(pat)))
PY
```

## Key lesson

For unattended Claude planning batches, prompt design must force an observable artifact very early. Process exit codes and silent logs are not reliable proof of work completion.
