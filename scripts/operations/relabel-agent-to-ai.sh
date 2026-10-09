#!/usr/bin/env bash
set -euo pipefail

OWNER="${OWNER:-vamseeachanta}"
APPLY=false
INCLUDE_CLOSED=false

usage() {
  cat <<'USAGE'
Usage: scripts/operations/relabel-agent-to-ai.sh [--apply] [--open-only|--include-closed]

Dry-run by default. --open-only is the default sweep mode.

Owner decision F01 = lane_soft (saved round-4 board, 2026-10-09):
- Open issues and PRs: agent:claude -> lane:claude, agent:codex -> lane:codex.
  Existing lane:* labels win; the script removes agent:* and adds no lane.
  Other open agent:* labels are removed and reported with no lane added.
  Open items never receive ai:* labels.
- Closed issues and PRs: only with --include-closed, agent:<x> -> ai:<x> for
  history, with agent:gemini -> ai:agy.

Repos missing a target lane:* or ai:* label are stopped before any edit for that
repo. Dry-run also reports missing target labels. The script is idempotent: a
re-run resumes where an earlier partial sweep stopped because migrated items no
longer carry agent:<provider> labels.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)
      APPLY=true
      ;;
    --open-only)
      INCLUDE_CLOSED=false
      ;;
    --include-closed)
      INCLUDE_CLOSED=true
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

open_lane_for_agent() {
  case "$1" in
    agent:claude) printf '%s\n' "lane:claude" ;;
    agent:codex) printf '%s\n' "lane:codex" ;;
    *) return 1 ;;
  esac
}

closed_ai_label_for_agent() {
  local provider="${1#agent:}"
  [[ "$provider" != "$1" && -n "$provider" ]] || return 1
  case "$provider" in
    gemini) provider="agy" ;;
  esac
  printf 'ai:%s\n' "$provider"
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

