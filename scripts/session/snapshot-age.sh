#!/usr/bin/env bash
# snapshot-age.sh — Check age of session snapshot file.
# Extracts ISO8601 timestamp from "# Session Snapshot — <TS>" header.
# Exits 0 (fresh, <48h) or 1 (stale/missing/malformed). Prints age description.
# Usage: snapshot-age.sh [--snapshot-path <path>]
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
SNAPSHOT_PATH="${REPO_ROOT}/.claude/state/session-snapshot.md"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --snapshot-path) SNAPSHOT_PATH="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [[ ! -f "$SNAPSHOT_PATH" ]]; then
  echo "snapshot: missing"
  exit 1
fi

# Extract timestamp from first line: "# Session Snapshot — 2026-02-19T16:39:06Z"
FIRST_LINE=$(head -1 "$SNAPSHOT_PATH" 2>/dev/null)
TS=$(echo "$FIRST_LINE" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}' || true)

if [[ -z "$TS" ]]; then
  echo "snapshot: malformed (no ISO timestamp in header)"
  exit 1
fi

# Compute age in hours using Python (portable across Linux/macOS)
AGE_RESULT=$(uv run --no-project python - "$TS" << 'PYEOF' 2>/dev/null) || AGE_RESULT="error"
import sys
from datetime import datetime, timezone

ts_str = sys.argv[1]
# Try with and without Z suffix
for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"):
    try:
        snap_dt = datetime.strptime(ts_str, fmt).replace(tzinfo=timezone.utc)
        break
    except ValueError:
        continue
else:
    print("error")
    sys.exit(1)

now = datetime.now(timezone.utc)
age_h = (now - snap_dt).total_seconds() / 3600
print(f"{age_h:.1f}")
PYEOF

if [[ "$AGE_RESULT" == "error" ]] || [[ -z "$AGE_RESULT" ]]; then
  echo "snapshot: malformed timestamp '${TS}'"
  exit 1
fi

# Integer comparison (strip decimals)
AGE_INT=${AGE_RESULT%%.*}
if [[ $AGE_INT -lt 48 ]]; then
  echo "snapshot: ${AGE_INT}h old (fresh)"
  exit 0
else
  echo "snapshot: ${AGE_INT}h old (stale)"
  exit 1
fi
