#!/usr/bin/env bash
# codex-session-export.sh — Export Codex sessions to orchestrator JSONL format
#
# Converts ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl to
# logs/orchestrator/codex/session_YYYYMMDD.jsonl matching the Claude
# orchestrator format for comprehensive-learning pipeline consumption.
#
# Usage: bash scripts/cron/codex-session-export.sh [--dry-run] [--all]
# Cron:  Called by comprehensive-learning-nightly.sh
#
# By default, only exports sessions newer than the last export timestamp.
# Use --all to re-export everything.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="$(cd "$SCRIPT_DIR/../.." && pwd)"
CODEX_SESSIONS="${HOME}/.codex/sessions"
OUTPUT_DIR="${WORKSPACE_HUB}/logs/orchestrator/codex"
STATE_FILE="${OUTPUT_DIR}/.last-export-ts"

DRY_RUN=false
EXPORT_ALL=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --all)     EXPORT_ALL=true ;;
  esac
done

mkdir -p "$OUTPUT_DIR"

if [[ "$EXPORT_ALL" == "true" && "$DRY_RUN" == "false" ]]; then
  rm -f "$OUTPUT_DIR"/session_*.jsonl "$STATE_FILE"
fi

if [[ ! -d "$CODEX_SESSIONS" ]]; then
  echo "No Codex sessions directory at $CODEX_SESSIONS — skipping"
  exit 0
fi

# Determine cutoff
last_ts=""
if [[ -f "$STATE_FILE" && "$EXPORT_ALL" == "false" ]]; then
  last_ts=$(cat "$STATE_FILE")
fi

source "${WORKSPACE_HUB}/scripts/lib/python-resolver.sh" 2>/dev/null || PYTHON=python3

exported=0
skipped=0

for session_file in $(find "$CODEX_SESSIONS" -name "rollout-*.jsonl" -type f 2>/dev/null | sort); do
  [[ -f "$session_file" ]] || continue

  # Skip if older than last export
  if [[ -n "$last_ts" ]]; then
    file_ts=$(stat -c %Y "$session_file" 2>/dev/null || stat -f %m "$session_file" 2>/dev/null || echo 0)
    if [[ "$file_ts" -le "$last_ts" ]]; then
      skipped=$((skipped + 1))
      continue
    fi
  fi

  # Extract date from path: .../YYYY/MM/DD/rollout-...
  session_date=$(echo "$session_file" | grep -oE '[0-9]{4}/[0-9]{2}/[0-9]{2}' | tr -d '/')
  [[ -z "$session_date" ]] && continue

  output_file="${OUTPUT_DIR}/session_${session_date}.jsonl"

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[dry-run] Would export $(basename "$session_file") -> session_${session_date}.jsonl"
    exported=$((exported + 1))
    continue
  fi

  # Convert Codex session JSONL to orchestrator format
  ${PYTHON} -c "
import json, sys, os

TOOL_MAP = {
    'exec_command': 'Bash',
    'read_file': 'Read',
    'write_file': 'Write',
    'apply_diff': 'Edit',
    'write_stdin': 'Bash',
    'list_directory': 'Read',
    'search_files': 'Grep',
    'browser': 'Browser',
}

try:
    lines = []
    session_id = ''
    model = 'codex'
    cwd = ''

    with open('$session_file') as f:
        for raw_line in f:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                obj = json.loads(raw_line)
            except json.JSONDecodeError:
                continue

            ts = obj.get('timestamp', '')
            msg_type = obj.get('type', '')
            payload = obj.get('payload', {})

            if msg_type == 'session_meta':
                session_id = payload.get('id', '')
                cwd = payload.get('cwd', '')
                model = payload.get('model_provider', 'codex')

            elif msg_type == 'response_item' and payload.get('type') == 'function_call':
                name = payload.get('name', '')
                mapped = TOOL_MAP.get(name, name)
                entry = {
                    'ts': ts,
                    'hook': 'post',
                    'tool': mapped,
                    'codex_tool': name,
                    'project': 'workspace-hub',
                    'repo': 'workspace-hub',
                    'model': model,
                    'session_id': session_id,
                }

                # Add context
                if name == 'exec_command':
                    args = payload.get('arguments', '{}')
                    try:
                        args = json.loads(args) if isinstance(args, str) else args
                    except json.JSONDecodeError:
                        args = {}
                    cmd = ''
                    if isinstance(args, dict):
                        cmd = args.get('command', '') or ''
                        for item in args.get('cmd', []):
                            if isinstance(item, str):
                                cmd += ' ' + item
                    entry['cmd'] = str(cmd)[:500]
                elif name in ('read_file', 'write_file', 'apply_diff'):
                    args = payload.get('arguments', '{}')
                    try:
                        args = json.loads(args) if isinstance(args, str) else args
                    except json.JSONDecodeError:
                        args = {}
                    if isinstance(args, dict):
                        entry['file'] = args.get('path', args.get('file_path', ''))

                lines.append(json.dumps(entry, default=str))

    if lines:
        with open('$output_file', 'a') as f:
            f.write('\n'.join(lines) + '\n')

except Exception as e:
    pass
" 2>/dev/null && exported=$((exported + 1)) || true

done

# Update timestamp
if [[ "$DRY_RUN" == "false" && "$exported" -gt 0 ]]; then
  date +%s > "$STATE_FILE"
fi

echo "Codex session export: $exported exported, $skipped skipped"
