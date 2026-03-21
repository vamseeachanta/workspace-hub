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

# Post-pass: compute urgency scores for all non-archived entries
WEIGHTS_PATH="${WORKSPACE_ROOT}/config/work-queue/urgency-weights.yaml"
python3 - <<PYEOF
import json, os, re
from pathlib import Path
from datetime import datetime, timezone

idx_path = Path("${QUEUE_DIR}/wrk-status-index.json")
data = json.loads(idx_path.read_text())

# Load urgency weights
weights = {"priority": {"high": 6.0, "medium": 3.9, "low": 1.8},
           "blocking_count": 8.0, "age_factor": 2.0,
           "blocked_penalty": -5.0, "has_checkpoint": 4.0, "due_proximity": 12.0}
wp = Path("${WEIGHTS_PATH}")
if wp.is_file():
    text = wp.read_text()
    for m in re.finditer(r"^\s+(high|medium|low):\s*([\d.+-]+)", text, re.M):
        weights["priority"][m.group(1)] = float(m.group(2))
    for key in ("blocking_count", "age_factor", "blocked_penalty", "has_checkpoint", "due_proximity"):
        m = re.search(rf"^{key}:\s*([\d.+-]+)", text, re.M)
        if m:
            weights[key] = float(m.group(1))

now = datetime.now(timezone.utc)
archived_ids = {wid for wid, e in data.items() if e.get("status") == "archived"}
active_entries = {wid: e for wid, e in data.items() if e.get("status") not in ("archived", "done")}

# Pre-compute blocking_count: how many other items list this WRK in blocked_by
blocking_counts = {}
for wid, entry in active_entries.items():
    bb = entry.get("blocked_by", "")
    if not bb or bb == "[]":
        continue
    for dep in re.findall(r"WRK-\d+", bb):
        blocking_counts[dep] = blocking_counts.get(dep, 0) + 1

for wid, entry in active_entries.items():
    # Priority score
    pri = weights["priority"].get(entry.get("priority", "").lower(), 0.0)

    # Age score
    age_score = 0.0
    ca = entry.get("created_at", "")
    if ca:
        try:
            dt = datetime.strptime(ca.split(".")[0].strip(), "%Y-%m-%d").replace(tzinfo=timezone.utc)
            days = max((now - dt).days, 0)
            age_score = min(days / 30.0, 10.0) * weights["age_factor"] / 10.0
        except ValueError:
            pass

    # Blocking count score
    bc = blocking_counts.get(wid, 0) * weights["blocking_count"]

    # Blocked penalty
    bp = 0.0
    bb = entry.get("blocked_by", "")
    if bb and bb != "[]":
        for dep in re.findall(r"WRK-\d+", bb):
            if dep not in archived_ids:
                bp = weights["blocked_penalty"]
                break

    # Checkpoint bonus
    cp = weights["has_checkpoint"] if entry.get("checkpoint_stage") else 0.0

    # Due proximity (not stored in index yet, skip for now)
    total = round(pri + age_score + bc + bp + cp, 1)
    data[wid]["urgency_score"] = total

tmp = idx_path.with_suffix(".json.tmp")
tmp.write_text(json.dumps(data, indent=2))
os.replace(str(tmp), str(idx_path))
print(len(data))
PYEOF

count=$?
count=$(python3 -c "import json; print(len(json.loads(open('${QUEUE_DIR}/wrk-status-index.json').read())))")

echo "✔ Rebuilt wrk-status-index.json: ${count} entries (with urgency scores)"
