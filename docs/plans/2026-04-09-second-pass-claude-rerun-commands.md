# Second-pass Claude rerun commands (2026-04-09)

Use these only for streams with real remaining delta.

Prereqs:
1. Run from `/mnt/local-analysis/workspace-hub`
2. Use trusted workspace only
3. Create `logs/` if needed: `mkdir -p logs`
4. These commands use `--permission-mode acceptEdits` because unattended writes were blocked under default/auto

## Priority 1 — T2 economics relaunch

Purpose:
- finish the still-missing delta for #1858
- force startup visibility
- avoid another silent/no-op run

```bash
PROMPT=$(< docs/plans/overnight-prompts/2026-04-09-4claude/terminal-2-field-dev-economics.md)
claude -p \
  --permission-mode acceptEdits \
  --no-session-persistence \
  --output-format text \
  --max-budget-usd 20 \
  "$PROMPT" </dev/null | tee logs/claude-terminal-2-rerun.log
```

Expected closeout artifact:
- either implementation/review artifacts under `/tmp/terminal-2-*`
- or `/tmp/terminal-2-blocker.md`

## Priority 2 — T4 governance/queue relaunch

Purpose:
- implement the remaining bounded delta for #1857/#1839 if writes are allowed
- otherwise produce a clean analysis-only patch plan

```bash
PROMPT=$(< docs/plans/overnight-prompts/2026-04-09-4claude/terminal-4-governance-and-queue.md)
claude -p \
  --permission-mode acceptEdits \
  --no-session-persistence \
  --output-format text \
  --max-budget-usd 20 \
  "$PROMPT" </dev/null | tee logs/claude-terminal-4-rerun.log
```

Expected closeout artifact:
- either implementation/review artifacts under `/tmp/terminal-4-*`
- or `/tmp/terminal-4-analysis.md`

## Optional audit-only reruns

T1 benchmark audit only:
```bash
PROMPT=$(< docs/plans/overnight-prompts/2026-04-09-4claude/terminal-1-subseaiq-benchmarks.md)
claude -p --permission-mode plan --no-session-persistence --output-format text "$PROMPT" </dev/null | tee logs/claude-terminal-1-audit.log
```

T3 naval-arch audit only:
```bash
PROMPT=$(< docs/plans/overnight-prompts/2026-04-09-4claude/terminal-3-naval-arch-vessel-integration.md)
claude -p --permission-mode plan --no-session-persistence --output-format text "$PROMPT" </dev/null | tee logs/claude-terminal-3-audit.log
```

## Recommended execution order

1. Launch T2 alone and confirm startup output appears quickly
2. Launch T4 after T2 shows healthy execution
3. Only run T1/T3 if you want audit/follow-up validation
