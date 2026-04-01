#!/usr/bin/env bash
# memory-backup.sh — rsync Claude memory to remote with race-condition tolerance
# Cron: 0 5 * * *  /path/to/memory-backup.sh >> /tmp/claude-memory-backup.log 2>&1

set -euo pipefail

SRC="$HOME/.claude/projects/"
DST="ace-linux-2:~/workspace-hub-backup/claude-projects/"

echo "$(date '+%Y-%m-%d %H:%M:%S') [START] memory backup"

rsync -a --delete \
  --ignore-missing-args \
  --exclude='*.tmp' \
  --exclude='.*.jsonl.*' \
  "$SRC" "$DST"
rc=$?

# Exit code 24 = "some files vanished before transfer" — expected during active sessions
if [ "$rc" -eq 24 ] || [ "$rc" -eq 0 ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') [OK] backup completed (exit=$rc)"
  exit 0
else
  echo "$(date '+%Y-%m-%d %H:%M:%S') [FAIL] backup failed (exit=$rc)"
  exit "$rc"
fi
