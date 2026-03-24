#!/usr/bin/env bash
# gh-next-id.sh — Obtain WRK ID from GitHub issue creation
#
# Creates a GitHub issue in vamseeachanta/workspace-hub and uses the returned
# issue number as the WRK ID. Falls back to LOCAL-YYYYMMDD-HHMMSS-{hostname}
# when gh CLI is unavailable or unauthenticated.
#
# Usage:
#   gh-next-id.sh --title "Fix login redirect" [--body "Details..."] [--labels "bug,high"]
#
# Output (stdout):
#   Line 1: ID (numeric or LOCAL-YYYYMMDD-HHMMSS-hostname)
#   Line 2: Issue URL (or "offline" for local fallback)
#
# Exit codes:
#   0 = success (ID allocated)
#   1 = error (missing args, API failure with no fallback)
set -euo pipefail

REPO="vamseeachanta/workspace-hub"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
BLOCKLIST="${WORKSPACE_ROOT}/config/work-queue/reserved-wrk-ids.txt"

_wrk_id_is_reserved() {
  local id_num="$1"
  if [[ -f "$BLOCKLIST" ]] && grep -qx "$id_num" "$BLOCKLIST"; then
    return 0
  fi
  local queue_dir="${WORKSPACE_ROOT}/.claude/work-queue"
  for dir in pending working done blocked archive; do
    [[ -f "${queue_dir}/${dir}/WRK-${id_num}.md" ]] && return 0
  done
  for f in "${queue_dir}/archive"/*/WRK-"${id_num}".md; do
    [[ -f "$f" ]] && return 0
  done
  [[ -d "${queue_dir}/assets/WRK-${id_num}" ]] && return 0
  return 1
}

# ── Parse arguments ──────────────────────────────────────────────────────────
TITLE=""
BODY=""
LABELS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --title)  TITLE="$2";  shift 2 ;;
    --body)   BODY="$2";   shift 2 ;;
    --labels) LABELS="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: $0 --title <title> [--body <body>] [--labels <labels>]"
      echo ""
      echo "Options:"
      echo "  --title   (required) Title for the WRK item"
      echo "  --body    (optional) Body/description for the GitHub issue"
      echo "  --labels  (optional) Comma-separated labels"
      echo ""
      echo "Output:"
      echo "  Line 1: ID (numeric GitHub issue number, or LOCAL-YYYYMMDD-HHMMSS-hostname)"
      echo "  Line 2: Issue URL (or 'offline' for local fallback)"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$TITLE" ]]; then
  echo "Error: --title is required" >&2
  exit 1
fi

# ── Attempt GitHub issue creation ────────────────────────────────────────────
_try_github() {
  # Check gh CLI is available and authenticated
  if ! command -v gh &>/dev/null; then
    >&2 echo "gh-next-id: gh CLI not found, falling back to offline ID"
    return 1
  fi

  if ! gh auth status &>/dev/null 2>&1; then
    >&2 echo "gh-next-id: gh not authenticated, falling back to offline ID"
    return 1
  fi

  # Build gh issue create command
  local gh_args=("issue" "create" "--repo" "$REPO")
  gh_args+=("--title" "WRK-PENDING: ${TITLE}")

  if [[ -n "$BODY" ]]; then
    gh_args+=("--body" "$BODY")
  else
    gh_args+=("--body" "WRK item created via gh-next-id.sh. Details will be updated.")
  fi

  if [[ -n "$LABELS" ]]; then
    gh_args+=("--label" "$LABELS")
  fi

  # Create the issue — gh issue create outputs the issue URL
  local issue_url
  issue_url=$(gh "${gh_args[@]}" 2>/dev/null) || return 1

  # Extract issue number from URL (e.g., https://github.com/.../issues/1234)
  local issue_number
  issue_number="${issue_url##*/}"

  if [[ -z "$issue_number" || ! "$issue_number" =~ ^[0-9]+$ ]]; then
    >&2 echo "gh-next-id: failed to extract issue number from URL: $issue_url"
    return 1
  fi

  # Collision avoidance: burn GH numbers that collide with existing WRK IDs
  local max_retries=200
  while _wrk_id_is_reserved "$issue_number" && (( max_retries-- > 0 )); do
    >&2 echo "gh-next-id: collision — WRK-${issue_number} exists locally, burning GH #${issue_number}"
    gh issue close "$issue_number" --repo "$REPO" \
      --comment "ID collision — WRK-${issue_number} already existed locally. Burned by gh-next-id.sh (WRK-5140)." \
      2>/dev/null || true
    issue_url=$(gh "${gh_args[@]}" 2>/dev/null) || return 1
    issue_number="${issue_url##*/}"
    if [[ -z "$issue_number" || ! "$issue_number" =~ ^[0-9]+$ ]]; then
      >&2 echo "gh-next-id: failed to extract issue number from: $issue_url"
      return 1
    fi
  done
  if _wrk_id_is_reserved "$issue_number"; then
    >&2 echo "gh-next-id: ERROR — still colliding after retries."
    return 1
  fi

  # Update issue title from WRK-PENDING to WRK-{number}
  gh issue edit "$issue_number" --repo "$REPO" \
    --title "WRK-${issue_number}: ${TITLE}" &>/dev/null || true

  # Record newly allocated ID in blocklist
  if [[ -f "$BLOCKLIST" ]]; then
    echo "$issue_number" >> "$BLOCKLIST"
  fi

  # Output: ID on line 1, URL on line 2
  echo "$issue_number"
  echo "$issue_url"
  return 0
}

# ── Offline fallback ─────────────────────────────────────────────────────────
_offline_fallback() {
  local timestamp hostname_short local_id
  timestamp="$(date -u +"%Y%m%d-%H%M%S")"
  hostname_short="${HOSTNAME:-$(hostname)}"
  # Truncate hostname to first component (e.g., "dev-primary" from "dev-primary.local")
  hostname_short="${hostname_short%%.*}"
  hostname_short=$(echo "$hostname_short" | tr -cd 'a-zA-Z0-9_-')

  local_id="LOCAL-${timestamp}-${hostname_short}"
  echo "$local_id"
  echo "offline"
}

# ── Main ─────────────────────────────────────────────────────────────────────
if _try_github; then
  exit 0
else
  _offline_fallback
  exit 0
fi
