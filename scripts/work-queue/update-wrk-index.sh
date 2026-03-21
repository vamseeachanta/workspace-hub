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
SUBCATEGORY=""
CREATED_AT=""
BLOCKED_BY=""
GH_ISSUE_REF=""
WRK_TYPE=""
NOTE=""
NOT_BEFORE=""
STANDING=""
CADENCE=""
COMPUTER=""
CHECKPOINT_STAGE=""
SESSION_PID=""
if [[ -n "$WRK_FILE" ]]; then
  TITLE=$(get_fm_field "$WRK_FILE" "title")
  PRIORITY=$(get_fm_field "$WRK_FILE" "priority")
  CATEGORY=$(get_fm_field "$WRK_FILE" "category")
  SUBCATEGORY=$(get_fm_field "$WRK_FILE" "subcategory")
  CREATED_AT=$(get_fm_field "$WRK_FILE" "created_at")
  BLOCKED_BY=$(grep -m1 "^blocked_by:" "$WRK_FILE" 2>/dev/null | sed 's/^blocked_by: *//' || true)
  GH_ISSUE_REF=$(get_fm_field "$WRK_FILE" "github_issue_ref")
  WRK_TYPE=$(get_fm_field "$WRK_FILE" "type")
  NOTE=$(get_fm_field "$WRK_FILE" "note")
  NOT_BEFORE=$(get_fm_field "$WRK_FILE" "not_before")
  STANDING=$(get_fm_field "$WRK_FILE" "standing")
  CADENCE=$(get_fm_field "$WRK_FILE" "cadence")
  COMPUTER=$(get_fm_field "$WRK_FILE" "computer")
  # Checkpoint stage from assets
  CP_FILE="${QUEUE_DIR}/assets/${WRK_ID}/checkpoint.yaml"
  [[ -f "$CP_FILE" ]] && CHECKPOINT_STAGE=$(get_fm_field "$CP_FILE" "current_stage")
  # Session PID from evidence
  LOCK_FILE="${QUEUE_DIR}/assets/${WRK_ID}/evidence/session-lock.yaml"
  [[ -f "$LOCK_FILE" ]] && SESSION_PID=$(get_fm_field "$LOCK_FILE" "session_pid")
fi

python3 - <<PYEOF
import json, os
from pathlib import Path
from datetime import datetime, timezone

idx_path = Path("${QUEUE_DIR}/wrk-status-index.json")
data = {}
if idx_path.exists():
    try:
        data = json.loads(idx_path.read_text())
    except (json.JSONDecodeError, OSError):
        data = {}

entry = {
    "status": "${STATUS}",
    "machine": "${MACHINE}",
    "last_updated": datetime.now(timezone.utc).isoformat(),
    "updated_by": "${CALLER}",
    "title": """${TITLE}""",
    "priority": "${PRIORITY}",
    "category": "${CATEGORY}",
    "subcategory": "${SUBCATEGORY}",
    "created_at": "${CREATED_AT}",
    "blocked_by": "${BLOCKED_BY}",
    "github_issue_ref": "${GH_ISSUE_REF}",
    "type": "${WRK_TYPE}",
    "note": "${NOTE}",
    "not_before": "${NOT_BEFORE}",
    "standing": "${STANDING}",
    "cadence": "${CADENCE}",
    "computer": "${COMPUTER}",
    "checkpoint_stage": "${CHECKPOINT_STAGE}",
    "session_pid": "${SESSION_PID}",
}

# Preserve urgency_score from previous index entry if present (computed by rebuild post-pass)
prev = data.get("${WRK_ID}", {})
if "urgency_score" in prev and "${CALLER}" != "rebuild-wrk-index":
    entry["urgency_score"] = prev["urgency_score"]

data["${WRK_ID}"] = entry

tmp = idx_path.with_suffix(".json.tmp")
tmp.write_text(json.dumps(data, indent=2))
os.replace(str(tmp), str(idx_path))
PYEOF

echo "✔ Updated wrk-status-index.json: ${WRK_ID} → ${STATUS}"
