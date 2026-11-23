#!/usr/bin/env bash
# classify-pr-failures.sh — wh#3368
# For a PR's FAILING checks, decide which are pre-existing on the base branch
# (BASELINE — not this PR's fault) vs newly red (REGRESSION — investigate).
#
# Automates the manual investigation that recurs on every merge: "is this red
# check my PR's fault, or already broken on main?" (this session proved it via
# a throwaway probe PR — #1343). One command instead.
#
# Method: pull the PR's failing check names, then the base branch's latest
# check-runs (?filter=latest) and legacy statuses; for each PR failure, look up
# the same name on the base:
#   base red      -> BASELINE    (also broken on main)
#   base green    -> REGRESSION  (green on main, red on the PR)
#   base pending  -> UNKNOWN     (main's run hasn't concluded — can't decide)
#   base absent   -> NEW         (a check the PR introduces)
#
# Limitation (conservative by design): the base state is read from the base
# branch's *latest* commit only. A path-filtered check that didn't run on that
# commit shows as NEW/UNKNOWN even if it is chronically red — so the tool may
# under-claim BASELINE, never over-claim it. It never green-lights a merge it
# cannot prove is baseline. (A future v2 could walk back N base commits for the
# last concluded run of each check name.)
#
# Usage:
#   scripts/ci_health/classify-pr-failures.sh <pr#> [--repo <owner/name>] [--base <branch>]
#
# Exit codes: 0 = every failing check is BASELINE (safe to merge past, per the
#             standing "non-required-failing" authorization); 1 = at least one
#             REGRESSION / NEW / UNKNOWN needs a look; 2 = usage/tooling error.
# Override the binary for testing: GH_BIN=/path/to/fake-gh.

set -euo pipefail

GH_BIN="${GH_BIN:-gh}"
PR=""
REPO=""
BASE=""

while (( $# > 0 )); do
  case "$1" in
    --repo=*) REPO="${1#*=}"; shift ;;
    --repo)   REPO="${2:?--repo requires a value}"; shift 2 ;;
    --base=*) BASE="${1#*=}"; shift ;;
    --base)   BASE="${2:?--base requires a value}"; shift 2 ;;
    -*)       echo "classify-pr-failures: unknown flag: $1" >&2; exit 2 ;;
    *)        if [[ -z "$PR" ]]; then PR="$1"; else echo "classify-pr-failures: unexpected arg: $1" >&2; exit 2; fi; shift ;;
  esac
done

[[ -n "$PR" ]] || { echo "usage: classify-pr-failures.sh <pr#> [--repo owner/name] [--base branch]" >&2; exit 2; }
command -v "$GH_BIN" >/dev/null 2>&1 || { echo "classify-pr-failures: '$GH_BIN' not found on PATH" >&2; exit 2; }

declare -a REPO_ARGS=()
if [[ -n "$REPO" ]]; then REPO_ARGS=(--repo "$REPO"); fi

# Resolve repo (owner/name) for the raw API calls if not supplied.
if [[ -z "$REPO" ]]; then
  REPO="$("$GH_BIN" repo view --json nameWithOwner -q .nameWithOwner)" \
    || { echo "classify-pr-failures: could not resolve repo; pass --repo owner/name" >&2; exit 2; }
fi

# Base branch: explicit, else the PR's base.
if [[ -z "$BASE" ]]; then
  BASE="$("$GH_BIN" pr view "$PR" "${REPO_ARGS[@]}" --json baseRefName -q .baseRefName)" \
    || { echo "classify-pr-failures: could not read PR #$PR base branch" >&2; exit 2; }
fi

# PR's failing check names.
mapfile -t PR_FAILURES < <(
  "$GH_BIN" pr checks "$PR" "${REPO_ARGS[@]}" --json name,state \
    -q '.[] | select(.state=="FAILURE" or .state=="ERROR") | .name'
)

if (( ${#PR_FAILURES[@]} == 0 )); then
  echo "PR #$PR ($REPO): no failing checks."
  exit 0
fi

# Base-branch state per check name. Build an associative map name->red|green|pending.
declare -A BASE_STATE=()

_red_conclusion() { case "$1" in failure|timed_out|cancelled|action_required|startup_failure|stale) return 0;; *) return 1;; esac; }
_green_conclusion() { case "$1" in success|neutral|skipped) return 0;; *) return 1;; esac; }

# check-runs (GitHub Actions), latest per name.
while IFS=$'\t' read -r name status conclusion; do
  [[ -z "$name" ]] && continue
  if [[ "$status" != "completed" ]]; then
    state="pending"
  elif _red_conclusion "$conclusion"; then
    state="red"
  elif _green_conclusion "$conclusion"; then
    state="green"
  else
    state="pending"
  fi
  # First (latest) wins; don't overwrite a decided state with a later duplicate.
  if [[ -z "${BASE_STATE[$name]:-}" ]]; then BASE_STATE["$name"]="$state"; fi
done < <(
  "$GH_BIN" api "repos/$REPO/commits/$BASE/check-runs?filter=latest" --paginate \
    -q '.check_runs[] | [.name, .status, (.conclusion // "")] | @tsv' 2>/dev/null || true
)

# Legacy commit statuses (e.g. some app contexts) — only fill gaps.
while IFS=$'\t' read -r context cstate; do
  [[ -z "$context" ]] && continue
  [[ -n "${BASE_STATE[$context]:-}" ]] && continue
  case "$cstate" in
    success) BASE_STATE["$context"]="green" ;;
    failure|error) BASE_STATE["$context"]="red" ;;
    *) BASE_STATE["$context"]="pending" ;;
  esac
done < <(
  "$GH_BIN" api "repos/$REPO/commits/$BASE/status" \
    -q '.statuses[] | [.context, .state] | @tsv' 2>/dev/null || true
)

echo "PR #$PR ($REPO) failing checks vs base '$BASE':"
n_baseline=0; n_regression=0; n_new=0; n_unknown=0
for name in "${PR_FAILURES[@]}"; do
  case "${BASE_STATE[$name]:-absent}" in
    red)     label="BASELINE  "; n_baseline=$((n_baseline + 1)) ;;
    green)   label="REGRESSION"; n_regression=$((n_regression + 1)) ;;
    pending) label="UNKNOWN   "; n_unknown=$((n_unknown + 1)) ;;
    *)       label="NEW       "; n_new=$((n_new + 1)) ;;
  esac
  printf '  %s  %s\n' "$label" "$name"
done

echo "Summary: ${n_baseline} baseline, ${n_regression} regression, ${n_new} new, ${n_unknown} unknown"
if (( n_regression == 0 && n_new == 0 && n_unknown == 0 )); then
  echo "  → all failures are pre-existing on '$BASE' (baseline-red); safe to merge past per the non-required-failing policy."
  exit 0
fi
echo "  → not all failures are baseline; investigate the regression/new/unknown checks before merging." >&2
exit 1
