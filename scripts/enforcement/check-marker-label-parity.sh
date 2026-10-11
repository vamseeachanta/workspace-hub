#!/usr/bin/env bash
# check-marker-label-parity.sh — Reverse-direction plan-approval gate
#
# Existing forward gate (require-plan-approval.sh): "implementation commit ->
# require .planning/plan-approved/<n>.md marker present".
#
# This reverse gate enforces the OTHER half: when a marker file is ADDED or
# MODIFIED in a PR, require that the corresponding GitHub issue also carries
# the `status:plan-approved` label, set by a non-bot account. Without this,
# an agent can rationalize "user dispatched -> user approved" and write the
# marker file directly, satisfying the forward gate while bypassing the
# user-in-loop contract.
#
# Failure mode this gate prevents was observed 2026-05-14 in issue #2703 (Hermes
# lane wrote .planning/plan-approved/2703.md from execution-instruction). Captured
# in memory at feedback_dispatch_local_marker_rationalization.md. Companion to
# audit issue #2701 (forward direction: 17 labels without markers). Exit codes
# follow the convention in require-plan-approval.sh.
#
# Usage:
#   check-marker-label-parity.sh [--strict] [--base-ref REF] [--head-ref REF]
#   check-marker-label-parity.sh [--strict] --issue ISSUE [--issue ISSUE ...]
#
# Options:
#   --strict             Exit 1 on any marker-label parity failure (default).
#   --check              Advisory mode (warn but exit 0).
#   --base-ref REF       Base ref for diff (default: origin/main).
#   --head-ref REF       Head ref for diff (default: HEAD).
#   --issue ISSUE        Check a referenced issue by number.
#   --issues LIST        Check comma/space-separated issue numbers.
#
# Requires: gh CLI authenticated (GH_TOKEN in CI; local: `gh auth status`).

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
STRICT_MODE=1
BASE_REF="origin/main"
HEAD_REF="HEAD"
ISSUES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --strict) STRICT_MODE=1 ;;
    --check) STRICT_MODE=0 ;;
    --base-ref) BASE_REF="${2:-}"; shift ;;
    --base-ref=*) BASE_REF="${1#*=}" ;;
    --head-ref) HEAD_REF="${2:-}"; shift ;;
    --head-ref=*) HEAD_REF="${1#*=}" ;;
    --issue) ISSUES+=("${2:-}"); shift ;;
    --issue=*) ISSUES+=("${1#*=}") ;;
    --issues)
      read -r -a parsed_issues <<< "${2//,/ }"
      ISSUES+=("${parsed_issues[@]}")
      shift
      ;;
    --issues=*)
      issues_arg="${1#*=}"
      read -r -a parsed_issues <<< "${issues_arg//,/ }"
      ISSUES+=("${parsed_issues[@]}")
      ;;
    -h|--help) sed -n '2,30p' "$0"; exit 0 ;;
  esac
  shift || true
done

# Verify gh is available + authenticated. Without it we can't validate labels;
# fail closed in strict mode rather than green-light a possibly-bad parity.
if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh CLI not found in PATH" >&2
  [[ "$STRICT_MODE" == "1" ]] && exit 2 || exit 0
fi
if ! gh auth status >/dev/null 2>&1; then
  echo "ERROR: gh not authenticated (set GH_TOKEN or run 'gh auth login')" >&2
  [[ "$STRICT_MODE" == "1" ]] && exit 2 || exit 0
fi

REPO="${GITHUB_REPOSITORY:-}"
if [[ -z "$REPO" ]]; then
  remote_url="$(git -C "$REPO_ROOT" remote get-url origin 2>/dev/null || true)"
  if [[ "$remote_url" =~ github.com[:/]([^/]+/[^/.]+)(\.git)?$ ]]; then
    REPO="${BASH_REMATCH[1]}"
  fi
fi

if [[ -z "$REPO" ]]; then
  echo "ERROR: could not determine GitHub repository (set GITHUB_REPOSITORY)" >&2
  [[ "$STRICT_MODE" == "1" ]] && exit 2 || exit 0
fi

