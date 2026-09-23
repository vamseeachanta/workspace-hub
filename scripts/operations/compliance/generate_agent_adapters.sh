#!/usr/bin/env bash

# ABOUTME: Create missing AGENTS.md pointers from the canonical contract
# ABOUTME: Preserves existing AGENTS.md content and every CLAUDE.md baseline

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CANONICAL_FILE="$WORKSPACE_ROOT/AGENTS.md"
TARGET_MODE="all"
REPOS_CSV=""

usage() {
  cat << USAGE
Usage: $(basename "$0") [--workspace-only] [--repos repo1,repo2]

Options:
  --workspace-only     Validate the workspace-hub root only
  --repos <csv>        Update selected repositories only
  -h, --help           Show this help
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
      if [[ -z "$REPOS_CSV" ]]; then
        echo "--repos requires a comma-separated value" >&2
        exit 1
      fi
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
  echo "Canonical contract missing: $CANONICAL_FILE" >&2
  exit 1
fi

CONTRACT_VERSION="$(awk -F': ' '/^Contract-Version:/{print $2}' "$CANONICAL_FILE" | head -n1)"
CONTRACT_VERSION="${CONTRACT_VERSION:-unknown}"
write_repo_agents_pointer() {
  local repo_path="$1"
  local repo_name
  repo_name="$(basename "$repo_path")"

  # Keep workspace root AGENTS.md as canonical content; repo files are pointers.
  if [[ "$repo_path" == "$WORKSPACE_ROOT" ]]; then
    return
  fi

  if [[ -e "$repo_path/AGENTS.md" || -L "$repo_path/AGENTS.md" ]]; then
    echo "preserve: $repo_name AGENTS.md already exists"
    return
  fi

  cat > "$repo_path/AGENTS.md" << POINTER
# $repo_name Agent Contract Pointer

This repository inherits the canonical contract from:
../AGENTS.md

- Contract-Version: $CONTRACT_VERSION
Do not hand-edit policy here. Update workspace-hub/AGENTS.md and regenerate adapters.
POINTER
}

update_repo() {
  local repo_path="$1"
  if [[ ! -d "$repo_path" ]]; then
    echo "skip: missing path $repo_path"
    return
  fi

  local repo_name
  repo_name="$(basename "$repo_path")"
  if [[ -e "$repo_path/CLAUDE.md" || -L "$repo_path/CLAUDE.md" ]]; then
    echo "preserve: $repo_name CLAUDE.md baseline unchanged"
  fi
  write_repo_agents_pointer "$repo_path"
  echo "updated: $repo_path"
}

if [[ "$TARGET_MODE" == "workspace" ]]; then
  update_repo "$WORKSPACE_ROOT"
  exit 0
fi

if [[ "$TARGET_MODE" == "repos" ]]; then
  IFS=',' read -r -a repos <<< "$REPOS_CSV"
  update_repo "$WORKSPACE_ROOT"
  for repo in "${repos[@]}"; do
    repo="${repo// /}"
    [[ -z "$repo" ]] && continue
    if [[ ! "$repo" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
      echo "unsafe repository name: $repo" >&2
      exit 1
    fi
    update_repo "$WORKSPACE_ROOT/$repo"
  done
  exit 0
fi

# Default: all managed repos with a .git entry (dir or file)
update_repo "$WORKSPACE_ROOT"
while IFS= read -r -d '' dir; do
  if [[ -e "$dir/.git" ]]; then
    update_repo "$dir"
  fi
done < <(find "$WORKSPACE_ROOT" -mindepth 1 -maxdepth 1 -type d -print0)
