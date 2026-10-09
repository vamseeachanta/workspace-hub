#!/usr/bin/env bash
# Ensure config/github/canonical-labels.tsv exists, with identical color/description,
# in every non-archived repo of an owner. Create/update only; never deletes.
# Usage: sync-canonical-labels.sh [--owner NAME] [--repo NAME] [--apply|--dry-run]
set -euo pipefail
OWNER=vamseeachanta; ONLY=""; APPLY=false
while [[ $# -gt 0 ]]; do case "$1" in
  --owner) OWNER="$2"; shift 2;;
  --repo) ONLY="$2"; shift 2;;
  --apply) APPLY=true; shift;;
  --dry-run) APPLY=false; shift;;
  *) echo "unknown arg: $1" >&2; exit 2;; esac; done
TSV="$(git rev-parse --show-toplevel)/config/github/canonical-labels.tsv"
if [[ -n "$ONLY" ]]; then repos="$ONLY"; else
  repos=$(gh repo list "$OWNER" --limit 500 --no-archived --json name --jq '.[].name' </dev/null); fi
rc=0
for r in $repos; do
  repo="$OWNER/$r"
  repo_rc=0
  declare -A current_color=()
  declare -A current_desc=()
  if ! $APPLY; then
    if ! current=$(
      gh label list --repo "$repo" --limit 500 --json name,color,description \
        --jq '.[] | [.name,.color,.description] | @tsv' </dev/null
    ); then
      echo "FAILED $repo label list" >&2
      rc=1
      continue
    fi
    while IFS=$'\t' read -r have_name have_color have_desc; do
      [[ -z "$have_name" ]] && continue
      current_color["$have_name"]="$have_color"
      current_desc["$have_name"]="$have_desc"
    done <<< "$current"
  fi
  while IFS=$'\t' read -r name color desc; do
    [[ -z "$name" || "$name" == \#* ]] && continue
    if ! $APPLY; then
      if [[ -z "${current_color[$name]+x}" ]]; then
        printf 'would create %s %s %s %s\n' "$repo" "$name" "$color" "$desc"
      elif [[ "${current_color[$name]}" != "$color" || "${current_desc[$name]}" != "$desc" ]]; then
        printf 'would update %s %s current:%s\t%s canonical:%s\t%s\n' \
          "$repo" "$name" "${current_color[$name]}" "${current_desc[$name]}" "$color" "$desc"
      fi
      continue
    fi
    if ! gh label create "$name" --repo "$repo" --color "$color" --description "$desc" --force >/dev/null </dev/null; then
      echo "FAILED $repo $name" >&2
      repo_rc=1
    fi
  done < "$TSV"
  if [[ "$repo_rc" -eq 0 ]]; then
    echo "ok $repo"
  else
    echo "FAILED $repo" >&2
    rc=1
  fi
  unset current_color
  unset current_desc
done
exit $rc
