#!/usr/bin/env bash
set -euo pipefail

WRK_ID="${1:-}"
STATUS="${2:-}"

if [[ -z "$WRK_ID" || -z "$STATUS" ]]; then
  echo "Usage: update-wrk-index.sh <WRK-ID> <status> [caller]" >&2
  exit 1
fi

WORKSPACE_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
QUEUE_DIR="${WORK_QUEUE_ROOT:-${WORKSPACE_ROOT}/.claude/work-queue}"

get_fm_field() { grep -m1 "^$2:" "$1" 2>/dev/null | sed "s/^$2: *//" | tr -d '"' || true; }

WRK_FILE=""
for dir in "working" "pending" "blocked" "done"; do
  candidate="${QUEUE_DIR}/${dir}/${WRK_ID}.md"
  if [[ -f "$candidate" ]]; then
    WRK_FILE="$candidate"; break
  fi
done

# Also check archive/YYYY-MM/ subdirs
if [[ -z "$WRK_FILE" && -d "${QUEUE_DIR}/archive" ]]; then
  while IFS= read -r f; do
    WRK_FILE="$f"; break
  done < <(find "${QUEUE_DIR}/archive" -name "${WRK_ID}.md" 2>/dev/null)
fi

MACHINE=$(hostname -s 2>/dev/null || echo "unknown")
CALLER="${3:-unknown}"
TITLE=""
PRIORITY=""
CATEGORY=""
if [[ -n "$WRK_FILE" ]]; then
  TITLE=$(get_fm_field "$WRK_FILE" "title")
  PRIORITY=$(get_fm_field "$WRK_FILE" "priority")
  CATEGORY=$(get_fm_field "$WRK_FILE" "category")
fi

uv run --no-project python - <<PYEOF
import json, os, tempfile
from pathlib import Path
from datetime import datetime, timezone

idx_path = Path("${QUEUE_DIR}/wrk-status-index.json")
data = {}
if idx_path.exists():
    try:
        data = json.loads(idx_path.read_text())
    except (json.JSONDecodeError, OSError):
        data = {}

data["${WRK_ID}"] = {
    "status": "${STATUS}",
    "machine": "${MACHINE}",
    "last_updated": datetime.now(timezone.utc).isoformat(),
    "updated_by": "${CALLER}",
    "title": """${TITLE}""",
    "priority": "${PRIORITY}",
    "category": "${CATEGORY}",
}

tmp = idx_path.with_suffix(".json.tmp")
tmp.write_text(json.dumps(data, indent=2))
os.replace(str(tmp), str(idx_path))
PYEOF

echo "✔ Updated wrk-status-index.json: ${WRK_ID} → ${STATUS}"
