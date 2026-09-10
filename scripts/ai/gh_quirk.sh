#!/usr/bin/env bash
set -euo pipefail

LABEL="quirk"
LABEL_COLOR="D93F0B"
LABEL_DESCRIPTION="Time-costing undocumented behavior or ecosystem quirk"

usage() {
  cat <<'USAGE'
Usage:
  gh_quirk.sh [--dry-run] log --repo <owner/repo> --area <area> --symptom "<text>" --cause "<text>" --fix "<text>" --doc "<path-or-url>" [--session <id>]
  gh_quirk.sh [--dry-run] list [--repo <owner/repo>]
  gh_quirk.sh [--dry-run] close --repo <owner/repo> --number N --fixed-by <commit> --doc <path>

Creates/updates GitHub issues labelled "quirk". Log de-dupes by exact symptom
text against open and closed quirk issue titles and bodies in the target repo.
USAGE
}

die() {
  echo "error: $*" >&2
  exit 2
}

shell_quote() {
  printf '%q' "$1"
}

dry_run=false
if [[ "${1:-}" == "--dry-run" ]]; then
  dry_run=true
  shift
fi

cmd="${1:-}"
[[ -n "$cmd" ]] || { usage; exit 2; }
shift

run_cmd() {
  if "$dry_run"; then
    printf 'gh'
    local arg
    for arg in "$@"; do
      printf ' %s' "$(shell_quote "$arg")"
    done
    printf '\n'
  else
    gh "$@"
  fi
}

ensure_label() {
  local repo="$1"

  if "$dry_run"; then
    run_cmd label create "$LABEL" \
      --repo "$repo" \
      --description "$LABEL_DESCRIPTION" \
      --color "$LABEL_COLOR"
    return
  fi

  if ! gh label list --repo "$repo" --json name --jq '.[].name' | grep -Fxq "$LABEL"; then
    gh label create "$LABEL" \
      --repo "$repo" \
      --description "$LABEL_DESCRIPTION" \
      --color "$LABEL_COLOR" >/dev/null 2>&1 || true
  fi
}

default_session() {
  printf 'codex:%s:%s' "$(hostname -s 2>/dev/null || hostname)" "$(date -u +%Y%m%dT%H%M%SZ)"
}

quirk_body() {
  local symptom="$1" cause="$2" fix="$3" doc="$4" session="$5"

  cat <<EOF
## Symptom
$symptom

## Cause (verified or suspected)
$cause

## Fix/workaround
$fix

## Where documented (wiki page / script)
$doc

## Date
$(date -u +%F)

## Session
$session
EOF
}

close_body() {
  local fixed_by="$1" doc="$2"

  cat <<EOF
Closing quirk: fix merged in \`$fixed_by\` and documented at \`$doc\`.
EOF
}

log_quirk() {
  local repo="" area="" symptom="" cause="" fix="" doc="" session=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --repo) repo="${2:-}"; shift 2 ;;
      --area) area="${2:-}"; shift 2 ;;
      --symptom) symptom="${2:-}"; shift 2 ;;
      --cause) cause="${2:-}"; shift 2 ;;
      --fix) fix="${2:-}"; shift 2 ;;
      --doc) doc="${2:-}"; shift 2 ;;
      --session) session="${2:-}"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      *) die "unknown log argument: $1" ;;
    esac
  done

  [[ -n "$repo" ]] || die "log requires --repo"
  [[ -n "$area" ]] || die "log requires --area"
  [[ -n "$symptom" ]] || die "log requires --symptom"
  [[ -n "$cause" ]] || die "log requires --cause"
  [[ -n "$fix" ]] || die "log requires --fix"
  [[ -n "$doc" ]] || die "log requires --doc"
  [[ -n "$session" ]] || session="$(default_session)"

  local title="quirk(${area}): ${symptom}"
  local body
  body="$(quirk_body "$symptom" "$cause" "$fix" "$doc" "$session")"

  ensure_label "$repo"

  if "$dry_run"; then
    run_cmd issue list --repo "$repo" --state all --label "$LABEL" --limit 200 \
      --json number,title,body,state,url
    printf '# If an existing issue contains the symptom, comment with this body:\n'
    printf '%s\n' "$body" | sed 's/^/#   /'
    run_cmd issue comment "<number>" --repo "$repo" --body-file -
    printf '# Otherwise create this issue:\n'
    printf '%s\n' "$body" | sed 's/^/#   /'
    run_cmd issue create --repo "$repo" --title "$title" --label "$LABEL" --body-file -
    return
  fi

  local issues match
  issues="$(gh issue list --repo "$repo" --state all --label "$LABEL" --limit 200 \
    --json number,title,body,state,url)"
  match="$(jq -r --arg symptom "$symptom" '
    map(select((.title // "" | contains($symptom)) or (.body // "" | contains($symptom))))
    | sort_by(.state == "CLOSED")
    | .[0].number // empty
  ' <<<"$issues")"

  if [[ -n "$match" ]]; then
    printf '%s\n' "$body" | gh issue comment "$match" --repo "$repo" --body-file -
    gh issue view "$match" --repo "$repo" --json number,url,state --jq '"updated #\(.number) \(.state) \(.url)"'
  else
    printf '%s\n' "$body" | gh issue create --repo "$repo" --title "$title" --label "$LABEL" --body-file -
  fi
}

list_quirks() {
  local repo="vamseeachanta/workspace-hub"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --repo) repo="${2:-}"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      *) die "unknown list argument: $1" ;;
    esac
  done

  if "$dry_run"; then
    run_cmd issue list --repo "$repo" --state all --label "$LABEL" --limit 200 \
      --json number,title,state,url
    return
  fi

  gh issue list --repo "$repo" --state all --label "$LABEL" --limit 200 \
    --json number,title,state,url \
    --jq '.[] | "#\(.number) [\(.state)] \(.title) \(.url)"'
}

close_quirk() {
  local repo="" number="" fixed_by="" doc=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --repo) repo="${2:-}"; shift 2 ;;
      --number) number="${2:-}"; shift 2 ;;
      --fixed-by) fixed_by="${2:-}"; shift 2 ;;
      --doc) doc="${2:-}"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      *) die "unknown close argument: $1" ;;
    esac
  done

  [[ -n "$repo" ]] || die "close requires --repo"
  [[ -n "$number" ]] || die "close requires --number"
  [[ -n "$fixed_by" ]] || die "close requires --fixed-by"
  [[ -n "$doc" ]] || die "close requires --doc"

  local body
  body="$(close_body "$fixed_by" "$doc")"

  if "$dry_run"; then
    printf '%s\n' "$body" | sed 's/^/#   /'
    run_cmd issue comment "$number" --repo "$repo" --body-file -
    run_cmd issue close "$number" --repo "$repo" --reason completed
    return
  fi

  printf '%s\n' "$body" | gh issue comment "$number" --repo "$repo" --body-file -
  gh issue close "$number" --repo "$repo" --reason completed
}

case "$cmd" in
  log) log_quirk "$@" ;;
  list) list_quirks "$@" ;;
  close) close_quirk "$@" ;;
  -h|--help) usage ;;
  *) die "unknown command: $cmd" ;;
esac
