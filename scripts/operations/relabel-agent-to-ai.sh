#!/usr/bin/env bash
set -euo pipefail

OWNER="${OWNER:-vamseeachanta}"
APPLY=false

usage() {
  cat <<'USAGE'
Usage: scripts/operations/relabel-agent-to-ai.sh [--apply]

Dry-run by default. With --apply, add ai:<provider> and remove agent:<provider>
on every issue and PR across the owner's non-archived repositories.
agent:gemini maps to ai:agy.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)
      APPLY=true
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
  shift
done

ai_label_for_agent() {
  case "$1" in
    agent:claude) printf '%s\n' "ai:claude" ;;
    agent:codex) printf '%s\n' "ai:codex" ;;
    agent:gemini) printf '%s\n' "ai:agy" ;;
    agent:hermes) printf '%s\n' "ai:hermes" ;;
    agent:agy) printf '%s\n' "ai:agy" ;;
    *) return 1 ;;
  esac
}

repo_has_target_label() {
  local label="$1"
  grep -Fxq "$label" <<<"$REPO_LABELS"
}

agent_labels_from_item() {
  local encoded="$1"
  ENCODED_ITEM="$encoded" python - <<'PY'
import base64
import json
import os

item = json.loads(base64.b64decode(os.environ["ENCODED_ITEM"]).decode("utf-8"))
for label in item.get("labels", []):
    name = label.get("name") if isinstance(label, dict) else label
    if isinstance(name, str) and name.startswith("agent:"):
        print(name)
PY
}

item_number_from_item() {
  local encoded="$1"
  ENCODED_ITEM="$encoded" python - <<'PY'
import base64
import json
import os

item = json.loads(base64.b64decode(os.environ["ENCODED_ITEM"]).decode("utf-8"))
print(item["number"])
PY
}

process_item() {
  local kind="$1"
  local repo="$2"
  local encoded="$3"
  local number
  number="$(item_number_from_item "$encoded")"
  number="${number%$'\r'}"

  local agent_label ai_label
  while IFS= read -r agent_label; do
    agent_label="${agent_label%$'\r'}"
    [[ -n "$agent_label" ]] || continue
    if ! ai_label="$(ai_label_for_agent "$agent_label")"; then
      echo "SKIP ${kind} ${repo}#${number}: unsupported legacy label ${agent_label}"
      continue
    fi
    if [[ "$APPLY" == true ]]; then
      if ! repo_has_target_label "$ai_label"; then
        echo "SKIP ${kind} ${repo}#${number}: target label ${ai_label} missing in repo"
        continue
      fi
      echo "APPLY ${kind} ${repo}#${number}: add ${ai_label} remove ${agent_label}"
      gh "$kind" edit "$number" --repo "$repo" --add-label "$ai_label" --remove-label "$agent_label"
    else
      echo "DRY-RUN ${kind} ${repo}#${number}: add ${ai_label} remove ${agent_label}"
    fi
  done < <(agent_labels_from_item "$encoded")
}

while IFS= read -r repo; do
  [[ -n "$repo" ]] || continue
  REPO_LABELS=""
  if [[ "$APPLY" == true ]]; then
    if ! REPO_LABELS="$(gh label list --repo "$repo" --limit 1000 --json name --jq '.[].name')"; then
      echo "SKIP ${repo}: unable to list labels" >&2
      continue
    fi
  fi
  while IFS= read -r encoded; do
    [[ -n "$encoded" ]] || continue
    process_item issue "$repo" "$encoded"
  done < <(gh issue list --repo "$repo" --state all --limit 10000 --json number,labels --jq '.[] | @base64')

  while IFS= read -r encoded; do
    [[ -n "$encoded" ]] || continue
    process_item pr "$repo" "$encoded"
  done < <(gh pr list --repo "$repo" --state all --limit 10000 --json number,labels --jq '.[] | @base64')
done < <(gh repo list "$OWNER" --no-archived --limit 10000 --json nameWithOwner --jq '.[].nameWithOwner')
