# WRK-1080 Plan — Claude

Route A (simple) — inline plan.

1. Write `scripts/operations/backup-workspace.sh`
   - rsync 5 target paths to ace-linux-2:/mnt/workspace-hub-backup/
   - --link-dest for incremental; excludes .git/, __pycache__/, *.pyc, site/
   - Creates destination dir if missing; logs size delta to logs/backup/backup.log
   - --dry-run flag for restore verification

2. Add daily cron entry at 04:00 on ace-linux-1

3. Write .claude/docs/workspace-recovery.md — step-by-step restore procedure

4. Run backup to verify first run; dry-run restore to /tmp/workspace-restore-test/

5. Codex cross-review of the script; fix any findings
