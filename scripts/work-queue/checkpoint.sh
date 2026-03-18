#!/usr/bin/env bash
# checkpoint.sh [--decision "text"] [--blocker "text"] [--resolve-blocker "text"] [WRK-NNN ...]
# Writes checkpoint.yaml for context handoff with decisions/blockers tracking.
# Usage: bash scripts/work-queue/checkpoint.sh            # auto: active-wrk + all working/
#        bash scripts/work-queue/checkpoint.sh WRK-NNN   # single WRK
#        bash scripts/work-queue/checkpoint.sh --decision "chose YAML" WRK-NNN
#        bash scripts/work-queue/checkpoint.sh --blocker "waiting for API" WRK-NNN
#        bash scripts/work-queue/checkpoint.sh --resolve-blocker "waiting for API" WRK-NNN
# Resume: /wrk-resume WRK-NNN  — reads checkpoint.yaml and loads entry_reads into context
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
ACTIVE_WRK_FILE="$REPO_ROOT/.claude/state/active-wrk"
QUEUE_DIR="$REPO_ROOT/.claude/work-queue"

# ── Parse --decision / --blocker / --resolve-blocker flags ──────────────────
declare -a NEW_DECISIONS=()
declare -a NEW_BLOCKERS=()
declare -a RESOLVED_BLOCKERS=()
declare -a POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --decision)
      [[ $# -lt 2 ]] && { echo "ERROR: --decision requires a value" >&2; exit 1; }
      NEW_DECISIONS+=("$2"); shift 2 ;;
    --blocker)
      [[ $# -lt 2 ]] && { echo "ERROR: --blocker requires a value" >&2; exit 1; }
      NEW_BLOCKERS+=("$2"); shift 2 ;;
    --resolve-blocker)
      [[ $# -lt 2 ]] && { echo "ERROR: --resolve-blocker requires a value" >&2; exit 1; }
      RESOLVED_BLOCKERS+=("$2"); shift 2 ;;
    *)
      POSITIONAL_ARGS+=("$1"); shift ;;
  esac
done
set -- "${POSITIONAL_ARGS[@]+"${POSITIONAL_ARGS[@]}"}"

# ── Resolve WRK ID list ───────────────────────────────────────────────────────
declare -a WRK_IDS=()
if [[ $# -gt 0 ]]; then
  WRK_IDS=("$@")
else
  # Auto-detect: active-wrk + all items currently in working/
  [[ -f "$ACTIVE_WRK_FILE" ]] && {
    active="$(head -n1 "$ACTIVE_WRK_FILE" | tr -d '[:space:]')"
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
EXISTING_CP="$OUT_DIR/checkpoint.yaml"

# Build JSON arrays for new decisions/blockers/resolved to pass to Python
DECISIONS_JSON="[]"
if [[ ${#NEW_DECISIONS[@]} -gt 0 ]]; then
  DECISIONS_JSON=$(printf '%s\n' "${NEW_DECISIONS[@]}" | uv run --no-project python -c "
import sys, json; print(json.dumps([l.rstrip() for l in sys.stdin]))")
fi
BLOCKERS_JSON="[]"
if [[ ${#NEW_BLOCKERS[@]} -gt 0 ]]; then
  BLOCKERS_JSON=$(printf '%s\n' "${NEW_BLOCKERS[@]}" | uv run --no-project python -c "
import sys, json; print(json.dumps([l.rstrip() for l in sys.stdin]))")
fi
RESOLVED_JSON="[]"
if [[ ${#RESOLVED_BLOCKERS[@]} -gt 0 ]]; then
  RESOLVED_JSON=$(printf '%s\n' "${RESOLVED_BLOCKERS[@]}" | uv run --no-project python -c "
import sys, json; print(json.dumps([l.rstrip() for l in sys.stdin]))")
fi

export EXISTING_CP DECISIONS_JSON BLOCKERS_JSON RESOLVED_JSON NOW
export CP_WRK_ID="$WRK_ID" CP_TITLE="$WRK_TITLE"
export CP_STAGE="$CURRENT_STAGE" CP_STAGE_NAME="$STAGE_NAME"
export CP_ENTRY_READS="$ENTRY_READS"

CP_TMPFILE=$(mktemp)
uv run --no-project python - <<'PYEOF' > "$CP_TMPFILE"
import os, json, pathlib

try:
    import yaml
except ImportError:
    yaml = None

now = os.environ["NOW"]
existing_path = pathlib.Path(os.environ["EXISTING_CP"])
new_decisions_raw = json.loads(os.environ["DECISIONS_JSON"])
new_blockers_raw = json.loads(os.environ["BLOCKERS_JSON"])
resolved_raw = json.loads(os.environ["RESOLVED_JSON"])

# Timestamp new decisions
new_decisions = [f"{now}: {d}" for d in new_decisions_raw]
new_blockers = [{"text": b, "added": now, "status": "active"} for b in new_blockers_raw]

# Load existing checkpoint for merging
old_decisions = []
old_blockers = []
old_resolved = []
if existing_path.exists():
    text = existing_path.read_text()
    if yaml:
        data = yaml.safe_load(text) or {}
        old_decisions = data.get("decisions_this_session", []) or []
        old_blockers = data.get("blockers", []) or []
        old_resolved = data.get("resolved_blockers", []) or []
    else:
        # Fallback: parse decisions/blockers from YAML without PyYAML
        import re
        def parse_list_section(t, field):
            """Extract items from a YAML list field via regex."""
            m = re.search(rf'^{field}:\s*\n((?:  - .+\n(?:    .+\n)*)*)', t, re.M)
            if not m:
                return []
            items = []
            block = m.group(1)
            # Simple scalar list items: "  - value"
            for scalar in re.finditer(r'^  - "?(.+?)"?\s*$', block, re.M):
                items.append(scalar.group(1))
            return items

        def parse_dict_list(t, field):
            """Extract list-of-dicts from a YAML field."""
            m = re.search(
                rf'^{field}:\s*\n((?:  - .+\n(?:    .+\n)*)*)', t, re.M
            )
            if not m:
                return []
            items = []
            current = None
            for line in m.group(1).split("\n"):
                if re.match(r'^  - ', line):
                    if current is not None:
                        items.append(current)
                    current = {}
                    kv = re.match(r'^  - (\w+):\s*"?(.+?)"?\s*$', line)
                    if kv:
                        current[kv.group(1)] = kv.group(2)
                elif re.match(r'^    ', line) and current is not None:
                    kv = re.match(r'^    (\w+):\s*"?(.+?)"?\s*$', line)
                    if kv:
                        current[kv.group(1)] = kv.group(2)
            if current is not None:
                items.append(current)
            return items

        old_decisions = parse_list_section(text, "decisions_this_session")
        old_blockers = parse_dict_list(text, "blockers")
        old_resolved = parse_dict_list(text, "resolved_blockers")

# Merge decisions (append new)
merged_decisions = old_decisions + new_decisions

# Resolve blockers: move matching active blockers to resolved
merged_blockers = list(old_blockers)
merged_resolved = list(old_resolved)
for rt in resolved_raw:
    for b in merged_blockers[:]:
        b_text = b["text"] if isinstance(b, dict) else b
        if b_text == rt:
            entry = b if isinstance(b, dict) else {"text": b, "added": now}
            entry["status"] = "resolved"
            entry["resolved"] = now
            merged_resolved.append(entry)
            merged_blockers.remove(b)
            break

# Add new blockers
merged_blockers.extend(new_blockers)

# Build entry_reads list from the env variable
entry_reads = [
    line.strip().lstrip("- ")
    for line in os.environ["CP_ENTRY_READS"].split("\n")
    if line.strip()
]

# Build output
out = {
    "wrk_id": os.environ["CP_WRK_ID"],
    "title": os.environ["CP_TITLE"],
    "checkpointed_at": now,
    "current_stage": int(os.environ["CP_STAGE"]),
    "stage_name": os.environ["CP_STAGE_NAME"],
    "entry_reads": entry_reads,
    "decisions_this_session": merged_decisions,
    "blockers": merged_blockers,
    "resolved_blockers": merged_resolved,
    "artifacts_written": [],
    "next_action": "",
    "context_summary": [],
}

if yaml:
    print(yaml.dump(out, default_flow_style=False, sort_keys=False), end="")
else:
    # Fallback: manual YAML output
    print(f"wrk_id: {out['wrk_id']}")
    print(f'title: "{out["title"]}"')
    print(f'checkpointed_at: "{now}"')
    print(f"current_stage: {out['current_stage']}")
    print(f'stage_name: "{out["stage_name"]}"')
    print("entry_reads:")
    for e in entry_reads:
        print(f"  - {e}")
    print("decisions_this_session:")
    if merged_decisions:
        for d in merged_decisions:
            print(f'  - "{d}"')
    else:
        print("  []")
    print("blockers:")
    if merged_blockers:
        for b in merged_blockers:
            print(f"  - text: \"{b['text']}\"")
            print(f"    added: \"{b['added']}\"")
            print(f"    status: \"{b['status']}\"")
    else:
        print("  []")
    print("resolved_blockers:")
    if merged_resolved:
        for r in merged_resolved:
            print(f"  - text: \"{r['text']}\"")
            print(f"    added: \"{r['added']}\"")
            print(f"    status: \"{r['status']}\"")
            if "resolved" in r:
                print(f"    resolved: \"{r['resolved']}\"")
    else:
        print("  []")
    print("artifacts_written: []")
    print('next_action: ""')
    print("context_summary: []")
PYEOF
mv "$CP_TMPFILE" "$OUT_DIR/checkpoint.yaml"

echo "✓ $WRK_ID — $WRK_TITLE"
echo "  Stage $CURRENT_STAGE ($STAGE_NAME) · checkpoint.yaml → $OUT_DIR/checkpoint.yaml"
} # end checkpoint_one

# ── Run for each WRK ─────────────────────────────────────────────────────────
for WRK_ID in "${WRK_IDS[@]}"; do
  echo "=== Checkpointing $WRK_ID ==="
  checkpoint_one "$WRK_ID"
done
echo "Done. ${#WRK_IDS[@]} checkpoint(s) written."
