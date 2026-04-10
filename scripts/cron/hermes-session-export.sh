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
CORRECTIONS_DIR="${OUTPUT_DIR}/corrections"
STATE_FILE="${OUTPUT_DIR}/.last-export-ts"

DRY_RUN=false
EXPORT_ALL=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --all)     EXPORT_ALL=true ;;
  esac
done

mkdir -p "$OUTPUT_DIR" "$CORRECTIONS_DIR"

if [[ "$EXPORT_ALL" == "true" && "$DRY_RUN" == "false" ]]; then
  rm -f "$OUTPUT_DIR"/session_*.jsonl "$CORRECTIONS_DIR"/session_*.jsonl "$STATE_FILE"
fi

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
  corrections_file="${CORRECTIONS_DIR}/session_${session_date}.jsonl"

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[dry-run] Would export $basename -> session_${session_date}.jsonl"
    exported=$((exported + 1))
    continue
  fi

  # Convert Hermes session JSON to orchestrator JSONL
  uv run --no-project python - "$session_file" "$output_file" "$corrections_file" <<'PY' 2>/dev/null && exported=$((exported + 1)) || true
import json, sys, os

session_file, output_file, corrections_file = sys.argv[1], sys.argv[2], sys.argv[3]

# Tool name mapping: Hermes -> Claude orchestrator convention
TOOL_MAP = {
    'terminal': 'Bash',
    'read_file': 'Read',
    'write_file': 'Write',
    'patch': 'Edit',
    'search_files': 'Grep',
    'skill_view': 'Read',
    'skill_manage': 'Write',
    'skills_list': 'ToolSearch',
    'browser_navigate': 'Browser',
    'browser_click': 'Browser',
    'browser_snapshot': 'Browser',
    'browser_type': 'Browser',
    'browser_vision': 'Browser',
    'delegate_task': 'Task',
    'execute_code': 'Bash',
    'memory': 'Write',
    'session_search': 'Grep',
    'vision_analyze': 'Read',
    'todo': 'Write',
    'clarify': 'UserInput',
    'cronjob': 'Bash',
    'process': 'Bash',
    'text_to_speech': 'Write',
}

try:
    with open(session_file) as f:
        session = json.load(f)
except Exception:
    sys.exit(0)

session_start = session.get('session_start', '')
messages = session.get('messages', [])
model = session.get('model', 'unknown')
session_id = session.get('session_id', '')

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
                'session_id': session_id,
            }
            
            # Add context-specific fields
            if name == 'terminal':
                entry['cmd'] = args.get('command', '')[:500]
            elif name in ('read_file', 'search_files'):
                entry['file'] = args.get('path', args.get('name', args.get('pattern', '')))
            elif name == 'skill_view':
                entry['file'] = args.get('name', '')
                entry['skill_name'] = args.get('name', '')
            elif name == 'skills_list':
                category = (args.get('category', '') or '').strip()
                entry['file'] = category or '__all__'
                entry['skill_category'] = category or '__all__'
            elif name == 'session_search':
                query = (args.get('query', '') or '').strip()
                entry['file'] = '__session_history__'
                entry['search_query'] = query or '__all__'
                entry['role_filter'] = args.get('role_filter', '')
                if 'limit' in args:
                    entry['limit'] = args.get('limit')
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

# Detect repeated file edits in this exported session and emit correction-style entries
correction_lines = []
recent_writes = []
for raw in lines:
    try:
        entry = json.loads(raw)
    except Exception:
        continue
    file_path = entry.get('file', '')
    if entry.get('hermes_tool') not in {'write_file', 'patch'} or not file_path:
        continue
    basename = os.path.basename(file_path)
    file_extension = os.path.splitext(basename)[1].lstrip('.') or 'none'
    is_correction = any(prev == file_path for prev in recent_writes)
    recent_writes.append(file_path)
    if not is_correction:
        continue
    correction_entry = {
        'timestamp': session_start,
        'file': file_path,
        'basename': basename,
        'tool': entry.get('tool', 'Write'),
        'correction_gap_seconds': 0,
        'diff_stat': '',
        'type': 'correction',
        'file_extension': file_extension,
        'edit_context': {
            'old_string_preview': '',
            'new_string_preview': '',
        },
        'chain_id': None,
        'chain_position': len(recent_writes),
        'chain_files': list(dict.fromkeys(recent_writes)),
        'edit_sequence_id': len(recent_writes),
    }
    correction_lines.append(json.dumps(correction_entry, default=str))

# Append to output file (multiple sessions can share a date)
if lines:
    with open(output_file, 'a') as f:
        f.write('\n'.join(lines) + '\n')
if correction_lines:
    with open(corrections_file, 'a') as f:
        f.write('\n'.join(correction_lines) + '\n')
PY

done

# Update last-export timestamp
if [[ "$DRY_RUN" == "false" && "$exported" -gt 0 ]]; then
  date +%s > "$STATE_FILE"
fi

echo "Hermes session export: $exported exported, $skipped skipped"