check_issue_label_setter() {
  local issue="$1"
  local require_label="$2"
  local labels
  local setter
  local login
  local actor_type

  labels="$(gh issue view "$issue" --repo "$REPO" --json labels 2>/dev/null \
            | python3 -c 'import json,sys; print(",".join(l["name"] for l in json.load(sys.stdin).get("labels",[])))' || echo "")"
  if ! echo "$labels" | tr ',' '\n' | grep -qx 'status:plan-approved'; then
    if [[ "$require_label" == "1" ]]; then
      echo "  FAIL: #${issue} — marker file present in PR but issue lacks status:plan-approved label"
      echo "        (labels currently: ${labels:-<none>})"
      return 1
    fi
    echo "  PASS: #${issue} — status:plan-approved label absent"
    return 0
  fi

  # Walk all timeline pages and select the most recent matching labeled event.
  # `gh api --paginate` may print one JSON array per page, so use --slurp and
  # flatten the resulting page arrays before parsing.
  setter="$(gh api "repos/${REPO}/issues/${issue}/timeline" \
            --paginate --slurp -H 'Accept: application/vnd.github.mockingbird-preview+json' 2>/dev/null \
            | python3 -c '
import json, sys

try:
    pages = json.load(sys.stdin)
except json.JSONDecodeError:
    pages = []

events = []
if isinstance(pages, list):
    for page in pages:
        if isinstance(page, list):
            events.extend(page)
        elif isinstance(page, dict):
            events.append(page)
elif isinstance(pages, dict):
    events.append(pages)

last = None
for event in events:
    if event.get("event") == "labeled" and event.get("label", {}).get("name") == "status:plan-approved":
        last = event

if last:
    actor = last.get("actor", {}) or {}
    print("{}\t{}".format(actor.get("login", ""), actor.get("type", "")))
else:
    print("\t")
' 2>/dev/null || echo $'\t')"

  login="$(echo "$setter" | cut -f1)"
  actor_type="$(echo "$setter" | cut -f2)"

  if [[ -z "$login" ]]; then
    echo "  WARN: #${issue} — could not determine label-setter from timeline (label is set, but provenance unclear)"
    return 0
  fi

  if [[ "$actor_type" == "Bot" ]] || [[ "$login" == *"[bot]" ]]; then
    echo "  FAIL: #${issue} — status:plan-approved set by bot (${login}, type=${actor_type})"
    echo "        User-in-loop contract requires a non-bot account."
    return 1
  fi

  echo "  PASS: #${issue} — status:plan-approved set by ${login} (type=${actor_type})"
  return 0
}

if [[ "${#ISSUES[@]}" -gt 0 ]]; then
  FAILURES=0
  CHECKED=0
  for issue in "${ISSUES[@]}"; do
    [[ -z "$issue" ]] && continue
    if ! [[ "$issue" =~ ^[0-9]+$ ]]; then
      echo "  SKIP: ${issue} — issue reference is not numeric"
      continue
    fi
    CHECKED=$((CHECKED+1))
    if ! check_issue_label_setter "$issue" 0; then
      FAILURES=$((FAILURES+1))
    fi
  done

  if [[ "$CHECKED" -eq 0 ]]; then
    echo "PASS: no issue references to inspect"
    exit 0
  fi

  if [[ "$FAILURES" -gt 0 ]]; then
    echo "RESULT: ${FAILURES} referenced issue label provenance failure(s)"
    [[ "$STRICT_MODE" == "1" ]] && exit 1 || exit 0
  fi

  echo "RESULT: PASS — ${CHECKED} referenced issue(s) checked"
  exit 0
fi

# Find marker files added or modified in the PR diff.
ADDED_OR_MODIFIED_MARKERS=$(
  git -C "$REPO_ROOT" diff --name-only --diff-filter=AM "${BASE_REF}...${HEAD_REF}" -- '.planning/plan-approved/*.md' 2>/dev/null || true
)

if [[ -z "$ADDED_OR_MODIFIED_MARKERS" ]]; then
  echo "PASS: no marker files added or modified in ${BASE_REF}...${HEAD_REF}"
  exit 0
fi

echo "Found marker file(s) to validate against GH labels:"
echo "$ADDED_OR_MODIFIED_MARKERS" | sed 's/^/  /'
echo

FAILURES=0

while IFS= read -r marker_path; do
  [[ -z "$marker_path" ]] && continue

  # Extract issue number from filename: .planning/plan-approved/2703.md -> 2703
  fname="$(basename "$marker_path" .md)"
  if ! [[ "$fname" =~ ^[0-9]+$ ]]; then
    echo "  SKIP: $marker_path — filename not <issue-number>.md"
    continue
  fi
  issue="$fname"

  if ! check_issue_label_setter "$issue" 1; then
    FAILURES=$((FAILURES+1))
  fi
done <<< "$ADDED_OR_MODIFIED_MARKERS"

echo
if [[ "$FAILURES" -gt 0 ]]; then
  echo "RESULT: ${FAILURES} marker-label parity failure(s)"
  if [[ "$STRICT_MODE" == "1" ]]; then
    cat >&2 <<HELP

How to fix:
  1. Confirm the issue is genuinely user-approved.
  2. Set the label as a human:
       gh issue edit <N> --repo vamseeachanta/workspace-hub \\
         --add-label status:plan-approved
  3. Re-run this check or push a new commit to re-trigger CI.

If the marker was written by an agent rationalizing a dispatch instruction
as approval, strip it instead:
  git rebase --onto <marker-commit>^ <marker-commit> <branch>
HELP
    exit 1
  fi
  exit 0
fi

echo "RESULT: PASS — all ${ADDED_OR_MODIFIED_MARKERS} marker file(s) backed by user-set labels"
exit 0
