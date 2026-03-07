#!/usr/bin/env bash
# checkpoint.sh WRK-NNN — writes checkpoint.yaml for context handoff
# Usage: bash scripts/work-queue/checkpoint.sh WRK-NNN
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
[[ $# -lt 1 ]] && { echo "Usage: checkpoint.sh WRK-NNN" >&2; exit 1; }
WRK_ID="$1"

# ── Locate WRK file ──────────────────────────────────────────────────────────
WRK_FILE=""
for dir in pending working; do
  candidate="$REPO_ROOT/.claude/work-queue/$dir/$WRK_ID.md"
  [[ -f "$candidate" ]] && WRK_FILE="$candidate" && break
done
[[ -z "$WRK_FILE" ]] && { echo "ERROR: $WRK_ID.md not found in pending/ or working/" >&2; exit 1; }

# ── Parse title + stage via single Python call ────────────────────────────────
EVIDENCE_FILE="$REPO_ROOT/.claude/work-queue/assets/$WRK_ID/evidence/stage-evidence.yaml"
export WRK_FILE EVIDENCE_FILE

IFS=$'\t' read -r CURRENT_STAGE STAGE_NAME WRK_TITLE <<< "$(uv run --no-project python - <<'PYEOF'
import re, pathlib, os
try:
    import yaml
except ImportError:
    yaml = None

wf = pathlib.Path(os.environ["WRK_FILE"]).read_text()
if yaml:
    # Parse full YAML frontmatter to get multi-line title correctly
    fm_match = re.search(r'^---\n(.+?)\n---', wf, re.DOTALL)
    fm = yaml.safe_load(fm_match.group(1)) if fm_match else {}
    title = str(fm.get("title", "")).strip()
else:
    title_m = re.search(r'^title:\s*(.+)', wf, re.MULTILINE)
    title = title_m.group(1).strip().strip('"').strip("'") if title_m else ""

ef = pathlib.Path(os.environ["EVIDENCE_FILE"])
stage, name = 1, "Capture"
if yaml and ef.exists():
    data = yaml.safe_load(ef.read_text()) or {}
    for s in data.get("stages", []):
        if str(s.get("status", "")).lower() == "done":
            stage, name = s.get("order", stage), s.get("stage", name)
print(f"{stage}\t{name}\t{title}")
PYEOF
)"

# ── Build entry_reads ─────────────────────────────────────────────────────────
WRK_DIR="pending"; [[ "$WRK_FILE" == *"/working/"* ]] && WRK_DIR="working"
RI="$REPO_ROOT/.claude/work-queue/assets/$WRK_ID/evidence/resource-intelligence.yaml"
ENTRY_READS="  - .claude/work-queue/assets/$WRK_ID/evidence/stage-evidence.yaml"
[[ -f "$RI" ]] && ENTRY_READS+=$'\n'"  - .claude/work-queue/assets/$WRK_ID/evidence/resource-intelligence.yaml"
ENTRY_READS+=$'\n'"  - .claude/work-queue/$WRK_DIR/$WRK_ID.md"

# ── Write checkpoint.yaml ─────────────────────────────────────────────────────
OUT_DIR="$REPO_ROOT/.claude/work-queue/assets/$WRK_ID"
mkdir -p "$OUT_DIR"
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cat > "$OUT_DIR/checkpoint.yaml" <<YAML
wrk_id: $WRK_ID
title: "$WRK_TITLE"
checkpointed_at: "$NOW"
current_stage: $CURRENT_STAGE
stage_name: "$STAGE_NAME"
entry_reads:
$ENTRY_READS
decisions_this_session: []
artifacts_written: []
next_action: ""
context_summary: []
YAML

echo "checkpoint.yaml written -> $OUT_DIR/checkpoint.yaml"
echo "Stage: $CURRENT_STAGE -- $STAGE_NAME"
