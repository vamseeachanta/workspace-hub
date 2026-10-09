#!/usr/bin/env bash
set -euo pipefail

CONTEXT="review/cross-provider"
DESCRIPTION_PREFIX="Cross-provider review"
DRY_RUN=1
PR=""
VERDICT=""
REVIEWER_PROVIDER=""
AUTHOR_PROVIDER=""
REPO=""
TARGET_URL=""

usage() {
  cat <<'USAGE'
Usage: post_review_status.sh --pr <number-or-url> --verdict <verdict> \
  --reviewer-provider <provider> --author-provider <provider> [--repo owner/name] \
  [--target-url <url>] [--post]

Posts the review/cross-provider commit status on a PR head SHA.
Dry-run is the default. Use --post to call the GitHub statuses API.

Status mapping:
  success: APPROVE, APPROVED, PASS, PASSED, SUCCESS, OK, MINOR
  failure: FAIL, FAILED, FAILURE, MAJOR, BLOCKING, REQUEST_CHANGES, CHANGES_REQUESTED,
           NO_OUTPUT, INVALID_OUTPUT
  pending: PENDING, RUNNING, IN_PROGRESS, UNAVAILABLE, UNKNOWN

The script refuses to post success when reviewer-provider matches author-provider.
USAGE
}

die() {
  echo "ERROR: $*" >&2
  exit 1
}

normalize_token() {
  printf '%s' "$1" | tr '[:lower:]' '[:upper:]' | tr ' -' '__'
}

normalize_provider() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]'
}

status_from_verdict() {
  local verdict
  verdict="$(normalize_token "$1")"

  case "$verdict" in
    APPROVE|APPROVED|PASS|PASSED|SUCCESS|OK|LGTM|MINOR)
      printf 'success'
      ;;
    FAIL|FAILED|FAILURE|MAJOR|CRITICAL|BLOCKING|REQUEST_CHANGES|CHANGES_REQUESTED|REJECT|REJECTED|NO_OUTPUT|INVALID_OUTPUT)
      printf 'failure'
      ;;
    PENDING|RUNNING|IN_PROGRESS|UNAVAILABLE|UNKNOWN)
      printf 'pending'
      ;;
    *)
      die "unsupported verdict: $1"
      ;;
  esac
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --pr)
      PR="${2:-}"
      shift 2
      ;;
    --verdict)
      VERDICT="${2:-}"
      shift 2
      ;;
    --reviewer-provider)
      REVIEWER_PROVIDER="${2:-}"
      shift 2
      ;;
    --author-provider)
      AUTHOR_PROVIDER="${2:-}"
      shift 2
      ;;
    --repo)
      REPO="${2:-}"
      shift 2
      ;;
    --target-url)
      TARGET_URL="${2:-}"
      shift 2
      ;;
    --post)
      DRY_RUN=0
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown argument: $1"
      ;;
  esac
done

[[ -n "$PR" ]] || die "--pr is required"
[[ -n "$VERDICT" ]] || die "--verdict is required"
[[ -n "$REVIEWER_PROVIDER" ]] || die "--reviewer-provider is required"
[[ -n "$AUTHOR_PROVIDER" ]] || die "--author-provider is required"

command -v gh >/dev/null 2>&1 || die "gh CLI not found"

STATE="$(status_from_verdict "$VERDICT")"
REVIEWER_PROVIDER="$(normalize_provider "$REVIEWER_PROVIDER")"
AUTHOR_PROVIDER="$(normalize_provider "$AUTHOR_PROVIDER")"

if [[ "$STATE" == "success" && "$REVIEWER_PROVIDER" == "$AUTHOR_PROVIDER" ]]; then
  echo "ERROR: refusing success for same-provider review: reviewer-provider=${REVIEWER_PROVIDER} author-provider=${AUTHOR_PROVIDER}" >&2
  exit 2
fi

if [[ -z "$REPO" ]]; then
  REPO="$(gh repo view --json nameWithOwner --jq '.nameWithOwner')"
fi

HEAD_SHA="$(gh pr view "$PR" --repo "$REPO" --json headRefOid --jq '.headRefOid')"
[[ -n "$HEAD_SHA" && "$HEAD_SHA" != "null" ]] || die "could not resolve PR head SHA for ${PR}"

DESCRIPTION="${DESCRIPTION_PREFIX}: ${REVIEWER_PROVIDER} verdict ${VERDICT}"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "dry-run: would post ${CONTEXT} state=${STATE} repo=${REPO} sha=${HEAD_SHA} reviewer-provider=${REVIEWER_PROVIDER} author-provider=${AUTHOR_PROVIDER}"
  exit 0
fi

api_args=(
  "repos/${REPO}/statuses/${HEAD_SHA}"
  -f "state=${STATE}"
  -f "context=${CONTEXT}"
  -f "description=${DESCRIPTION}"
)

if [[ -n "$TARGET_URL" ]]; then
  api_args+=(-f "target_url=${TARGET_URL}")
fi

gh api "${api_args[@]}" >/dev/null

echo "posted ${CONTEXT} ${STATE} on ${REPO}@${HEAD_SHA}"
