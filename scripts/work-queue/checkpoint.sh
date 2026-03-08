#!/usr/bin/env bash
# checkpoint.sh [WRK-NNN ...] — writes checkpoint.yaml for context handoff
# Usage: bash scripts/work-queue/checkpoint.sh            # auto: active-wrk + all working/
#        bash scripts/work-queue/checkpoint.sh WRK-NNN   # single WRK
#        bash scripts/work-queue/checkpoint.sh WRK-A WRK-B  # multiple explicit
# Resume: /wrk-resume WRK-NNN  — reads checkpoint.yaml and loads entry_reads into context
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
ACTIVE_WRK_FILE="$REPO_ROOT/.claude/state/active-wrk"
QUEUE_DIR="$REPO_ROOT/.claude/work-queue"

# ── Resolve WRK ID list ───────────────────────────────────────────────────────
declare -a WRK_IDS=()
if [[ $# -gt 0 ]]; then
  WRK_IDS=("$@")
else
  # Auto-detect: active-wrk + all items currently in working/
  [[ -f "$ACTIVE_WRK_FILE" ]] && {
    active="$(cat "$ACTIVE_WRK_FILE" | tr -d '[:space:]')"
    [[ -n "$active" ]] && WRK_IDS+=("$active")
  }
  for f in "$QUEUE_DIR/working"/WRK-*.md; do
    [[ -f "$f" ]] || continue
    id="$(basename "$f" .md)"
    # Avoid duplicates
    already=0; for x in "${WRK_IDS[@]:-}"; do [[ "$x" == "$id" ]] && already=1; done
    [[ $already -eq 0 ]] && WRK_IDS+=("$id")
  done
  [[ ${#WRK_IDS[@]} -eq 0 ]] && { echo "No active WRK found. Pass WRK-NNN as argument or set active-wrk." >&2; exit 1; }
fi

checkpoint_one() {
local WRK_ID="$1"
# ── Locate WRK file ──────────────────────────────────────────────────────────
WRK_FILE=""
for dir in pending working; do
  candidate="$QUEUE_DIR/$dir/$WRK_ID.md"
  [[ -f "$candidate" ]] && WRK_FILE="$candidate" && break
done
[[ -z "$WRK_FILE" ]] && { echo "ERROR: $WRK_ID.md not found in pending/ or working/" >&2; return 1; }

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

echo "✓ $WRK_ID — $WRK_TITLE"
echo "  Stage $CURRENT_STAGE ($STAGE_NAME) · checkpoint.yaml → $OUT_DIR/checkpoint.yaml"
} # end checkpoint_one

# ── Run for each WRK ─────────────────────────────────────────────────────────
for WRK_ID in "${WRK_IDS[@]}"; do
  echo "=== Checkpointing $WRK_ID ==="
  checkpoint_one "$WRK_ID"
done
echo "Done. ${#WRK_IDS[@]} checkpoint(s) written."
