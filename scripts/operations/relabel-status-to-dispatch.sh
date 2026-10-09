#!/usr/bin/env bash
# Relabel sparse status:* workflow labels to dispatch:* labels.
#
# Dry-run is the default. Pass --apply to edit issues/PRs and delete retired
# labels only after both issue and PR probes return no remaining uses.

set -euo pipefail

GH_BIN="${GH_BIN:-gh}"
OWNER="vamseeachanta"
APPLY=0

usage() {
  cat <<'USAGE'
Usage: relabel-status-to-dispatch.sh [--owner OWNER] [--apply]

Dry-run by default. With --apply, relabels issues and PRs across all
non-archived repos owned by OWNER, then deletes retired status labels only where
both issue and PR usage are zero.
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --owner)
      [ $# -ge 2 ] || { echo "--owner requires a value" >&2; exit 2; }
      OWNER="$2"
      shift 2
      ;;
    --apply)
      APPLY=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

STATUS_LABELS=(
  "status:done"
  "status:closed"
  "status:implemented"
  "status:working"
  "status:in-progress"
  "status:pending"
)

dispatch_for_status() {
  case "$1" in
    status:done|status:closed|status:implemented) printf '%s\n' "dispatch:done" ;;
    status:working|status:in-progress) printf '%s\n' "dispatch:active" ;;
    status:pending) printf '%s\n' "dispatch:ready" ;;
    *) echo "no dispatch mapping for $1" >&2; exit 2 ;;
  esac
}

dispatch_color() {
  case "$1" in
    dispatch:done) printf '%s\n' "0e8a16" ;;
    dispatch:active) printf '%s\n' "fbca04" ;;
    dispatch:ready) printf '%s\n' "1d76db" ;;
    *) echo "no color mapping for $1" >&2; exit 2 ;;
  esac
}

dispatch_description() {
  case "$1" in
    dispatch:done) printf '%s\n' "Dispatch lane completed or closed" ;;
    dispatch:active) printf '%s\n' "Dispatch lane is active" ;;
    dispatch:ready) printf '%s\n' "Dispatch lane is ready" ;;
    *) echo "no description mapping for $1" >&2; exit 2 ;;
  esac
}

run_or_print() {
  if [ "$APPLY" -eq 1 ]; then
    "$@"
  else
    printf 'DRY-RUN:'
    printf ' %q' "$@"
    printf '\n'
  fi
}

repo_list() {
  "$GH_BIN" repo list "$OWNER" \
    --no-archived \
    --limit 1000 \
    --json nameWithOwner \
    --jq '.[].nameWithOwner'
}

issue_numbers() {
  local repo="$1"
  local label="$2"
  "$GH_BIN" issue list \
    --repo "$repo" \
    --state all \
    --label "$label" \
    --limit 1000 \
    --json number \
    --jq '.[].number'
}

pr_numbers() {
  local repo="$1"
  local label="$2"
  "$GH_BIN" pr list \
    --repo "$repo" \
    --state all \
    --label "$label" \
    --limit 1000 \
    --json number \
    --jq '.[].number'
}

label_exists() {
  local repo="$1"
  local label="$2"
  "$GH_BIN" label list \
    --repo "$repo" \
    --limit 1000 \
    --json name \
    --jq '.[].name' | grep -Fx -- "$label" >/dev/null
}

ensure_dispatch_label() {
  local repo="$1"
  local label="$2"
  if label_exists "$repo" "$label"; then
    return 0
  fi
  run_or_print "$GH_BIN" label create "$label" \
    --repo "$repo" \
    --color "$(dispatch_color "$label")" \
    --description "$(dispatch_description "$label")"
}

has_any_issue_or_pr() {
  local repo="$1"
  local label="$2"
  [ -n "$(issue_numbers "$repo" "$label" | head -n 1)" ] && return 0
  [ -n "$(pr_numbers "$repo" "$label" | head -n 1)" ] && return 0
  return 1
}

if [ "$APPLY" -eq 0 ]; then
  echo "DRY-RUN mode. Pass --apply to mutate GitHub labels."
fi

while IFS= read -r repo; do
  [ -n "$repo" ] || continue
  echo "Repo: $repo"
  existing_status_labels=()

  for status_label in "${STATUS_LABELS[@]}"; do
    if ! label_exists "$repo" "$status_label"; then
      continue
    fi
    existing_status_labels+=("$status_label")
  done

  if [ "${#existing_status_labels[@]}" -eq 0 ]; then
    echo "No retired status labels found in $repo."
    continue
  fi

  for status_label in "${existing_status_labels[@]}"; do
    ensure_dispatch_label "$repo" "$(dispatch_for_status "$status_label")"
  done

  for status_label in "${existing_status_labels[@]}"; do
    dispatch_label="$(dispatch_for_status "$status_label")"

    while IFS= read -r issue; do
      [ -n "$issue" ] || continue
      run_or_print "$GH_BIN" issue edit "$issue" \
        --repo "$repo" \
        --remove-label "$status_label" \
        --add-label "$dispatch_label"
    done < <(issue_numbers "$repo" "$status_label")

    while IFS= read -r pr; do
      [ -n "$pr" ] || continue
      run_or_print "$GH_BIN" pr edit "$pr" \
        --repo "$repo" \
        --remove-label "$status_label" \
        --add-label "$dispatch_label"
    done < <(pr_numbers "$repo" "$status_label")
  done

  for status_label in "${existing_status_labels[@]}"; do
    if has_any_issue_or_pr "$repo" "$status_label"; then
      echo "Keep $status_label in $repo: still used by at least one issue or PR."
    else
      run_or_print "$GH_BIN" label delete "$status_label" --repo "$repo" --yes
    fi
  done
done < <(repo_list)
