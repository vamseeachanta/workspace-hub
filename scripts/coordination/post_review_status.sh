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
SHA=""
EVIDENCE_URL=""

usage() {
  cat <<'USAGE'
Usage: post_review_status.sh --pr <number-or-url> --verdict <verdict> \
  --reviewer-provider <provider> --sha <reviewed-sha> --evidence-url <url> \
  [--author-provider <provider>] [--repo owner/name] [--post]

Posts the review/cross-provider commit status on a PR head SHA.
Dry-run is the default. Use --post to call the GitHub statuses API.

Status mapping:
  success: APPROVE, APPROVED, PASS, PASSED, SUCCESS, OK, MINOR
  failure: FAIL, FAILED, FAILURE, MAJOR, BLOCKING, REQUEST_CHANGES, CHANGES_REQUESTED,
           NO_OUTPUT, INVALID_OUTPUT
  pending: PENDING, RUNNING, IN_PROGRESS, UNAVAILABLE, UNKNOWN

The script refuses to post success when reviewer-provider matches author-provider.
Providers are restricted to claude, codex, and gemini. The author provider is
derived from the PR branch prefix and every commit's Co-Authored-By trailers.
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

validate_provider() {
  case "$1" in
    claude|codex|gemini)
      ;;
    *)
      die "unsupported provider: $1"
      ;;
  esac
}