lane_labels_from_item() {
  local encoded="$1"
  ENCODED_ITEM="$encoded" "$PY" - <<'PY'
import base64
import json
import os

item = json.loads(base64.b64decode(os.environ["ENCODED_ITEM"]).decode("utf-8"))
for label in item.get("labels", []):
    name = label.get("name") if isinstance(label, dict) else label
    if isinstance(name, str) and name.startswith("lane:"):
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

edit_item() {
  local kind="$1"
  local repo="$2"
  local number="$3"
  local add_label="$4"
  local remove_label="$5"
  local -a command=(gh "$kind" edit "$number" --repo "$repo")
  if [[ -n "$add_label" ]]; then
    command+=(--add-label "$add_label")
  fi
  command+=(--remove-label "$remove_label")
  if ! "${command[@]}"; then
    echo "FAIL ${kind} ${repo}#${number}: edit failed" >&2
    return 20
  fi
}

remove_open_agent_label() {
  local kind="$1"
  local repo="$2"
  local number="$3"
  local agent_label="$4"
  local message="$5"
  echo "$message"
  if [[ "$APPLY" == true ]] && ! edit_item "$kind" "$repo" "$number" "" "$agent_label"; then
    return 20
  fi
}

process_open_item() {
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
  local lane_labels existing_lane
  if ! lane_labels="$(lane_labels_from_item "$encoded")"; then
    echo "FAIL ${kind} ${repo}#${number}: unable to parse lane labels" >&2
    return 31
  fi
  existing_lane="$(printf '%s\n' "$lane_labels" | sed -n '1p')"
  existing_lane="${existing_lane%$'\r'}"

  while IFS= read -r agent_label; do
    agent_label="${agent_label%$'\r'}"
    [[ -n "$agent_label" ]] || continue
    if [[ -n "$existing_lane" ]]; then
      remove_open_agent_label "$kind" "$repo" "$number" "$agent_label" \
        "CONFLICT ${kind} ${repo}#${number}: existing lane label ${existing_lane} wins; remove ${agent_label}" || return 20
      continue
    fi
    if ! ai_label="$(open_lane_for_agent "$agent_label")"; then
      remove_open_agent_label "$kind" "$repo" "$number" "$agent_label" \
        "UNMAPPED ${kind} ${repo}#${number}: remove ${agent_label}; no lane added for open item" || return 20
      continue
    fi
    if ! repo_has_target_label "$ai_label"; then
      echo "SKIP ${kind} ${repo}#${number}: target label ${ai_label} missing in repo"
      return 10
    fi
    if [[ "$APPLY" == true ]]; then
      echo "APPLY ${kind} ${repo}#${number}: add ${ai_label} remove ${agent_label}"
      edit_item "$kind" "$repo" "$number" "$ai_label" "$agent_label" || return 20
    else
      echo "DRY-RUN ${kind} ${repo}#${number}: add ${ai_label} remove ${agent_label}"
    fi
  done <<<"$agent_labels"
}

process_closed_item() {
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
    if ! ai_label="$(closed_ai_label_for_agent "$agent_label")"; then
      echo "SKIP ${kind} ${repo}#${number}: unsupported legacy label ${agent_label}"
      continue
    fi
    if ! repo_has_target_label "$ai_label"; then
      echo "SKIP ${kind} ${repo}#${number}: target label ${ai_label} missing in repo"
      return 10
    fi
    if [[ "$APPLY" == true ]]; then
      echo "APPLY ${kind} ${repo}#${number}: add ${ai_label} remove ${agent_label}"
      edit_item "$kind" "$repo" "$number" "$ai_label" "$agent_label" || return 20
    else
      echo "DRY-RUN ${kind} ${repo}#${number}: add ${ai_label} remove ${agent_label}"
    fi
  done <<<"$agent_labels"
}

process_encoded_items() {
  local kind="$1"
  local repo="$2"
  local state="$3"
  local items="$4"
  local encoded result
  while IFS= read -r encoded; do
    [[ -n "$encoded" ]] || continue
    if [[ "$state" == "open" ]]; then
      if process_open_item "$kind" "$repo" "$encoded"; then
        continue
      else
        result=$?
        return "$result"
      fi
    else
      if process_closed_item "$kind" "$repo" "$encoded"; then
        continue
      else
        result=$?
        return "$result"
      fi
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

  if ! ISSUE_ITEMS="$(gh issue list --repo "$repo" --state open --limit 10000 --json number,labels --jq '.[] | @base64')"; then
    echo "FAIL ${repo}: unable to list issues" >&2
    REPOS_FAILED=$((REPOS_FAILED + 1))
    continue
  fi
  if process_encoded_items issue "$repo" open "$ISSUE_ITEMS"; then
    :
  else
    result=$?
    case "$result" in
      10) repo_status="skipped" ;;
      *) repo_status="failed" ;;
    esac
  fi

  if [[ "$repo_status" == "ok" ]]; then
    if ! PR_ITEMS="$(gh pr list --repo "$repo" --state open --limit 10000 --json number,labels --jq '.[] | @base64')"; then
      echo "FAIL ${repo}: unable to list prs" >&2
      repo_status="failed"
    elif process_encoded_items pr "$repo" open "$PR_ITEMS"; then
      :
    else
      result=$?
      case "$result" in
        10) repo_status="skipped" ;;
        *) repo_status="failed" ;;
      esac
    fi
  fi

  if [[ "$INCLUDE_CLOSED" == true && "$repo_status" == "ok" ]]; then
    if ! ISSUE_ITEMS="$(gh issue list --repo "$repo" --state closed --limit 10000 --json number,labels --jq '.[] | @base64')"; then
      echo "FAIL ${repo}: unable to list closed issues" >&2
      repo_status="failed"
    elif process_encoded_items issue "$repo" closed "$ISSUE_ITEMS"; then
      :
    else
      result=$?
      case "$result" in
        10) repo_status="skipped" ;;
        *) repo_status="failed" ;;
      esac
    fi
  fi

  if [[ "$INCLUDE_CLOSED" == true && "$repo_status" == "ok" ]]; then
    if ! PR_ITEMS="$(gh pr list --repo "$repo" --state closed --limit 10000 --json number,labels --jq '.[] | @base64')"; then
      echo "FAIL ${repo}: unable to list closed prs" >&2
      repo_status="failed"
    elif process_encoded_items pr "$repo" closed "$PR_ITEMS"; then
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
