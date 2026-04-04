#!/usr/bin/env bash
# redact-session-signals.sh — Strip last_assistant_message from session-signal JSONL
#
# The last_assistant_message field in session-signal JSONL files contains LLM
# response text that may reference client project names (Prelude FLNG, West
# Boreas, 2H Offshore, etc.). This violates legal-sanity-scan.sh rules.
#
# The valuable metadata (session_id, hook_event_name, permission_mode, cwd,
# stop_hook_active) is preserved. Only the LLM response text is removed.
#
# Usage:
#   bash scripts/cron/redact-session-signals.sh [--dry-run]
#
# Called by commit-learning-artifacts.sh before git-add.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="$(cd "$SCRIPT_DIR/../.." && pwd)"
SIGNALS_DIR="${WORKSPACE_HUB}/.claude/state/session-signals"

DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
  esac
done

log() { echo "[redact-session-signals] $*"; }

if [[ ! -d "$SIGNALS_DIR" ]]; then
  log "No session-signals directory — nothing to do"
  exit 0
fi

source "${WORKSPACE_HUB}/scripts/lib/python-resolver.sh" 2>/dev/null || PYTHON=python3

redacted=0
skipped=0

for jsonl_file in "$SIGNALS_DIR"/*.jsonl; do
  [[ -f "$jsonl_file" ]] || continue
  basename=$(basename "$jsonl_file")

  # Skip files that don't contain the field (cost-tracking, smoke-tests, etc.)
  if ! grep -q '"last_assistant_message"' "$jsonl_file" 2>/dev/null; then
    skipped=$((skipped + 1))
    continue
  fi

  if $DRY_RUN; then
    lines_with=$(grep -c '"last_assistant_message"' "$jsonl_file" 2>/dev/null || echo 0)
    log "[dry-run] Would redact $basename ($lines_with lines with last_assistant_message)"
    redacted=$((redacted + 1))
    continue
  fi

  # Redact in-place using Python for safe JSON manipulation
  ${PYTHON} -c "
import json, sys, os, tempfile

inpath = '$jsonl_file'
lines_out = []
changed = False

with open(inpath) as f:
    for line in f:
        line = line.rstrip('\n')
        if not line:
            lines_out.append(line)
            continue
        try:
            obj = json.loads(line)
            if 'last_assistant_message' in obj:
                # Keep first 80 chars as a non-identifying summary hint
                msg = obj['last_assistant_message']
                # Truncate to first sentence or 80 chars, whichever is shorter
                trunc = msg[:80].split('.')[0] + '...' if len(msg) > 80 else msg
                obj['last_assistant_message'] = '[REDACTED]'
                changed = True
            lines_out.append(json.dumps(obj, ensure_ascii=False))
        except (json.JSONDecodeError, TypeError):
            lines_out.append(line)

if changed:
    # Atomic write
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(inpath))
    with os.fdopen(fd, 'w') as f:
        f.write('\n'.join(lines_out) + '\n')
    os.replace(tmp, inpath)
    print('REDACTED')
else:
    print('CLEAN')
" 2>/dev/null

  result=$?
  if [[ $result -eq 0 ]]; then
    redacted=$((redacted + 1))
  fi
done

log "Redacted: $redacted files, Skipped: $skipped files (no last_assistant_message)"