provider_from_branch() {
  case "$1" in
    claude/*)
      printf 'claude'
      ;;
    codex/*)
      printf 'codex'
      ;;
    gemini/*)
      printf 'gemini'
      ;;
    *)
      die "could not derive author provider from PR branch prefix: $1"
      ;;
  esac
}

providers_from_commit_body() {
  local body provider found=()
  body="$1"

  for provider in claude codex gemini; do
    if printf '%s\n' "$body" | grep -Eiq '^Co-Authored-By: .*'"$provider"; then
      found+=("$provider")
    fi
  done

  if [[ "${#found[@]}" -gt 0 ]]; then
    printf '%s\n' "${found[@]}"
  fi
}

derive_author_provider() {
  local pr_json branch branch_provider commit_count encoded oid body providers provider
  pr_json="$1"

  branch="$(jq -r '.headRefName // ""' <<<"$pr_json")"
  [[ -n "$branch" && "$branch" != "null" ]] || die "could not resolve PR branch name"
  branch_provider="$(provider_from_branch "$branch")"

  commit_count="$(jq '.commits | length' <<<"$pr_json")"
  [[ "$commit_count" -gt 0 ]] || die "could not resolve PR commits"

  while IFS= read -r encoded; do
    oid="$(printf '%s' "$encoded" | base64 -d | jq -r '.oid // "unknown"')"
    body="$(printf '%s' "$encoded" | base64 -d | jq -r '.messageBody // ""')"
    mapfile -t providers < <(providers_from_commit_body "$body")

    if [[ "${#providers[@]}" -ne 1 ]]; then
      die "could not derive exactly one provider from Co-Authored-By trailers on commit ${oid}"
    fi

    provider="${providers[0]}"
    if [[ "$provider" != "$branch_provider" ]]; then
      die "mixed author providers: branch=${branch_provider} commit=${oid} trailer=${provider}"
    fi
  done < <(jq -r '.commits[] | @base64' <<<"$pr_json")

  printf '%s' "$branch_provider"
}

head_committed_date() {
  local pr_json head_sha committed_date
  pr_json="$1"
  head_sha="$2"

  committed_date="$(jq -r --arg sha "$head_sha" '
    ([.commits[]? | select(.oid == $sha) | .committedDate][0]
      // [.commits[]? | .committedDate][-1]
      // "")
  ' <<<"$pr_json")"
  [[ -n "$committed_date" && "$committed_date" != "null" ]] || die "could not resolve PR head committedDate"
  printf '%s' "$committed_date"
}

validate_evidence_url() {
  local pr_json evidence_url reviewer_provider expected_state head_date comment_json comment_body
  local comment_created_at verdict_re evidence_verdict evidence_state
  pr_json="$1"
  evidence_url="$2"
  reviewer_provider="$3"
  expected_state="$4"
  head_date="$5"

  comment_json="$(jq -c --arg url "$evidence_url" '
    [.comments[]? | select(.url == $url)][0] // {}
  ' <<<"$pr_json")"
  comment_body="$(jq -r '.body // ""' <<<"$comment_json")"
  comment_created_at="$(jq -r '.createdAt // ""' <<<"$comment_json")"

  [[ -n "$comment_body" ]] || die "--evidence-url must point at a comment on the same PR"
  [[ -n "$comment_created_at" && "$comment_created_at" != "null" ]] || die "--evidence-url comment is missing createdAt"
  [[ "$comment_created_at" > "$head_date" ]] || die "--evidence-url evidence comment is not later than head commit"

  if ! grep -Eiq "(^|[^[:alpha:]])${reviewer_provider}[[:space:]-]+review([^[:alpha:]]|$)" <<<"$comment_body"; then
    die "--evidence-url comment does not identify reviewer provider: ${reviewer_provider}"
  fi

  verdict_re='verdict[[:space:]]*:[[:space:]]*[*_`]*([[:alnum:]_-]+)'
  shopt -s nocasematch
  if [[ "$comment_body" =~ $verdict_re ]]; then
    evidence_verdict="${BASH_REMATCH[1]}"
  else
    shopt -u nocasematch
    die "--evidence-url comment does not contain a verdict token"
  fi
  shopt -u nocasematch

  evidence_state="$(status_from_verdict "$evidence_verdict")"
  [[ "$evidence_state" == "$expected_state" ]] \
    || die "--evidence-url verdict state ${evidence_state} does not match --verdict state ${expected_state}"
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
    --sha)
      SHA="${2:-}"
      shift 2
      ;;
    --repo)
      REPO="${2:-}"
      shift 2
      ;;
    --evidence-url)
      EVIDENCE_URL="${2:-}"
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
[[ -n "$SHA" ]] || die "--sha is required"
[[ -n "$EVIDENCE_URL" ]] || die "--evidence-url is required"

command -v gh >/dev/null 2>&1 || die "gh CLI not found"
command -v jq >/dev/null 2>&1 || die "jq not found"

STATE="$(status_from_verdict "$VERDICT")"
REVIEWER_PROVIDER="$(normalize_provider "$REVIEWER_PROVIDER")"
validate_provider "$REVIEWER_PROVIDER"

if [[ -n "$AUTHOR_PROVIDER" ]]; then
  AUTHOR_PROVIDER="$(normalize_provider "$AUTHOR_PROVIDER")"
  validate_provider "$AUTHOR_PROVIDER"
fi

if [[ -z "$REPO" ]]; then
  REPO="$(gh repo view --json nameWithOwner --jq '.nameWithOwner')"
fi

PR_JSON="$(gh pr view "$PR" --repo "$REPO" --json headRefOid,headRefName,commits,comments)"
HEAD_SHA="$(jq -r '.headRefOid // ""' <<<"$PR_JSON")"
[[ -n "$HEAD_SHA" && "$HEAD_SHA" != "null" ]] || die "could not resolve PR head SHA for ${PR}"

if [[ "$SHA" != "$HEAD_SHA" ]]; then
  die "--sha ${SHA} does not match current PR head ${HEAD_SHA}"
fi

DERIVED_AUTHOR_PROVIDER="$(derive_author_provider "$PR_JSON")"

if [[ -n "$AUTHOR_PROVIDER" && "$AUTHOR_PROVIDER" != "$DERIVED_AUTHOR_PROVIDER" ]]; then
  die "--author-provider ${AUTHOR_PROVIDER} does not match derived PR author provider ${DERIVED_AUTHOR_PROVIDER}"
fi

AUTHOR_PROVIDER="$DERIVED_AUTHOR_PROVIDER"
HEAD_COMMITTED_DATE="$(head_committed_date "$PR_JSON" "$HEAD_SHA")"
validate_evidence_url "$PR_JSON" "$EVIDENCE_URL" "$REVIEWER_PROVIDER" "$STATE" "$HEAD_COMMITTED_DATE"

if [[ "$STATE" == "success" && "$REVIEWER_PROVIDER" == "$AUTHOR_PROVIDER" ]]; then
  echo "ERROR: refusing success for same-provider review: reviewer-provider=${REVIEWER_PROVIDER} author-provider=${AUTHOR_PROVIDER}" >&2
  exit 2
fi

DESCRIPTION="${DESCRIPTION_PREFIX}: ${REVIEWER_PROVIDER} verdict ${VERDICT}"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "dry-run: would post ${CONTEXT} state=${STATE} repo=${REPO} sha=${HEAD_SHA} reviewer-provider=${REVIEWER_PROVIDER} author-provider=${AUTHOR_PROVIDER} target_url=${EVIDENCE_URL}"
  exit 0
fi

api_args=(
  "repos/${REPO}/statuses/${HEAD_SHA}"
  -f "state=${STATE}"
  -f "context=${CONTEXT}"
  -f "description=${DESCRIPTION}"
  -f "target_url=${EVIDENCE_URL}"
)

gh api "${api_args[@]}" >/dev/null

echo "posted ${CONTEXT} ${STATE} on ${REPO}@${HEAD_SHA}"
