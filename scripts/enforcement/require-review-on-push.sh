#!/usr/bin/env bash
# require-review-on-push.sh — Pre-push hook: verify adversarial review evidence
# Enforcement Level 2 (script) per .claude/rules/patterns.md
# Called from .git/hooks/pre-push with LOCAL_OID and REMOTE_OID args
#
# Modes:
#   Default (STRICT):      blocks push (exit 1) if unreviewed commits exist
#   REVIEW_GATE_STRICT=0:  prints warning for unreviewed commits, exits 0
#   SKIP_REVIEW_GATE=1:    logs bypass and exits 0

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
TODAY="$(date +%Y-%m-%d)"
START_MS="$(uv run --no-project python - <<'PY'
import time
print(int(time.time() * 1000))
PY
)"

# --- Arguments ---
LOCAL_OID="${1:-HEAD}"
REMOTE_OID="${2:-}"

# --- Classify a commit message ---
# Returns 0 if the commit needs review (feature/fix), 1 if it can be skipped
needs_review() {
  local msg="$1"
  local lower_msg
  lower_msg="$(echo "$msg" | tr '[:upper:]' '[:lower:]')"

  # Skip patterns: docs, chore, test, ci, style, sync, merge, revert, build
  if echo "$lower_msg" | grep -qE '^(docs|chore|test|ci|style|sync|merge|revert|build)(\(|:| )'; then
    return 1
  fi
  # Merge commits (auto-generated)
  if echo "$lower_msg" | grep -qE '^merge '; then
    return 1
  fi

  # Feature/fix patterns: feat, fix, refactor, perf, security
  if echo "$lower_msg" | grep -qE '^(feat|fix|refactor|perf|security)(\(|:| |!)'; then
    return 0
  fi

  # Unknown prefix — default to needing review to be safe
  return 0
}

# --- Review evidence checks ---

commit_touches_only_low_risk_paths() {
  local commit_hash="$1"
  local files
  files="$(git diff-tree --no-commit-id --name-only -r "$commit_hash" 2>/dev/null || true)"
  [[ -z "$files" ]] && return 1

  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    case "$file" in
      docs/*|*.md|*.rst|LICENSE|README*|CHANGELOG*|config/ai-tools/*|config/user-profile.yaml)
        ;;
      *)
        return 1
        ;;
    esac
  done <<< "$files"
  return 0
}

# Check 1: scripts/review/results/ has files from today
check_review_results() {
  local results_dir="${REPO_ROOT}/scripts/review/results"
  if [[ -d "$results_dir" ]]; then
    if find "$results_dir" -maxdepth 2 -type f -newermt "$TODAY 00:00:00" 2>/dev/null | grep -q .; then
      return 0
    fi
  fi
  return 1
}

# Check 2: .planning/phases/*/REVIEWS.md or .planning/quick/REVIEWS.md modified today
check_planning_reviews() {
  # Phase REVIEWS.md
  if find "${REPO_ROOT}/.planning/phases/" -name "REVIEWS.md" -newermt "$TODAY 00:00:00" 2>/dev/null | grep -q .; then
    return 0
  fi
  # Quick-mode REVIEWS.md
  if find "${REPO_ROOT}/.planning/quick/" -name "REVIEWS.md" -newermt "$TODAY 00:00:00" 2>/dev/null | grep -q .; then
    return 0
  fi
  return 1
}

# Check 3: .claude/reports/*review* modified today
check_report_reviews() {
  if find "${REPO_ROOT}/.claude/reports/" -iname "*review*" -newermt "$TODAY 00:00:00" 2>/dev/null | grep -q .; then
    return 0
  fi
  return 1
}

# Check 4: Recent git commit messages contain review keywords
check_git_evidence() {
  if git log --oneline -30 --format='%s' 2>/dev/null | grep -qiE '(review|codex|gemini|adversarial)'; then
    return 0
  fi
  return 1
}

# Run all evidence checks in order, return 0 on first hit
has_review_evidence() {
  check_review_results && return 0
  check_planning_reviews && return 0
  check_report_reviews && return 0
  check_git_evidence && return 0
  return 1
}

# --- Get commits in range ---
get_commit_list() {
  if [[ -z "$REMOTE_OID" ]] || [[ "$REMOTE_OID" == "0000000000000000000000000000000000000000" ]]; then
    # New branch or no remote — check last 10 commits
    git log --oneline -10 --format='%H %s' "$LOCAL_OID" 2>/dev/null
  else
    # Normal push — commits between remote and local
    git log --oneline --format='%H %s' "${REMOTE_OID}..${LOCAL_OID}" 2>/dev/null
  fi
}

# --- Logging ---
log_latency() {
  local verdict="$1"
  local latency_dir="${REPO_ROOT}/logs/hooks"
  local latency_file="${latency_dir}/review-gate-latency.jsonl"
  mkdir -p "$latency_dir"
  local end_ms latency_ms branch timestamp
  end_ms="$(uv run --no-project python - <<'PY'
import time
print(int(time.time() * 1000))
PY
)"
  latency_ms=$((end_ms - START_MS))
  branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
  timestamp="$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z')"
  echo "{\"timestamp\":\"${timestamp}\",\"branch\":\"${branch}\",\"strict\":$( [[ \"${REVIEW_GATE_STRICT:-}\" == \"1\" ]] && echo true || echo false ),\"verdict\":\"${verdict}\",\"latency_ms\":${latency_ms}}" >> "$latency_file"
}

