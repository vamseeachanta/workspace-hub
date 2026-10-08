#!/usr/bin/env bash
# Ensure config/github/canonical-labels.tsv exists, with identical color/description,
# in every non-archived repo of an owner. Create/update only; never deletes.
# Usage: sync-canonical-labels.sh [--owner NAME] [--repo NAME] [--dry-run]
set -euo pipefail
OWNER=vamseeachanta; ONLY=""; DRY=false
while [[ $# -gt 0 ]]; do case "$1" in
  --owner) OWNER="$2"; shift 2;; --repo) ONLY="$2"; shift 2;; --dry-run) DRY=true; shift;;
  *) echo "unknown arg: $1" >&2; exit 2;; esac; done
TSV="$(git rev-parse --show-toplevel)/config/github/canonical-labels.tsv"
if [[ -n "$ONLY" ]]; then repos="$ONLY"; else
  repos=$(gh repo list "$OWNER" --limit 500 --no-archived --json name --jq '.[].name'); fi
rc=0
for r in $repos; do
  while IFS=$'\t' read -r name color desc; do
    [[ -z "$name" || "$name" == \#* ]] && continue
    if $DRY; then echo "would ensure $OWNER/$r $name"; continue; fi
    gh label create "$name" --repo "$OWNER/$r" --color "$color" --description "$desc" --force >/dev/null \
      || { echo "FAILED $OWNER/$r $name" >&2; rc=1; }
  done < "$TSV"
  $DRY || echo "ok $OWNER/$r"
done
exit $rc
