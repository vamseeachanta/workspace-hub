#!/usr/bin/env bash

# ABOUTME: Generate provider adapter files from canonical AGENTS.md
# ABOUTME: Writes deterministic CLAUDE.md adapters and AGENTS.md pointers in managed repos

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
  --workspace-only     Only update workspace-hub root CLAUDE.md
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
DATE_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

write_claude_adapter() {
  local repo_path="$1"
  local repo_name
  repo_name="$(basename "$repo_path")"
  cat > "$repo_path/CLAUDE.md" << ADAPTER
# ${repo_name^} Agent Adapter

> Generated from workspace-hub/AGENTS.md
> Contract-Version: $CONTRACT_VERSION
> Generated-At: $DATE_UTC

## Adapter Role

This file is a provider-specific adapter for Claude-compatible tooling.
The canonical contract is in workspace-hub/AGENTS.md.

## Required Gates

1. Every non-trivial task must map to a WRK-* item in .claude/work-queue/.
2. Planning + explicit approval are required before implementation.
3. Route B/C work requires cross-review before completion.

## Plan and Spec Locality

1. Route A/B plan details can live in WRK body sections.
2. Route C execution specs: specs/wrk/WRK-<id>/.
3. Repository/domain specs: specs/repos/<repo>/.
4. Templates: specs/templates/.

## Compatibility

Legacy docs may exist during migration, but AGENTS.md is canonical.

## Repo Overrides

Add repo-specific details below this section without weakening required gates.
ADAPTER
}

write_repo_agents_pointer() {
  local repo_path="$1"
  local repo_name
  repo_name="$(basename "$repo_path")"

  # Keep workspace root AGENTS.md as canonical content; repo files are pointers.
  if [[ "$repo_path" == "$WORKSPACE_ROOT" ]]; then
    return
  fi

  cat > "$repo_path/AGENTS.md" << POINTER
# ${repo_name^} Agent Contract Pointer

This repository inherits the canonical contract from:
../AGENTS.md

- Contract-Version: $CONTRACT_VERSION
- Generated-At: $DATE_UTC

Do not hand-edit policy here. Update workspace-hub/AGENTS.md and regenerate adapters.
POINTER
}

update_repo() {
  local repo_path="$1"
  if [[ ! -d "$repo_path" ]]; then
    echo "skip: missing path $repo_path"
    return
  fi

  write_claude_adapter "$repo_path"
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
