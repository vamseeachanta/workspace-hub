#!/usr/bin/env bash
# Relabel sparse status:* workflow labels to dispatch:* labels.
#
# Dry-run is the default. Pass --apply to edit issues/PRs and delete retired
# labels only after both issue and PR probes return no remaining uses.

set -euo pipefail

GH_BIN="${GH_BIN:-gh}"
OWNER="vamseeachanta"
APPLY=0
HAD_FAILURE=0
REPO_FAILED=0

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

dispatch_rank() {
  case "$1" in
    dispatch:ready) printf '%s\n' "1" ;;
    dispatch:active) printf '%s\n' "2" ;;
    dispatch:done) printf '%s\n' "3" ;;
    *) printf '%s\n' "0" ;;
  esac
}

run_gh_capture() {
  local stderr_file
  local output
  local rc
  stderr_file="$(mktemp)"
  set +e
  output="$("$GH_BIN" "$@" 2>"$stderr_file")"
  rc=$?
  set -e
  if [ "$rc" -eq 0 ]; then
    if [ -s "$stderr_file" ]; then
      cat "$stderr_file" >&2
    fi
    rm -f "$stderr_file"
    printf '%s\n' "$output"
    return 0
  fi
  if [ -s "$stderr_file" ]; then
    cat "$stderr_file" >&2
  else
    printf 'gh command failed with exit %s:' "$rc" >&2
    printf ' %q' "$GH_BIN" "$@" >&2
    printf '\n' >&2
  fi
  rm -f "$stderr_file"
  return "$rc"
}
record_repo_failure() {
  HAD_FAILURE=1
  REPO_FAILED=1
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
  run_gh_capture repo list "$OWNER" \
    --no-archived \
    --limit 1000 \
    --json nameWithOwner \
    --jq '.[].nameWithOwner'
}
issue_items() {
  local repo="$1"
  local label="$2"
  run_gh_capture issue list \
    --repo "$repo" \
    --state all \
    --label "$label" \
    --limit 1000 \
    --json number,labels \
    --jq '.[] | [.number, ([.labels[].name | select(startswith("dispatch:"))] | join(","))] | @tsv'
}
pr_items() {
  local repo="$1"
  local label="$2"
  run_gh_capture pr list \
    --repo "$repo" \
    --state all \
    --label "$label" \
    --limit 1000 \
    --json number,labels \
    --jq '.[] | [.number, ([.labels[].name | select(startswith("dispatch:"))] | join(","))] | @tsv'
}
label_exists() {
  local repo="$1"
  local label="$2"
  local labels
  if ! labels="$(run_gh_capture label list \
    --repo "$repo" \
    --limit 1000 \
    --json name \
    --jq '.[].name')"; then
    return 2
  fi
  grep -Fx -- "$label" <<<"$labels" >/dev/null
}
ensure_dispatch_label() {
  local repo="$1"
  local label="$2"
  local rc
  if label_exists "$repo" "$label"; then
    rc=0
  else
    rc=$?
  fi
  if [ "$rc" -eq 0 ]; then
    return 0
  fi
  if [ "$rc" -eq 2 ]; then
    return 1
  fi
  run_or_print "$GH_BIN" label create "$label" \
    --repo "$repo" \
    --color "$(dispatch_color "$label")" \
    --description "$(dispatch_description "$label")"
}
has_any_issue_or_pr() {
  local repo="$1"
  local label="$2"
  local issues
  local prs
  if ! issues="$(issue_items "$repo" "$label")"; then
    return 2
  fi
  [ -n "$(head -n 1 <<<"$issues")" ] && return 0
  if ! prs="$(pr_items "$repo" "$label")"; then
    return 2
  fi
  [ -n "$(head -n 1 <<<"$prs")" ] && return 0
  return 1
}
item_number_from_line() {
  local line="$1"
  printf '%s\n' "${line%%$'\t'*}"
}
item_dispatch_labels_from_line() {
  local line="$1"
  if [[ "$line" == *$'\t'* ]]; then
    printf '%s\n' "${line#*$'\t'}"
  else
    printf '\n'
  fi
}
final_dispatch_label() {
  local target_label="$1"
  local existing_labels="$2"
  local final_label="$target_label"
  local final_rank
  local label
  local rank
  final_rank="$(dispatch_rank "$target_label")"
  IFS=',' read -r -a labels <<<"$existing_labels"
  for label in "${labels[@]}"; do
    rank="$(dispatch_rank "$label")"
    if [ "$rank" -gt "$final_rank" ]; then
      final_label="$label"
      final_rank="$rank"
    fi
  done
  printf '%s\n' "$final_label"
}
edit_item_labels() {
  local item_type="$1"
  local number="$2"
  local repo="$3"
  local status_label="$4"
  local target_label="$5"
  local existing_labels="$6"
  local final_label
  local final_rank
  local has_final=0
  local label
  local rank
  local args
  final_label="$(final_dispatch_label "$target_label" "$existing_labels")"
  final_rank="$(dispatch_rank "$final_label")"
  args=("$GH_BIN" "$item_type" edit "$number" --repo "$repo" --remove-label "$status_label")

  IFS=',' read -r -a labels <<<"$existing_labels"
  for label in "${labels[@]}"; do
    [ -n "$label" ] || continue
    if [ "$label" = "$final_label" ]; then
      has_final=1
      continue
    fi
    rank="$(dispatch_rank "$label")"
    if [ "$rank" -gt 0 ] && [ "$rank" -lt "$final_rank" ]; then
      args+=(--remove-label "$label")
    fi
  done

  if [ "$has_final" -eq 0 ]; then
    args+=(--add-label "$final_label")
  fi

  run_or_print "${args[@]}"
}

