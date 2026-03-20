# WRK-1066 Plan — Claude (Route A inline plan)

Route A: plan is inline in `pending/WRK-1066.md § Plan`.

## Steps
1. Create `scripts/operations/env-audit.sh` — SSH-based version collector for all 3 machines; licensed-win-1 marked unreachable (Windows/no-SSH) with graceful skip.
2. Create `config/machines/env-parity.yaml` — initial version matrix from script output.
3. Fix critical drifts on dev-primary (claude CLI, codex, gh); licensed-win-1 deferred to local session.
4. Add weekly cron entry (Sunday 03:45, `full` role) to `scripts/cron/crontab-template.sh`.
5. Codex cross-review; resolve MAJOR findings.
