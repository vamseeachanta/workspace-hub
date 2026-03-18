#!/usr/bin/env bash
# wrk-progress.sh WRK-NNN — Show comprehensive progress for a single WRK item.
# Usage: wrk-progress.sh <WRK-NNN>
set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"
QUEUE_DIR="${QUEUE_DIR:-$REPO_ROOT/.claude/work-queue}"
[[ $# -lt 1 ]] && { echo "Usage: wrk-progress.sh <WRK-NNN>" >&2; exit 1; }
WRK_ID="$1"

# ── Locate WRK file across subdirectories ──
WRK_FILE=""
for subdir in working pending blocked done archive archived; do
  candidate="$QUEUE_DIR/$subdir/${WRK_ID}.md"
  [[ -f "$candidate" ]] && { WRK_FILE="$candidate"; break; }
  if [[ "$subdir" == "archive" || "$subdir" == "archived" ]]; then
    for mdir in "$QUEUE_DIR/$subdir"/*/; do
      [[ -f "${mdir}${WRK_ID}.md" ]] && { WRK_FILE="${mdir}${WRK_ID}.md"; break 2; }
    done
  fi
done
[[ -z "$WRK_FILE" ]] && { echo "ERROR: ${WRK_ID} not found in queue" >&2; exit 1; }

# ── Parse frontmatter ──
get_field() {
  grep -m1 "^${1}:" "$WRK_FILE" 2>/dev/null \
    | sed "s/^${1}: *//" | tr -d '"' || true
}
TITLE=$(get_field title);       STATUS=$(get_field status)
PRIORITY=$(get_field priority); COMPLEXITY=$(get_field complexity)
PERCENT=$(get_field percent_complete)
CATEGORY=$(get_field category); SUBCATEGORY=$(get_field subcategory)
COMPUTER=$(get_field computer); CREATED=$(get_field created_at)

# ── Compute age ──
AGE_DAYS=""
if [[ -n "$CREATED" ]]; then
  created_epoch=$(date -d "${CREATED%%T*}" +%s 2>/dev/null || true)
  [[ -n "$created_epoch" ]] && AGE_DAYS=$(( ($(date +%s) - created_epoch) / 86400 ))
fi

# ── Determine current stage from stage-evidence.yaml ──
EVIDENCE_DIR="$QUEUE_DIR/assets/${WRK_ID}/evidence"
STAGE_FILE="$EVIDENCE_DIR/stage-evidence.yaml"
CURRENT_STAGE=""; STAGE_NAME=""
if [[ -f "$STAGE_FILE" ]]; then
  last_done=$(grep -B1 'status: done' "$STAGE_FILE" \
    | grep 'order:' | sed 's/.*order: *//' | sort -n | tail -1 || true)
  in_prog=$(grep -B1 'status: in_progress' "$STAGE_FILE" \
    | grep 'order:' | sed 's/.*order: *//' | sort -n | tail -1 || true)
  if [[ -n "$in_prog" ]]; then
    CURRENT_STAGE="$in_prog"
    STAGE_NAME=$(grep -A1 "order: ${in_prog}$" "$STAGE_FILE" \
      | grep 'stage:' | sed 's/.*stage: *//' | head -1 || true)
  elif [[ -n "$last_done" ]]; then
    CURRENT_STAGE="$last_done"
    STAGE_NAME=$(grep -A1 "order: ${last_done}$" "$STAGE_FILE" \
      | grep 'stage:' | sed 's/.*stage: *//' | head -1 || true)
  fi
fi

# ── Header ──
printf '\n╔══════════════════════════════════════════════╗\n'
printf '║   %-42s ║\n' "${WRK_ID} Progress"
printf '╚══════════════════════════════════════════════╝\n\n'

# ── Summary fields ──
printf 'Title:      "%s"\n' "$TITLE"
printf 'Status:     %s' "$STATUS"
[[ -n "$PERCENT" ]] && printf ' (%s%%)' "$PERCENT"
printf '\n'
[[ -n "$COMPLEXITY" ]] && printf 'Route:      %s\n' "$COMPLEXITY"
if [[ -n "$CURRENT_STAGE" ]]; then
  printf 'Stage:      %s / 20' "$CURRENT_STAGE"
  [[ -n "$STAGE_NAME" ]] && printf ' — %s' "$STAGE_NAME"
  printf '\n'
fi
printf 'Priority:   %s\n' "$PRIORITY"
[[ -n "$CATEGORY" ]] && {
  printf 'Category:   %s' "$CATEGORY"
  [[ -n "$SUBCATEGORY" ]] && printf ' / %s' "$SUBCATEGORY"
  printf '\n'
}
[[ -n "$COMPUTER" ]] && printf 'Computer:   %s\n' "$COMPUTER"
if [[ -n "$CREATED" ]]; then
  printf 'Created:    %s' "${CREATED%%T*}"
  [[ -n "$AGE_DAYS" ]] && printf ' (%s days ago)' "$AGE_DAYS"
  printf '\n'
fi

# ── Evidence Status ──
EXPECTED_EVIDENCE=(
  user-review-capture.yaml resource-intelligence.yaml
  user-review-plan-draft.yaml plan-final-review.yaml
  ac-test-matrix execute.yaml gate-evidence-summary
  future-work.yaml user-review-close.yaml cost-summary.yaml
)
printf '\n── Evidence Status ──\n'
for ev in "${EXPECTED_EVIDENCE[@]}"; do
  found=false
  for f in "$EVIDENCE_DIR/${ev}" "$EVIDENCE_DIR/${ev}.yaml" \
           "$EVIDENCE_DIR/${ev}.md" "$EVIDENCE_DIR/${ev}.json"; do
    [[ -f "$f" ]] && { found=true; break; }
  done
  $found && printf '  ✔ %s\n' "$ev" || printf '  ✗ %s\n' "$ev"
done

# ── Checkpoint ──
CHECKPOINT="$QUEUE_DIR/assets/${WRK_ID}/checkpoint.yaml"
if [[ -f "$CHECKPOINT" ]]; then
  printf '\n── Checkpoint ──\n'
  updated=$(grep -m1 '^updated_at:' "$CHECKPOINT" | sed 's/^updated_at: *//' | tr -d '"' || true)
  [[ -n "$updated" ]] && printf '  Last checkpoint: %s\n' "$updated"
  next_action=$(grep -m1 '^next_action:' "$CHECKPOINT" | sed 's/^next_action: *//' | tr -d '"' || true)
  if [[ "$next_action" == ">" || -z "$next_action" ]]; then
    next_action=$(sed -n '/^next_action:/,/^[a-z_]*:/{ /^next_action:/d; /^[a-z_]*:/d; p; }' \
      "$CHECKPOINT" | head -1 | sed 's/^ *//' || true)
  fi
  [[ -n "$next_action" ]] && printf '  Next action: "%s"\n' "$next_action"
  decisions=$(sed -n '/^decisions:/,/^[a-z_]*:/{/^decisions:/d; /^[a-z_]*:/d; p;}' \
    "$CHECKPOINT" | grep 'text:' | sed 's/.*text: *//' | tr -d '"' || true)
  if [[ -n "$decisions" ]]; then
    printf '  Decisions:\n'
    while IFS= read -r dec; do
      [[ -n "$dec" ]] && printf '    - %s\n' "$dec"
    done <<< "$decisions"
  fi
  blockers_line=$(grep -m1 '^blockers:' "$CHECKPOINT" | sed 's/^blockers: *//' || true)
  if [[ "$blockers_line" == "[]" || -z "$blockers_line" ]]; then
    printf '  Blockers: none\n'
  else
    printf '  Blockers: %s\n' "$blockers_line"
  fi
fi

# ── Urgency Score (best-effort) ──
URGENCY_SCRIPT="$REPO_ROOT/scripts/work-queue/urgency_score.py"
if [[ -f "$URGENCY_SCRIPT" ]]; then
  urgency_out=$(uv run --no-project python "$URGENCY_SCRIPT" "$WRK_ID" 2>/dev/null || true)
  if [[ -n "$urgency_out" ]]; then
    printf '\n── Urgency Score ──\n'
    printf '  %s\n' "$urgency_out"
  fi
fi
printf '\n'
