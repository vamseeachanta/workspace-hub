#!/usr/bin/env bash
# require-review-on-push.sh — Pre-push hook: verify adversarial review evidence
# Enforcement Level 2 (script) per .claude/rules/patterns.md
# Called from .git/hooks/pre-push with LOCAL_OID and REMOTE_OID args
#
# Modes:
#   Default (STRICT):      blocks push (exit 1) if unreviewed commits exist
#   REVIEW_GATE_STRICT=0:  prints warning for unreviewed commits, exits 0
#   REVIEW_GATE_EVIDENCE_MODE=warn|strict:
#                          warn accepts legacy evidence until 2026-10-26 while
#                          reporting commit-bound evidence failures; strict
#                          requires commit-bound evidence for each feature commit
#   SKIP_REVIEW_GATE=1:    logs bypass and exits 0

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
TODAY="$(date +%Y-%m-%d)"
REVIEW_GATE_EVIDENCE_MODE="${REVIEW_GATE_EVIDENCE_MODE:-warn}" # warn-first per owner card O83; flip this one line to strict on or after 2026-10-26 after second-provider review.

# Tracks whether the latency timer fell back to seconds-resolution (set by _ms_now).
# Tagged into the JSONL telemetry as "_precision":"seconds" so the audit cron can
# flag degraded measurements instead of silently treating them as ms. Issue #2532.
_MS_PRECISION="ms"

# _ms_now — portable millisecond-precision timestamp.
# Prefers GNU date (CI ubuntu, most Linux dev machines), falls back to python3
# (macOS dev machines where BSD date does not support %3N), final fallback to
# seconds*1000 with a stderr warning + JSONL precision tag for the audit cron.
# Decoupled from `uv` per #2532 so the pre-push hook works on any machine.
_ms_now() {
  local _candidate
  _candidate="$(date +%s%3N 2>/dev/null)"
  if [[ "$_candidate" =~ ^[0-9]+$ ]]; then
    echo "$_candidate"
    return
  fi
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import time; print(int(time.time() * 1000))'
    return
  fi
  echo "[review-gate] warning: ms-precision timestamp unavailable (no GNU date, no python3); latency telemetry degraded to seconds resolution" >&2
  _MS_PRECISION="seconds"
  echo $(( $(date +%s) * 1000 ))
}

START_MS="$(_ms_now)"

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

# NOTE on the `[[ -n "$(...)" ]]` / here-string forms below (#2925):
# The previous `find ... | grep -q .` and `git log ... | grep -qiE ...` pipelines
# returned a FALSE NEGATIVE under this script's `set -o pipefail`. `grep -q` exits
# on its first match and closes the pipe; the upstream `find`/`git log` is then
# killed by SIGPIPE (exit 141), and pipefail propagates that 141 as the pipeline's
# status — so a check with genuine evidence read as "no evidence" and blocked the
# push. Capturing output via command substitution (find) or feeding grep with a
# here-string (git log) removes the pipe entirely, so SIGPIPE can never fire.

# Check 1: scripts/review/results/ has files from today
check_review_results() {
  local results_dir="${REPO_ROOT}/scripts/review/results"
  local file
  if [[ -d "$results_dir" ]]; then
    while IFS= read -r file; do
      [[ -z "$file" ]] && continue
      if grep -qv '^Reviewed-' "$file"; then
        return 0
      fi
    done < <(find "$results_dir" -maxdepth 2 -type f -newermt "$TODAY 00:00:00" 2>/dev/null)
  fi
  return 1
}

# Check 2: .planning/phases/*/REVIEWS.md or .planning/quick/REVIEWS.md modified today
check_planning_reviews() {
  # Phase REVIEWS.md
  if [[ -n "$(find "${REPO_ROOT}/.planning/phases/" -name "REVIEWS.md" -newermt "$TODAY 00:00:00" 2>/dev/null)" ]]; then
    return 0
  fi
  # Quick-mode REVIEWS.md
  if [[ -n "$(find "${REPO_ROOT}/.planning/quick/" -name "REVIEWS.md" -newermt "$TODAY 00:00:00" 2>/dev/null)" ]]; then
    return 0
  fi
  return 1
}

