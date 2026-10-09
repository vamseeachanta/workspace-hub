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

Repos missing a target ai:<provider> label are stopped before any edit. Dry-run
also reports missing target labels.

The script is idempotent: a re-run resumes where an earlier partial sweep
stopped because migrated items no longer carry agent:<provider> labels.
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

if command -v python3 >/dev/null 2>&1; then
  PY="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PY="$(command -v python)"
else
  echo "FAIL: python3 or python is required to parse gh JSON output" >&2
  exit 2
fi

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
  ENCODED_ITEM="$encoded" "$PY" - <<'PY'
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
  ENCODED_ITEM="$encoded" "$PY" - <<'PY'
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
  if ! number="$(item_number_from_item "$encoded")"; then
    echo "FAIL ${kind} ${repo}: unable to parse item number" >&2
    return 30
  fi
  number="${number%$'\r'}"

  local agent_label ai_label
  local agent_labels
  if ! agent_labels="$(agent_labels_from_item "$encoded")"; then
    echo "FAIL ${kind} ${repo}#${number}: unable to parse labels" >&2
    return 31
  fi

  while IFS= read -r agent_label; do
    agent_label="${agent_label%$'\r'}"
    [[ -n "$agent_label" ]] || continue
    if ! ai_label="$(ai_label_for_agent "$agent_label")"; then
      echo "SKIP ${kind} ${repo}#${number}: unsupported legacy label ${agent_label}"
      continue
    fi
    if ! repo_has_target_label "$ai_label"; then
      echo "SKIP ${kind} ${repo}#${number}: target label ${ai_label} missing in repo"
      return 10
    fi
    if [[ "$APPLY" == true ]]; then
      echo "APPLY ${kind} ${repo}#${number}: add ${ai_label} remove ${agent_label}"
      if ! gh "$kind" edit "$number" --repo "$repo" --add-label "$ai_label" --remove-label "$agent_label"; then
        echo "FAIL ${kind} ${repo}#${number}: edit failed" >&2
        return 20
      fi
    else
      echo "DRY-RUN ${kind} ${repo}#${number}: add ${ai_label} remove ${agent_label}"
    fi
  done <<<"$agent_labels"
}

process_encoded_items() {
  local kind="$1"
  local repo="$2"
  local items="$3"
  local encoded result
  while IFS= read -r encoded; do
    [[ -n "$encoded" ]] || continue
    if process_item "$kind" "$repo" "$encoded"; then
      continue
    else
      result=$?
      return "$result"
    fi
  done <<<"$items"
}

REPOS_OK=0
REPOS_SKIPPED=0
REPOS_FAILED=0

if ! REPOS="$(gh repo list "$OWNER" --no-archived --limit 10000 --json nameWithOwner --jq '.[].nameWithOwner')"; then
  echo "FAIL ${OWNER}: unable to list repositories" >&2
  echo "Summary: repos OK=0 skipped=0 failed=1"
  exit 1
fi

while IFS= read -r repo; do
  [[ -n "$repo" ]] || continue
  repo_status="ok"
  REPO_LABELS=""
  if ! REPO_LABELS="$(gh label list --repo "$repo" --limit 1000 --json name --jq '.[].name')"; then
    echo "FAIL ${repo}: unable to list labels" >&2
    REPOS_FAILED=$((REPOS_FAILED + 1))
    continue
  fi
  REPO_LABELS="${REPO_LABELS//$'\r'/}"

  if ! ISSUE_ITEMS="$(gh issue list --repo "$repo" --state all --limit 10000 --json number,labels --jq '.[] | @base64')"; then
    echo "FAIL ${repo}: unable to list issues" >&2
    REPOS_FAILED=$((REPOS_FAILED + 1))
    continue
  fi
  if process_encoded_items issue "$repo" "$ISSUE_ITEMS"; then
    :
  else
    result=$?
    case "$result" in
      10) repo_status="skipped" ;;
      *) repo_status="failed" ;;
    esac
  fi

  if [[ "$repo_status" == "ok" ]]; then
    if ! PR_ITEMS="$(gh pr list --repo "$repo" --state all --limit 10000 --json number,labels --jq '.[] | @base64')"; then
      echo "FAIL ${repo}: unable to list prs" >&2
      repo_status="failed"
    elif process_encoded_items pr "$repo" "$PR_ITEMS"; then
      :
    else
      result=$?
      case "$result" in
        10) repo_status="skipped" ;;
        *) repo_status="failed" ;;
      esac
    fi
  fi

  case "$repo_status" in
    ok) REPOS_OK=$((REPOS_OK + 1)) ;;
    skipped) REPOS_SKIPPED=$((REPOS_SKIPPED + 1)) ;;
    failed) REPOS_FAILED=$((REPOS_FAILED + 1)) ;;
  esac
done <<<"$REPOS"

echo "Summary: repos OK=${REPOS_OK} skipped=${REPOS_SKIPPED} failed=${REPOS_FAILED}"

if (( REPOS_SKIPPED > 0 || REPOS_FAILED > 0 )); then
  exit 1
fi
