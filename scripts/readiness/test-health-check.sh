#!/usr/bin/env bash
# test-health-check.sh — Detect implementation commits without matching test files.
# Scans the last 7 days of git history across all submodules + hub.
# Emits JSONL to .claude/state/session-signals/test-health.jsonl (appended).
# Outputs per-repo TDD pairing rate to stdout.
# Returns 0 always — failures are logged, never fatal (best-effort readiness check).
# Called from: comprehensive-learning-nightly.sh (best-effort step)
# WRK-236
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
SIGNALS_DIR="${WORKSPACE_HUB}/.claude/state/session-signals"
JSONL_OUT="${SIGNALS_DIR}/test-health.jsonl"
RUN_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
RUN_DATE=$(date +%Y-%m-%d)

mkdir -p "$SIGNALS_DIR"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

log()  { echo "[test-health] $*"; }
warn() { echo "[test-health] WARN: $*" >&2; }

# Safe JSON string escape. Prefer python3 for correctness; fall back to sed.
_json_str() {
  if command -v python3 &>/dev/null; then
    printf '%s' "$1" \
      | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read())[1:-1])' \
      2>/dev/null || printf '%s' "$1" \
        | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\000-\037'
  else
    printf '%s' "$1" \
      | sed 's/\\/\\\\/g; s/"/\\"/g; s/'"$(printf '\t')"'/\\t/g' \
      | tr -d '\000-\037'
  fi
}

# Determine whether a changed file is an implementation file (non-test source)
# Returns 0 (true) if it qualifies.
_is_impl_file() {
  local f="$1"
  # Must be a source file by extension
  [[ "$f" =~ \.(py|ts|js|mjs|cjs|go|rs|java|rb|cpp|c|h)$ ]] || return 1
  # Must NOT itself be a test file
  [[ "$f" =~ (^|/)tests?/ ]] && return 1
  [[ "$f" =~ (^|/)spec/ ]] && return 1
  [[ "$(basename "$f")" =~ ^test_|_test\.|\.test\.|\.spec\. ]] && return 1
  return 0
}

# Determine whether a changed file is a test file. Returns 0 (true) if yes.
_is_test_file() {
  local f="$1"
  local base
  base=$(basename "$f")
  [[ "$f" =~ (^|/)tests?/ ]] && return 0
  [[ "$f" =~ (^|/)spec/ ]] && return 0
  # Prefix patterns: test_*.py, test_*.sh, test_*.cpp, test_*.c
  [[ "$base" =~ ^test_ ]] && return 0
  # Suffix patterns: *_test.py, *_test.go, *.test.ts, *.spec.ts, *Test.java
  [[ "$base" =~ _test\.(py|go|rs|rb|sh)$ ]] && return 0
  [[ "$base" =~ \.(test|spec)\.(ts|js|mjs|cjs)$ ]] && return 0
  [[ "$base" =~ Test\.(java|kt)$ ]] && return 0
  return 1
}

# For a given impl file, return a space-separated list of expected test
# file basenames (multiple patterns supported per language).
# e.g. src/foo/bar.py -> "test_bar.py bar_test.py"
_expected_test_basenames() {
  local impl="$1"
  local base stem ext
  base=$(basename "$impl")
  ext="${base##*.}"
  stem="${base%.*}"
  case "$ext" in
    py)
      echo "test_${stem}.py ${stem}_test.py"
      ;;
    ts|js|mjs|cjs)
      echo "${stem}.test.${ext} ${stem}.spec.${ext}"
      ;;
    go)
      echo "${stem}_test.go"
      ;;
    rs)
      # Rust uses inline #[cfg(test)] in the same file; flag as paired if file itself touched
      echo "${stem}.rs"
      ;;
    java|kt)
      echo "${stem}Test.${ext}"
      ;;
    rb)
      echo "${stem}_spec.rb"
      ;;
    cpp|c|h)
      echo "test_${stem}.${ext} ${stem}_test.${ext}"
      ;;
    *)
      echo "test_${stem}"
      ;;
  esac
}

