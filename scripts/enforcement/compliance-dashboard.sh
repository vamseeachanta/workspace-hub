#!/usr/bin/env bash
# compliance-dashboard.sh — Track and report review compliance metrics
# Reads from enforcement logs, produces JSON + human-readable report
# Issues: #1876, #2017

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
LOGS_DIR="${REPO_ROOT}/logs/hooks"
REPORTS_DIR="${REPO_ROOT}/logs/compliance"

mkdir -p "$REPORTS_DIR"

# ── Parameters ──────────────────────────────────────────────────────────
WINDOW_HOURS="${COMPLIANCE_WINDOW_HOURS:-24}"
THRESHOLD="${COMPLIANCE_THRESHOLD:-80}"  # percentage

# ── Count commits in window ─────────────────────────────────────────────
get_recent_commits() {
  local since
  since="$(date -d "-${WINDOW_HOURS} hours" -Iseconds 2>/dev/null || date -v-${WINDOW_HOURS}H -Iseconds 2>/dev/null || echo "2026-04-06T00:00:00")"
  git log --since="$since" --format='%H %s' 2>/dev/null || true
}

classify_commit() {
  local msg="$1"
  local lower
  lower="$(echo "$msg" | tr '[:upper:]' '[:lower:]')"
  
  # Skip: docs, chore, test, ci, style, sync, merge, revert, build, feat(skill), feat:wiki, feat:email  
  if echo "$lower" | grep -qE '^(docs|chore|test|ci|style|sync|merge|revert|build)\('; then
    echo "skip"
    return
  fi
  if echo "$lower" | grep -qE '^feat\((skill|email|wiki)'; then
    echo "skip"
    return
  fi
  
  # Needs review: feat, fix, refactor, perf, security (excluding skip patterns above)
  if echo "$lower" | grep -qE '^(feat|fix|refactor|perf|security)\('; then
    # Additional check: is this an engineering-critical commit?
    if echo "$lower" | grep -qE 'cat:engineering|cat:data-pipeline|engineering|calculation|pipeline|orcaflex|riser|mooring|fdas'; then
      echo "engineering"
    else
      echo "feature"
    fi
    return
  fi
  
  echo "needs-review"  # default: assume needs review
}

check_commit_reviewed() {
  local hash="$1"
  local short="${hash:0:8}"
  
  # Check 1: Commit message mentions review
  git log --format='%s %b' -1 "$hash" 2>/dev/null | grep -qiE '(review|approved|codex|gemini|adversarial)' && return 0
  
  # Check 2: Related REVIEWS.md exists and is newer
  find "${REPO_ROOT}/.planning/" -name "REVIEWS.md" -newer <(git log -1 --format='%at' "$hash" | xargs -I{} date -d "@{}" -Iseconds 2>/dev/null) 2>/dev/null | xargs grep -ql "$short" 2>/dev/null && return 0
  
  return 1
}

# ── Main Analysis ───────────────────────────────────────────────────────
main() {
  local commits
  commits="$(get_recent_commits)"
  
  if [[ -z "$commits" ]]; then
    echo "{\"window_hours\":$WINDOW_HOURS,\"total_commits\":0,\"message\":\"No commits in window\"}"
    exit 0
  fi
  
  local total=0 reviewed=0 unreviewed=0 skipped=0 engineering_total=0 engineering_reviewed=0
  local unreviewed_list=""
  
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    local hash="${line%% *}"
    local msg="${line#* }"
    total=$((total + 1))
    
    local category
    category="$(classify_commit "$msg")"
    
    case "$category" in
      skip)
        skipped=$((skipped + 1))
        ;;
      engineering|feature|needs-review)
        if [[ "$category" == "engineering" ]]; then
          engineering_total=$((engineering_total + 1))
        fi
        
        if check_commit_reviewed "$hash"; then
          reviewed=$((reviewed + 1))
          if [[ "$category" == "engineering" ]]; then
            engineering_reviewed=$((engineering_reviewed + 1))
          fi
        else
          unreviewed=$((unreviewed + 1))
          local short="${hash:0:8}"
          unreviewed_list="${unreviewed_list}  - ${short} ${msg}\n"
        fi
        ;;
    esac
  done <<< "$commits"
  
  # Calculate rates
  local reviewable=$((total - skipped))
  local compliance_rate=0
  if [[ $reviewable -gt 0 ]]; then
    compliance_rate=$((reviewed * 100 / reviewable))
  fi
  
  local engineering_rate=0
  if [[ $engineering_total -gt 0 ]]; then
    engineering_rate=$((engineering_reviewed * 100 / engineering_total))
  fi
  
  # Determine verdict
  local verdict="PASS"
  if [[ $compliance_rate -lt $THRESHOLD ]]; then
    verdict="FAIL"
  fi
  
  # ── Output: Human-readable ───────────────────────────────────────────
  echo "============================================================"
  echo "Compliance Report — Last ${WINDOW_HOURS}h"
  echo "============================================================"
  echo ""
  echo "Total commits:      $total"
  echo "Skipped (docs/etc): $skipped"
  echo "Reviewable:         $reviewable"
  echo ""
  echo "Reviewed:           $reviewed"
  echo "Unreviewed:         $unreviewed"
  echo "--------------------------------------------"
  echo "Compliance rate:    ${compliance_rate}% (threshold: ${THRESHOLD}%)"
  echo "Verdict:            $verdict"
  
  if [[ $engineering_total -gt 0 ]]; then
    echo ""
    echo "Engineering commits:    $engineering_total"
    echo "Engineering reviewed:   $engineering_reviewed"
    echo "Engineering rate:       ${engineering_rate}%"
  fi
  
  if [[ $unreviewed -gt 0 ]]; then
    echo ""
    echo "Unreviewed commits:"
    echo -e "$unreviewed_list"
  fi
  
  # ── Output: Machine-readable (JSON) ─────────────────────────────────
  local report_file="${REPORTS_DIR}/compliance-$(date +%Y%m%d).json"
  
  cat <<EOF
---
JSON Report:
EOF
  
  # Create JSON (simple approach)
  local json
  json="{
  \"timestamp\": \"$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z')\",
  \"window_hours\": $WINDOW_HOURS,
  \"total_commits\": $total,
  \"skipped\": $skipped,
  \"reviewable\": $reviewable,
  \"reviewed\": $reviewed,
  \"unreviewed\": $unreviewed,
  \"compliance_rate\": $compliance_rate,
  \"threshold\": $THRESHOLD,
  \"verdict\": \"$verdict\",
  \"engineering_total\": $engineering_total,
  \"engineering_reviewed\": $engineering_reviewed,
  \"engineering_rate\": $engineering_rate
}"
  echo "$json"
  
  # Save to file
  echo "$json" > "$report_file"
  echo ""
  echo "Report saved to: $report_file"
  
  # Exit code based on verdict
  if [[ "$verdict" == "FAIL" ]]; then
    exit 1
  fi
}

main
