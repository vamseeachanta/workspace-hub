#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
QUEUE_DIR="${WORK_QUEUE_ROOT:-${WORKSPACE_ROOT}/.claude/work-queue}"
UPDATER="${WORKSPACE_ROOT}/scripts/work-queue/update-wrk-index.sh"

# Fresh rebuild — clear existing index
echo '{}' > "${QUEUE_DIR}/wrk-status-index.json"

# Scan pending/, working/, blocked/
for dir in "pending" "working" "blocked"; do
  dir_path="${QUEUE_DIR}/${dir}"
  [[ -d "$dir_path" ]] || continue
  for f in "${dir_path}"/WRK-*.md; do
    [[ -f "$f" ]] || continue
    wrk_id=$(basename "$f" .md)
    status=$(grep -m1 "^status:" "$f" 2>/dev/null | sed 's/^status: *//' | tr -d '"' || echo "$dir")
    WORK_QUEUE_ROOT="$QUEUE_DIR" bash "$UPDATER" "$wrk_id" "$status" "rebuild-wrk-index" || true
  done
done

# Scan archive/YYYY-MM/ subdirs
if [[ -d "${QUEUE_DIR}/archive" ]]; then
  while IFS= read -r f; do
    [[ -f "$f" ]] || continue
    wrk_id=$(basename "$f" .md)
    WORK_QUEUE_ROOT="$QUEUE_DIR" bash "$UPDATER" "$wrk_id" "archived" "rebuild-wrk-index" || true
  done < <(find "${QUEUE_DIR}/archive" -name "WRK-*.md" 2>/dev/null | sort)
fi

# Count entries and print summary
count=$(uv run --no-project python - <<PYEOF
import json
from pathlib import Path
idx_path = Path("${QUEUE_DIR}/wrk-status-index.json")
try:
    data = json.loads(idx_path.read_text())
    print(len(data))
except Exception:
    print(0)
PYEOF
)

echo "✔ Rebuilt wrk-status-index.json: ${count} entries"