# ---------------------------------------------------------------------------
# Analyse one repo directory. Populates caller-scoped arrays:
#   _impl_without_test  (impl files with no matching test touched)
#   _impl_count         (total impl files touched)
#   _test_count         (total test files touched)
# ---------------------------------------------------------------------------
_analyse_repo() {
  local repo_dir="$1"
  local repo_name
  repo_name=$(basename "$repo_dir")

  command -v git &>/dev/null || { warn "git not found — skip $repo_name"; return; }
  git -C "$repo_dir" rev-parse --git-dir &>/dev/null 2>&1 \
    || { warn "not a git repo: $repo_dir — skip"; return; }

  # Collect all files touched in the last 7 days (deduplicated)
  local changed_files
  changed_files=$(git -C "$repo_dir" log \
    --since="7 days ago" \
    --name-only \
    --format="" \
    -- 2>/dev/null \
    | grep -v "^$" | sort | uniq)

  [[ -z "$changed_files" ]] && return

  local impl_files=()
  local test_files=()

  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    if _is_test_file "$f"; then
      test_files+=("$f")
    elif _is_impl_file "$f"; then
      impl_files+=("$f")
    fi
  done <<< "$changed_files"

  _impl_count=${#impl_files[@]}
  _test_count=${#test_files[@]}
  _impl_without_test=()

  for impl in "${impl_files[@]}"; do
    local expected_list
    expected_list=$(_expected_test_basenames "$impl")
    # Check if any touched test file matches any expected basename
    local matched=0
    for expected in $expected_list; do
      for tf in "${test_files[@]}"; do
        if [[ "$(basename "$tf")" == "$expected" ]]; then
          matched=1
          break 2
        fi
      done
    done
    [[ "$matched" -eq 0 ]] && _impl_without_test+=("$impl")
  done
}

# ---------------------------------------------------------------------------
# Collect repos: hub root + all git submodules
# ---------------------------------------------------------------------------
_collect_repos() {
  echo "$WORKSPACE_HUB"
  if command -v git &>/dev/null && \
     git -C "$WORKSPACE_HUB" rev-parse --git-dir &>/dev/null 2>&1; then
    git -C "$WORKSPACE_HUB" submodule --quiet foreach \
      'echo "$displaypath"' 2>/dev/null \
      | while IFS= read -r sub; do
          [[ -n "$sub" ]] && echo "${WORKSPACE_HUB}/${sub}"
        done || true
  fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
log "Test health check — ${RUN_TS}"

total_impl=0
total_tests=0
total_unpaired=0
repos_at_risk=()
repo_count=0

declare -a _impl_without_test=()
declare -i _impl_count=0
declare -i _test_count=0

while IFS= read -r repo_dir; do
  [[ -d "$repo_dir" ]] || continue
  repo_name=$(basename "$repo_dir")

  # Reset per-repo accumulators
  _impl_without_test=()
  _impl_count=0
  _test_count=0

  _analyse_repo "$repo_dir"

  [[ "$_impl_count" -eq 0 && "$_test_count" -eq 0 ]] && continue

  repo_count=$(( repo_count + 1 ))
  total_impl=$(( total_impl + _impl_count ))
  total_tests=$(( total_tests + _test_count ))
  n_unpaired=${#_impl_without_test[@]}
  total_unpaired=$(( total_unpaired + n_unpaired ))

  # Pairing rate: (impl files that had a matching test) / total impl files * 100
  paired=$(( _impl_count - n_unpaired ))
  if [[ "$_impl_count" -gt 0 ]]; then
    pairing_pct=$(awk -v p="$paired" -v t="$_impl_count" \
      'BEGIN { printf "%.0f", (p/t)*100 }')
  else
    pairing_pct=100
  fi

  # Flag repo at risk if pairing rate < 50% and at least one impl file touched
  if [[ "$_impl_count" -gt 0 && "$pairing_pct" -lt 50 ]]; then
    repos_at_risk+=("${repo_name}:${pairing_pct}%")
  fi

  # Build unpaired list JSON fragment
  unpaired_json="[]"
  if [[ "${n_unpaired}" -gt 0 ]]; then
    parts=()
    for uf in "${_impl_without_test[@]}"; do
      parts+=('"'"$(_json_str "$uf")"'"')
    done
    joined=$(IFS=,; echo "${parts[*]}")
    unpaired_json="[${joined}]"
  fi

  log "  ${repo_name}: impl=${_impl_count} tests=${_test_count}" \
      "unpaired=${n_unpaired} pairing=${pairing_pct}%"

  # Emit JSONL record per repo
  printf '{"event":"test_health","ts":"%s","date":"%s","repo":"%s",' \
    "$(_json_str "$RUN_TS")" \
    "$(_json_str "$RUN_DATE")" \
    "$(_json_str "$repo_name")" >> "$JSONL_OUT"
  printf '"impl_files_touched":%d,"test_files_touched":%d,' \
    "$_impl_count" "$_test_count" >> "$JSONL_OUT"
  printf '"unpaired_impl_count":%d,"tdd_pairing_pct":%s,' \
    "$n_unpaired" "$pairing_pct" >> "$JSONL_OUT"
  printf '"unpaired_impl_files":%s}\n' \
    "$unpaired_json" >> "$JSONL_OUT"

done < <(_collect_repos)

# ---------------------------------------------------------------------------
# Summary JSONL record (aggregate across all repos)
# ---------------------------------------------------------------------------
if [[ "$total_impl" -gt 0 ]]; then
  overall_pairing=$(awk -v p="$((total_impl - total_unpaired))" -v t="$total_impl" \
    'BEGIN { printf "%.0f", (p/t)*100 }')
else
  overall_pairing=100
fi

at_risk_json="[]"
if [[ "${#repos_at_risk[@]}" -gt 0 ]]; then
  parts=()
  for r in "${repos_at_risk[@]}"; do
    parts+=('"'"$(_json_str "$r")"'"')
  done
  joined=$(IFS=,; echo "${parts[*]}")
  at_risk_json="[${joined}]"
fi

printf '{"event":"test_health_summary","ts":"%s","date":"%s",' \
  "$(_json_str "$RUN_TS")" \
  "$(_json_str "$RUN_DATE")" >> "$JSONL_OUT"
printf '"repos_scanned":%d,"total_impl_touched":%d,"total_test_touched":%d,' \
  "$repo_count" "$total_impl" "$total_tests" >> "$JSONL_OUT"
printf '"total_unpaired":%d,"overall_tdd_pairing_pct":%s,' \
  "$total_unpaired" "$overall_pairing" >> "$JSONL_OUT"
printf '"repos_at_risk":%s}\n' "$at_risk_json" >> "$JSONL_OUT"

# ---------------------------------------------------------------------------
# Human-readable summary
# ---------------------------------------------------------------------------
echo ""
echo "=== Test Health Summary (last 7 days) ==="
echo "  Repos scanned   : ${repo_count}"
echo "  Impl files      : ${total_impl}"
echo "  Test files      : ${total_tests}"
echo "  Unpaired impl   : ${total_unpaired}"
echo "  TDD pairing rate: ${overall_pairing}%"
if [[ "${#repos_at_risk[@]}" -gt 0 ]]; then
  echo "  Repos at risk   : ${repos_at_risk[*]}"
else
  echo "  Repos at risk   : none"
fi
echo "  JSONL output    : ${JSONL_OUT}"

log "Done."
exit 0
