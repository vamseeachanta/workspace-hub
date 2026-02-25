#!/usr/bin/env bash

# ABOUTME: Migrate repo-local specs into centralized workspace-hub specs/repos
# ABOUTME: Supports dry-run by default and leaves compatibility README pointers

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DRY_RUN="true"
TARGET_REPOS=""

usage() {
  cat << USAGE
Usage: $(basename "$0") [--apply] [--repos repo1,repo2]

Options:
  --apply             Perform migration (default is dry-run)
  --repos <csv>       Limit migration to selected repos
  -h, --help          Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)
      DRY_RUN="false"
      shift
      ;;
    --repos)
      TARGET_REPOS="${2:-}"
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

should_process_repo() {
  local repo_name="$1"
  if [[ -z "$TARGET_REPOS" ]]; then
    return 0
  fi

  IFS=',' read -r -a arr <<< "$TARGET_REPOS"
  for item in "${arr[@]}"; do
    item="${item// /}"
    if [[ "$item" == "$repo_name" ]]; then
      return 0
    fi
  done
  return 1
}

migrate_repo_specs() {
  local repo_path="$1"
  local repo_name
  repo_name="$(basename "$repo_path")"
  
  # Find all directories named 'specs' recursively within the repo
  # excluding the root 'specs' dir if we are at root (but we skip root anyway)
  # also excluding .venv, node_modules, etc.
  local spec_dirs
  spec_dirs=$(find "$repo_path" -type d -name "specs" \
    -not -path "*/.venv/*" -not -path "*/node_modules/*" -not -path "*/.git/*")
  
  for repo_specs in $spec_dirs; do
    local file_count
    file_count="$(find "$repo_specs" -type f | wc -l | tr -d ' ')"
    [[ "$file_count" -gt 0 ]] || continue

    # Target directory in root: specs/repos/<repo_name>/<relative_path_within_repo>
    local rel_specs_path="${repo_specs#"$repo_path/"}"
    local target_dir="$WORKSPACE_ROOT/specs/repos/$repo_name/$rel_specs_path"
    
    echo "repo=$repo_name loc=$rel_specs_path files=$file_count target=$target_dir dry_run=$DRY_RUN"

    if [[ "$DRY_RUN" == "true" ]]; then
      find "$repo_specs" -type f | sed "s#^#  would-move: #"
      continue
    fi

    mkdir -p "$target_dir"

    # Copy preserving relative layout inside specs/
    while IFS= read -r -d '' file; do
      rel="${file#"$repo_specs/"}"
      mkdir -p "$(dirname "$target_dir/$rel")"
      cp "$file" "$target_dir/$rel"
    done < <(find "$repo_specs" -type f -print0)

    # Replace local specs with pointer README
    rm -rf "$repo_specs"
    mkdir -p "$repo_specs"
    cat > "$repo_specs/README.md" << POINTER
# Specs Pointer

Specs are centralized in:
\`specs/repos/$repo_name/$rel_specs_path/\`
POINTER
  done
}

while IFS= read -r -d '' dir; do
  if [[ -e "$dir/.git" ]]; then
    repo_name="$(basename "$dir")"
    if should_process_repo "$repo_name"; then
      migrate_repo_specs "$dir"
    fi
  fi
done < <(find "$WORKSPACE_ROOT" -mindepth 1 -maxdepth 1 -type d -print0)