# Check 3: .claude/reports/*review* modified today
check_report_reviews() {
  if [[ -n "$(find "${REPO_ROOT}/.claude/reports/" -iname "*review*" -newermt "$TODAY 00:00:00" 2>/dev/null)" ]]; then
    return 0
  fi
  return 1
}

# Check 4: Recent git commit messages contain review keywords
check_git_evidence() {
  local recent
  recent="$(git log --oneline -30 --format='%s' 2>/dev/null || true)"
  if grep -qiE '(review|codex|gemini|adversarial)' <<< "$recent"; then
    return 0
  fi
  return 1
}

legacy_review_evidence_kind() {
  if check_review_results; then
    echo "review-results-mtime"
    return 0
  fi
  if check_planning_reviews; then
    echo "planning-review-mtime"
    return 0
  fi
  if check_report_reviews; then
    echo "report-review-mtime"
    return 0
  fi
  if check_git_evidence; then
    echo "git-subject-keyword"
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

is_evidence_only_commit() {
  local commit_hash="$1"
  local files
  files="$(git diff-tree --no-commit-id --name-only -r "$commit_hash" 2>/dev/null || true)"
  [[ -z "$files" ]] && return 1

  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    case "$file" in
      scripts/review/results/*|.planning/phases/*/REVIEWS.md|.planning/quick/REVIEWS.md|.claude/reports/*review*)
        ;;
      *)
        return 1
        ;;
    esac
  done <<< "$files"
  return 0
}

default_branch_ref() {
  local origin_head
  origin_head="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)"
  if [[ -n "$origin_head" ]] && git rev-parse --verify --quiet "${origin_head}^{commit}" >/dev/null; then
    echo "$origin_head"
    return 0
  fi
  if git rev-parse --verify --quiet "origin/main^{commit}" >/dev/null; then
    echo "origin/main"
    return 0
  fi
  return 1
}

emit_commit_lines() {
  local rev
  while IFS= read -r rev; do
    [[ -z "$rev" ]] && continue
    printf '%s %s\n' "$rev" "$(git log -1 --format='%s' "$rev" 2>/dev/null || true)"
  done
}

# --- Get commits in range ---
get_commit_list() {
  local default_ref=""
  # Exclude commits reachable from the remote default branch. origin/main is used
  # unless origin/HEAD names another default branch ref.
  if default_ref="$(default_branch_ref)"; then
    if [[ -z "$REMOTE_OID" ]] || [[ "$REMOTE_OID" == "0000000000000000000000000000000000000000" ]]; then
      git rev-list "$LOCAL_OID" --not "$default_ref" 2>/dev/null | emit_commit_lines
    else
      git rev-list "$LOCAL_OID" --not "$REMOTE_OID" "$default_ref" 2>/dev/null | emit_commit_lines
    fi
    return 0
  fi

  echo "[review-gate] DIAGNOSTIC: remote default branch ref is absent; fetch the default branch before running this gate." >&2
  if [[ "$REVIEW_GATE_EVIDENCE_MODE" == "warn" ]]; then
    echo "[review-gate] DIAGNOSTIC: REVIEW_GATE_EVIDENCE_MODE=warn falls back to the present range calculation." >&2
  else
    echo "[review-gate] BLOCKED: REVIEW_GATE_EVIDENCE_MODE=strict fails closed without the remote default branch ref." >&2
    return 2
  fi

  if [[ -z "$REMOTE_OID" ]] || [[ "$REMOTE_OID" == "0000000000000000000000000000000000000000" ]]; then
    # New branch or no remote — check last 10 commits
    git log --oneline -10 --format='%H %s' "$LOCAL_OID" 2>/dev/null
  else
    # Normal push — commits between remote and local
    git log --oneline --format='%H %s' "${REMOTE_OID}..${LOCAL_OID}" 2>/dev/null
  fi
}

validate_evidence_commit() {
  local file="$1"
  local line_no="$2"
  local field="$3"
  local value="$4"
  local display_file="${file#${REPO_ROOT}/}"
  if [[ ! "$value" =~ ^[0-9a-f]{40}$ ]]; then
    echo "[review-gate] INVALID-EVIDENCE ${display_file}:${line_no}: ${field} must be a full 40-character lowercase hexadecimal commit id." >&2
    return 1
  fi
  if ! git cat-file -e "${value}^{commit}" 2>/dev/null; then
    echo "[review-gate] INVALID-EVIDENCE ${display_file}:${line_no}: ${field} does not resolve to a commit: ${value}" >&2
    return 1
  fi
  return 0
}

load_commit_bound_evidence() {
  local result_var="$1"
  local range_var="$2"
  local valid_var="$3"
  local results_dir="${REPO_ROOT}/scripts/review/results"
  local reviewed=""
  local ranges=""
  local valid=0
  local file line_no line field value start end display_file

  if [[ -d "$results_dir" ]]; then
    while IFS= read -r file; do
      [[ -z "$file" ]] && continue
      line_no=0
      while IFS= read -r line || [[ -n "$line" ]]; do
        line_no=$((line_no + 1))
        case "$line" in
          Reviewed-Commit:*)
            field="Reviewed-Commit"
            value="${line#Reviewed-Commit: }"
            if validate_evidence_commit "$file" "$line_no" "$field" "$value"; then
              reviewed+="${value}"$'\n'
            else
              valid=1
            fi
            ;;
          Reviewed-Range:*)
            field="Reviewed-Range"
            value="${line#Reviewed-Range: }"
            display_file="${file#${REPO_ROOT}/}"
            if [[ ! "$value" =~ ^[0-9a-f]{40}\.\.[0-9a-f]{40}$ ]]; then
              echo "[review-gate] INVALID-EVIDENCE ${display_file}:${line_no}: Reviewed-Range must be '<oldest-full-commit-id>..<reviewed-full-commit-id>'." >&2
              valid=1
              continue
            fi
            start="${value%%..*}"
            end="${value#*..}"
            if validate_evidence_commit "$file" "$line_no" "Reviewed-Range start" "$start" \
              && validate_evidence_commit "$file" "$line_no" "Reviewed-Range end" "$end"; then
              ranges+="${start} ${end}"$'\n'
            else
              valid=1
            fi
            ;;
          Reviewed-*)
            display_file="${file#${REPO_ROOT}/}"
            echo "[review-gate] INVALID-EVIDENCE ${display_file}:${line_no}: malformed evidence field: ${line}" >&2
            valid=1
            ;;
        esac
      done < "$file"
    done < <(find "$results_dir" -maxdepth 2 -type f 2>/dev/null | LC_ALL=C sort)
  fi

  printf -v "$result_var" '%s' "$reviewed"
  printf -v "$range_var" '%s' "$ranges"
  printf -v "$valid_var" '%s' "$valid"
}

commit_has_bound_evidence() {
  local commit_hash="$1"
  local checked_commits="$2"
  local reviewed_commits="$3"
  local reviewed_ranges="$4"
  local line start end

  if grep -qxF "$commit_hash" <<< "$reviewed_commits"; then
    return 0
  fi

  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    start="${line%% *}"
    end="${line#* }"
    grep -qxF "$end" <<< "$checked_commits" || continue
    git merge-base --is-ancestor "$start" "$commit_hash" 2>/dev/null || continue
    git merge-base --is-ancestor "$commit_hash" "$end" 2>/dev/null || continue
    return 0
  done <<< "$reviewed_ranges"

  return 1
}

# --- Logging ---
log_latency() {
  local verdict="$1"
  local latency_dir="${REPO_ROOT}/logs/hooks"
  local latency_file="${latency_dir}/review-gate-latency.jsonl"
  mkdir -p "$latency_dir"
  local end_ms latency_ms branch timestamp precision_field
  end_ms="$(_ms_now)"
  latency_ms=$((end_ms - START_MS))
  branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
  timestamp="$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z')"
  # Tag JSONL with "_precision":"seconds" if either timer call hit the seconds-
  # resolution fallback. Audit cron can then exclude or flag those entries.
  if [[ "${_MS_PRECISION}" == "seconds" ]]; then
    precision_field=",\"_precision\":\"seconds\""
  else
    precision_field=""
  fi
  echo "{\"timestamp\":\"${timestamp}\",\"branch\":\"${branch}\",\"strict\":$( [[ \"${REVIEW_GATE_STRICT:-}\" == \"1\" ]] && echo true || echo false ),\"verdict\":\"${verdict}\",\"latency_ms\":${latency_ms}${precision_field}}" >> "$latency_file"
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

  if [[ "$REVIEW_GATE_EVIDENCE_MODE" != "warn" && "$REVIEW_GATE_EVIDENCE_MODE" != "strict" ]]; then
    echo "[review-gate] ERROR: REVIEW_GATE_EVIDENCE_MODE must be warn or strict, got '${REVIEW_GATE_EVIDENCE_MODE}'." >&2
    echo "[review-gate] BLOCKED: invalid review evidence mode."
    log_latency "blocked"
    exit 1
  fi

  # Collect commits
  local commits get_commits_rc=0
  commits="$(get_commit_list)" || get_commits_rc=$?
  if [[ "$get_commits_rc" -ne 0 ]]; then
    log_latency "blocked"
    exit 1
  fi

  if [[ -z "$commits" ]]; then
    echo "[review-gate] PASS: No commits to check."
    log_latency "pass"
    exit 0
  fi

  # Classify commits
  local feature_commits=()
  local skip_commits=()
  local total=0
  local checked_commit_ids=""

  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    local hash="${line%% *}"
    local msg="${line#* }"
    total=$((total + 1))
    checked_commit_ids+="${hash}"$'\n'

    if needs_review "$msg"; then
      if is_evidence_only_commit "$hash"; then
        skip_commits+=("$hash $msg")
      elif commit_touches_only_low_risk_paths "$hash"; then
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
  local reviewed_commits reviewed_ranges invalid_evidence
  local legacy_kind=""
  local commit_hash commit_msg
  local strict_missing=()
  local legacy_missing=()

  load_commit_bound_evidence reviewed_commits reviewed_ranges invalid_evidence

  legacy_kind="$(legacy_review_evidence_kind || true)"

  for entry in "${feature_commits[@]}"; do
    commit_hash="${entry%% *}"
    commit_msg="${entry#* }"
    if commit_has_bound_evidence "$commit_hash" "$checked_commit_ids" "$reviewed_commits" "$reviewed_ranges"; then
      reviewed=$((reviewed + 1))
      continue
    fi

    strict_missing+=("$entry")
    if [[ "$REVIEW_GATE_EVIDENCE_MODE" == "warn" && -n "$legacy_kind" ]]; then
      echo "[review-gate] WOULD-REJECT ${commit_hash} ${commit_msg}"
      echo "[review-gate] DEPRECATED legacy evidence accepted until 2026-10-26: ${legacy_kind}"
      reviewed=$((reviewed + 1))
    else
      legacy_missing+=("$entry")
    fi
  done

  if [[ "${#legacy_missing[@]}" -gt 0 ]]; then
    unreviewed=${#legacy_missing[@]}
    unreviewed_list=("${legacy_missing[@]}")
  elif [[ "$REVIEW_GATE_EVIDENCE_MODE" == "strict" && "${#strict_missing[@]}" -gt 0 ]]; then
    unreviewed=${#strict_missing[@]}
    unreviewed_list=("${strict_missing[@]}")
    reviewed=$((feature_count - unreviewed))
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