if [ "$APPLY" -eq 0 ]; then
  echo "DRY-RUN mode. Pass --apply to mutate GitHub labels."
fi

if ! repos="$(repo_list)"; then
  exit 1
fi

while IFS= read -r repo; do
  [ -n "$repo" ] || continue
  echo "Repo: $repo"
  REPO_FAILED=0
  existing_status_labels=()

  for status_label in "${STATUS_LABELS[@]}"; do
    if label_exists "$repo" "$status_label"; then
      label_exists_rc=0
    else
      label_exists_rc=$?
    fi
    if [ "$label_exists_rc" -eq 2 ]; then
      record_repo_failure
      break
    fi
    if [ "$label_exists_rc" -ne 0 ]; then
      continue
    fi
    existing_status_labels+=("$status_label")
  done

  if [ "$REPO_FAILED" -eq 1 ]; then
    echo "Skip $repo: GitHub API failure while listing labels." >&2
    continue
  fi

  if [ "${#existing_status_labels[@]}" -eq 0 ]; then
    echo "No retired status labels found in $repo."
    continue
  fi

  for status_label in "${existing_status_labels[@]}"; do
    if ! ensure_dispatch_label "$repo" "$(dispatch_for_status "$status_label")"; then
      record_repo_failure
      break
    fi
  done

  if [ "$REPO_FAILED" -eq 1 ]; then
    echo "Skip $repo: GitHub API failure while ensuring dispatch labels." >&2
    continue
  fi

  for status_label in "${existing_status_labels[@]}"; do
    dispatch_label="$(dispatch_for_status "$status_label")"
    if ! issues="$(issue_items "$repo" "$status_label")"; then
      record_repo_failure
      break
    fi

    while IFS= read -r issue_line; do
      [ -n "$issue_line" ] || continue
      issue="$(item_number_from_line "$issue_line")"
      dispatch_labels="$(item_dispatch_labels_from_line "$issue_line")"
      if ! edit_item_labels issue "$issue" "$repo" "$status_label" "$dispatch_label" "$dispatch_labels"; then
        record_repo_failure
        break
      fi
    done <<<"$issues"

    if [ "$REPO_FAILED" -eq 1 ]; then
      break
    fi

    if ! prs="$(pr_items "$repo" "$status_label")"; then
      record_repo_failure
      break
    fi

    while IFS= read -r pr_line; do
      [ -n "$pr_line" ] || continue
      pr="$(item_number_from_line "$pr_line")"
      dispatch_labels="$(item_dispatch_labels_from_line "$pr_line")"
      if ! edit_item_labels pr "$pr" "$repo" "$status_label" "$dispatch_label" "$dispatch_labels"; then
        record_repo_failure
        break
      fi
    done <<<"$prs"
  done

  if [ "$REPO_FAILED" -eq 1 ]; then
    echo "Skip label deletion for $repo: GitHub API failure while relabeling." >&2
    continue
  fi

  for status_label in "${existing_status_labels[@]}"; do
    if has_any_issue_or_pr "$repo" "$status_label"; then
      has_any_rc=0
    else
      has_any_rc=$?
    fi
    if [ "$has_any_rc" -eq 0 ]; then
      echo "Keep $status_label in $repo: still used by at least one issue or PR."
    elif [ "$has_any_rc" -eq 2 ]; then
      record_repo_failure
      echo "Skip label deletion for $repo: GitHub API failure while checking label use." >&2
      break
    else
      if ! run_or_print "$GH_BIN" label delete "$status_label" --repo "$repo" --yes; then
        record_repo_failure
        echo "Skip remaining label deletion for $repo: GitHub API failure while deleting labels." >&2
        break
      fi
    fi
  done
done <<<"$repos"

exit "$HAD_FAILURE"