log_bypass() {
  local bypass_dir="${REPO_ROOT}/logs/hooks"
  local bypass_file="${bypass_dir}/review-gate-bypass.jsonl"
  mkdir -p "$bypass_dir"
  local timestamp
  timestamp="$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z')"
  local user
  user="$(git config user.name 2>/dev/null || echo 'unknown')"
  local branch
  branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
  echo "{\"timestamp\":\"${timestamp}\",\"user\":\"${user}\",\"branch\":\"${branch}\",\"local_oid\":\"${LOCAL_OID}\",\"remote_oid\":\"${REMOTE_OID}\",\"action\":\"bypass\"}" >> "$bypass_file"
}

# --- Main ---
main() {
  # Handle skip mode early
  if [[ "${SKIP_REVIEW_GATE:-}" == "1" ]]; then
    log_bypass
    log_latency "bypass"
    echo "[review-gate] SKIP: Review gate bypassed (SKIP_REVIEW_GATE=1). Logged to logs/hooks/review-gate-bypass.jsonl"
    exit 0
  fi

  # Collect commits
  local commits
  commits="$(get_commit_list)"

  if [[ -z "$commits" ]]; then
    echo "[review-gate] PASS: No commits to check."
    log_latency "pass"
    exit 0
  fi

  # Classify commits
  local feature_commits=()
  local skip_commits=()
  local total=0

  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    local hash="${line%% *}"
    local msg="${line#* }"
    total=$((total + 1))

    if needs_review "$msg"; then
      if commit_touches_only_low_risk_paths "$hash"; then
        skip_commits+=("$hash $msg")
      else
        feature_commits+=("$hash $msg")
      fi
    else
      skip_commits+=("$hash $msg")
    fi
  done <<< "$commits"

  local feature_count=${#feature_commits[@]}
  local skip_count=${#skip_commits[@]}

  # No feature commits — all clear
  if [[ "$feature_count" -eq 0 ]]; then
    echo "[review-gate] PASS: ${total} commit(s) checked — all chore/docs/sync/low-risk-paths (no review needed)."
    log_latency "pass"
    exit 0
  fi

  # Check for review evidence
  local reviewed=0
  local unreviewed=0
  local unreviewed_list=()

  if has_review_evidence; then
    reviewed=$feature_count
  else
    unreviewed=$feature_count
    unreviewed_list=("${feature_commits[@]}")
  fi

  # Summary
  echo "[review-gate] Summary: ${feature_count} feature/fix commit(s), ${skip_count} chore/docs/sync commit(s)"
  echo "[review-gate]   Reviewed: ${reviewed}, Unreviewed: ${unreviewed}"

  # All reviewed — pass
  if [[ "$unreviewed" -eq 0 ]]; then
    echo "[review-gate] PASS: All feature/fix commits have review evidence."
    log_latency "pass"
    exit 0
  fi

  # Unreviewed commits exist
  echo ""
  echo "[review-gate] WARNING: ${unreviewed} feature/fix commit(s) without review evidence:"
  for entry in "${unreviewed_list[@]}"; do
    local short_hash="${entry%% *}"
    short_hash="${short_hash:0:8}"
    local cmsg="${entry#* }"
    echo "  - ${short_hash} ${cmsg}"
  done
  echo ""
  echo "[review-gate] To resolve, run an adversarial review before pushing:"
  echo "  /codex:adversarial-review --base main"
  echo "  /gsd:review --phase <N> --codex"
  echo ""
  echo "[review-gate] To bypass: SKIP_REVIEW_GATE=1 git push"

  # Strict mode (default as of 2026-04-09, #1839) blocks the push
  # Override with REVIEW_GATE_STRICT=0 to revert to warn mode
  if [[ "${REVIEW_GATE_STRICT:-1}" != "0" ]]; then
    echo ""
    echo "[review-gate] BLOCKED: strict mode (default) — push rejected."
    echo "[review-gate] Override: REVIEW_GATE_STRICT=0 git push"
    log_latency "blocked"
    exit 1
  fi

  # Explicit warn mode — allow push (REVIEW_GATE_STRICT=0)
  log_latency "warn"
  exit 0
}

main "$@"
