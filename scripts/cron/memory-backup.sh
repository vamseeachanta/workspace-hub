#!/usr/bin/env bash
# memory-backup.sh — rsync Claude memory to remote with race-condition tolerance
# Cron: 0 5 * * *  /path/to/memory-backup.sh >> /tmp/claude-memory-backup.log 2>&1

set -euo pipefail

RSYNC_OPTS=(-a --delete --ignore-missing-args --exclude='*.tmp' --exclude='.*.jsonl.*')
SSH_OPTS=(-e "ssh -o ConnectTimeout=10 -o BatchMode=yes")
DST_HOST="ace-linux-2"

echo "$(date '+%Y-%m-%d %H:%M:%S') [START] agent memory backup"
overall_rc=0

# 1. Claude Code project memory (original scope)
SRC="$HOME/.claude/projects/"
DST="${DST_HOST}:~/workspace-hub-backup/claude-projects/"
echo "  Backing up Claude project memory..."
rsync "${RSYNC_OPTS[@]}" "${SSH_OPTS[@]}" "$SRC" "$DST" 2>/dev/null
rc=$?
[[ "$rc" -eq 24 || "$rc" -eq 0 ]] || overall_rc=$rc

# 2. Hermes memories + sessions (#1782)
if [[ -d "$HOME/.hermes/memories" ]]; then
  echo "  Backing up Hermes memories..."
  rsync "${RSYNC_OPTS[@]}" "${SSH_OPTS[@]}" \
    "$HOME/.hermes/memories/" \
    "${DST_HOST}:~/workspace-hub-backup/hermes-memories/" 2>/dev/null || true
fi
if [[ -d "$HOME/.hermes/sessions" ]]; then
  echo "  Backing up Hermes sessions..."
  rsync "${RSYNC_OPTS[@]}" "${SSH_OPTS[@]}" \
    "$HOME/.hermes/sessions/" \
    "${DST_HOST}:~/workspace-hub-backup/hermes-sessions/" 2>/dev/null || true
fi

# 3. Codex sessions + state (#1782)
if [[ -d "$HOME/.codex/sessions" ]]; then
  echo "  Backing up Codex sessions..."
  rsync "${RSYNC_OPTS[@]}" "${SSH_OPTS[@]}" \
    "$HOME/.codex/sessions/" \
    "${DST_HOST}:~/workspace-hub-backup/codex-sessions/" 2>/dev/null || true
fi
if [[ -f "$HOME/.codex/rules/default.rules" ]]; then
  echo "  Backing up Codex state..."
  rsync "${RSYNC_OPTS[@]}" "${SSH_OPTS[@]}" \
    "$HOME/.codex/rules/" \
    "${DST_HOST}:~/workspace-hub-backup/codex-rules/" 2>/dev/null || true
fi

# 4. Gemini sessions (#1782)
if [[ -d "$HOME/.gemini/tmp" ]]; then
  echo "  Backing up Gemini sessions..."
  rsync "${RSYNC_OPTS[@]}" "${SSH_OPTS[@]}" \
    "$HOME/.gemini/tmp/" \
    "${DST_HOST}:~/workspace-hub-backup/gemini-sessions/" 2>/dev/null || true
fi

if [ "$overall_rc" -eq 0 ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') [OK] backup completed"
  exit 0
else
  echo "$(date '+%Y-%m-%d %H:%M:%S') [FAIL] backup had errors (exit=$overall_rc)"
  exit "$overall_rc"
fi
