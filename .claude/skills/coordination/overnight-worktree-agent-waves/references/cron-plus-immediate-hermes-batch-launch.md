# Cron + Immediate Hermes Batch Launch

Use when the user asks for long-running/nightly batches and also expects work to start immediately.

## Pattern

1. Create durable scheduled jobs first (for example `hermes cron` / cronjob tool with `every 24h`, bounded repeat count, local delivery, explicit workdir, and required skills).
2. Do not assume the scheduled job starts now. Check `hermes cron status` and `hermes cron list`, but treat truncated/opaque cron output as insufficient evidence.
3. Create an immediate run directory with prompts and logs, e.g.:
   - `/mnt/local-analysis/agent-logs/nightly-YYYYMMDD-HHMM/prompts/batchN.md`
   - `/mnt/local-analysis/agent-logs/nightly-YYYYMMDD-HHMM/logs/batchN.log`
4. Launch manual Hermes runs in background using the same guardrails/skills as the cron jobs:
   ```bash
   RUN=/mnt/local-analysis/agent-logs/nightly-YYYYMMDD-HHMM
   hermes -s <skill-1> -s <skill-2> chat -q "$(cat "$RUN/prompts/batchN.md")" \
     2>&1 | tee -a "$RUN/logs/batchN.log"
   ```
5. Immediately poll each background session or verify with `ps` and log tails. Capture session IDs, PIDs, and log paths in the handoff.
6. Final status must distinguish:
   - scheduled recurring cron jobs and their repeat/next-run behavior,
   - immediate manual background sessions actually running now,
   - completed/failed/stale lanes after log/process verification.

## Guardrails to embed in every prompt

- no self-approval
- no unapproved implementation
- no contractor/prospect outreach unless explicitly approved
- no destructive cleanup/reset of dirty control-plane checkout
- use isolated worktrees with absolute paths
- leave evidence logs/handoffs and exact validation commands

## Pitfalls

- `hermes cron list` may be too terse/truncated in API logs; do not rely on it alone for final claims.
- A process listing tool may not enumerate terminal-spawned background sessions. Use known session IDs, PIDs, `ps`, and log files.
- If a context compaction occurs after launch but before reporting, re-verify current process/log/cron state before claiming success.