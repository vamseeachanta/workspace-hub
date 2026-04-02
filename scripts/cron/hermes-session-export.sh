#!/usr/bin/env bash
# hermes-session-export.sh — Export Hermes sessions to orchestrator JSONL format
#
# Converts ~/.hermes/sessions/*.json to logs/orchestrator/hermes/session_YYYYMMDD.jsonl
# matching the Claude orchestrator format for comprehensive-learning pipeline consumption.
#
# Usage: bash scripts/cron/hermes-session-export.sh [--dry-run] [--all]
# Cron:  Called by comprehensive-learning-nightly.sh
#
# By default, only exports sessions newer than the last export timestamp.
# Use --all to re-export everything.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="$(cd "$SCRIPT_DIR/../.." && pwd)"
HERMES_SESSIONS="${HOME}/.hermes/sessions"
OUTPUT_DIR="${WORKSPACE_HUB}/logs/orchestrator/hermes"
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

if [[ ! -d "$HERMES_SESSIONS" ]]; then
  echo "No Hermes sessions directory at $HERMES_SESSIONS — skipping"
  exit 0
fi

# Determine which sessions to export
last_ts=""
if [[ -f "$STATE_FILE" && "$EXPORT_ALL" == "false" ]]; then
  last_ts=$(cat "$STATE_FILE")
fi

exported=0
skipped=0

for session_file in "$HERMES_SESSIONS"/session_*.json; do
  [[ -f "$session_file" ]] || continue
  
  # Skip if older than last export
  if [[ -n "$last_ts" ]]; then
    file_ts=$(stat -c %Y "$session_file" 2>/dev/null || stat -f %m "$session_file" 2>/dev/null || echo 0)
    if [[ "$file_ts" -le "$last_ts" ]]; then
      skipped=$((skipped + 1))
      continue
    fi
  fi

  # Extract date from filename: session_YYYYMMDD_HHMMSS_hash.json
  basename=$(basename "$session_file" .json)
  session_date=$(echo "$basename" | grep -oE '[0-9]{8}' | head -1)
  [[ -z "$session_date" ]] && continue

  output_file="${OUTPUT_DIR}/session_${session_date}.jsonl"

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[dry-run] Would export $basename -> session_${session_date}.jsonl"
    exported=$((exported + 1))
    continue
  fi

  # Convert Hermes session JSON to orchestrator JSONL
  python3 -c "
import json, sys, os

# Tool name mapping: Hermes -> Claude orchestrator convention
TOOL_MAP = {
    'terminal': 'Bash',
    'read_file': 'Read',
    'write_file': 'Write',
    'patch': 'Edit',
    'search_files': 'Grep',
    'skill_view': 'Read',
    'skill_manage': 'Write',
    'skills_list': 'Read',
    'browser_navigate': 'Browser',
    'browser_click': 'Browser',
    'browser_snapshot': 'Browser',
    'browser_type': 'Browser',
    'browser_vision': 'Browser',
    'delegate_task': 'Task',
    'execute_code': 'Bash',
    'memory': 'Write',
    'session_search': 'Read',
    'vision_analyze': 'Read',
    'todo': 'Write',
    'clarify': 'UserInput',
    'cronjob': 'Bash',
    'process': 'Bash',
    'text_to_speech': 'Write',
}

try:
    with open('$session_file') as f:
        session = json.load(f)
except Exception:
    sys.exit(0)

session_start = session.get('session_start', '')
messages = session.get('messages', [])
model = session.get('model', 'unknown')

lines = []
for msg in messages:
    role = msg.get('role', '')
    
    if role == 'assistant':
        # Extract tool calls
        tool_calls = msg.get('tool_calls', [])
        for tc in tool_calls:
            func = tc.get('function', {})
            name = func.get('name', '')
            mapped = TOOL_MAP.get(name, name)
            
            try:
                args = json.loads(func.get('arguments', '{}'))
            except (json.JSONDecodeError, TypeError):
                args = {}
            
            entry = {
                'ts': session_start,
                'hook': 'post',
                'tool': mapped,
                'hermes_tool': name,
                'project': 'workspace-hub',
                'repo': 'workspace-hub',
                'model': model,
            }
            
            # Add context-specific fields
            if name == 'terminal':
                entry['cmd'] = args.get('command', '')[:500]
            elif name in ('read_file', 'search_files', 'skill_view'):
                entry['file'] = args.get('path', args.get('name', args.get('pattern', '')))
            elif name in ('write_file', 'patch'):
                entry['file'] = args.get('path', '')
            elif name == 'delegate_task':
                entry['task_count'] = len(args.get('tasks', [1]))
                entry['goal'] = (args.get('goal', '') or '')[:200]
            elif name == 'memory':
                entry['memory_action'] = args.get('action', '')
                entry['memory_target'] = args.get('target', '')
            elif name in ('skill_manage',):
                entry['skill_action'] = args.get('action', '')
                entry['skill_name'] = args.get('name', '')
            
            lines.append(json.dumps(entry, default=str))

# Append to output file (multiple sessions can share a date)
if lines:
    with open('$output_file', 'a') as f:
        f.write('\n'.join(lines) + '\n')
" 2>/dev/null && exported=$((exported + 1)) || true

done

# Update last-export timestamp
if [[ "$DRY_RUN" == "false" && "$exported" -gt 0 ]]; then
  date +%s > "$STATE_FILE"
fi

echo "Hermes session export: $exported exported, $skipped skipped"
