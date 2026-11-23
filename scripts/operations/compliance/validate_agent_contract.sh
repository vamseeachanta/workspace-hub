#!/usr/bin/env bash

# ABOUTME: Validate AGENTS.md/CLAUDE.md contract conformance across repos
# ABOUTME: Ensures adapter files exist and carry generation markers

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CANONICAL_FILE="$WORKSPACE_ROOT/AGENTS.md"
TARGET_MODE="all"
REPOS_CSV=""

usage() {
  cat << USAGE
Usage: $(basename "$0") [--workspace-only] [--repos repo1,repo2]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace-only)
      TARGET_MODE="workspace"
      shift
      ;;
    --repos)
      TARGET_MODE="repos"
      REPOS_CSV="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ ! -f "$CANONICAL_FILE" ]]; then
  echo "FAIL: missing $CANONICAL_FILE"
  exit 1
fi

CONTRACT_VERSION="$(awk -F': ' '/^Contract-Version:/{print $2}' "$CANONICAL_FILE" | head -n1)"
CONTRACT_VERSION="${CONTRACT_VERSION:-unknown}"

fail_count=0
check_count=0

check_repo() {
  local repo_path="$1"
  local repo_name
  repo_name="$(basename "$repo_path")"

  local claude="$repo_path/CLAUDE.md"
  local agents="$repo_path/AGENTS.md"

  check_count=$((check_count + 1))

  if [[ ! -f "$claude" ]]; then
    echo "FAIL [$repo_name] missing CLAUDE.md"
    fail_count=$((fail_count + 1))
    return
  fi

  if ! grep -q "Generated from workspace-hub/AGENTS.md" "$claude"; then
    echo "FAIL [$repo_name] CLAUDE.md missing generation marker"
    fail_count=$((fail_count + 1))
  fi

  if ! grep -q "Contract-Version: $CONTRACT_VERSION" "$claude"; then
    echo "FAIL [$repo_name] CLAUDE.md contract version mismatch"
    fail_count=$((fail_count + 1))
  fi

  if [[ "$repo_path" != "$WORKSPACE_ROOT" ]]; then
    if [[ ! -f "$agents" ]]; then
      echo "FAIL [$repo_name] missing AGENTS.md pointer"
      fail_count=$((fail_count + 1))
    elif ! grep -q "../AGENTS.md" "$agents"; then
      echo "FAIL [$repo_name] AGENTS.md pointer missing canonical reference"
      fail_count=$((fail_count + 1))
    fi
  fi
}

check_repo "$WORKSPACE_ROOT"

if [[ "$TARGET_MODE" == "workspace" ]]; then
  :
elif [[ "$TARGET_MODE" == "repos" ]]; then
  IFS=',' read -r -a repos <<< "$REPOS_CSV"
  for repo in "${repos[@]}"; do
    repo="${repo// /}"
    [[ -z "$repo" ]] && continue
    if [[ -d "$WORKSPACE_ROOT/$repo" ]]; then
      check_repo "$WORKSPACE_ROOT/$repo"
    fi
  done
else
  while IFS= read -r -d '' dir; do
    if [[ -e "$dir/.git" ]]; then
      check_repo "$dir"
    fi
  done < <(find "$WORKSPACE_ROOT" -mindepth 1 -maxdepth 1 -type d -print0)
fi

if [[ "$fail_count" -gt 0 ]]; then
  echo "Validation failed: $fail_count issues across $check_count repos"
  exit 1
fi

echo "Validation passed across $check_count repos (contract v$CONTRACT_VERSION)"
