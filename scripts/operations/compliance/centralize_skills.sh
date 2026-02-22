#!/usr/bin/env bash

# ABOUTME: Centralize child-repo skills into workspace-hub .claude/skills
# ABOUTME: Replaces local directories with relative symlinks to root
# ABOUTME: Preserves unique child-repo content by moving it to root first

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DRY_RUN="true"

usage() {
  cat << USAGE
Usage: $(basename "$0") [--apply]

Options:
  --apply             Perform centralization (default is dry-run)
  -h, --help          Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) DRY_RUN="false"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

echo "Starting skills centralization (dry_run=$DRY_RUN)..."

# Find all child repos
while IFS= read -r -d '' repo_dir; do
  repo_name="$(basename "$repo_dir")"
  skills_dir="$repo_dir/.claude/skills"

  if [[ "$repo_dir" == "$WORKSPACE_ROOT" ]]; then continue; fi
  [[ -d "$skills_dir" ]] || continue

  echo "Processing repo: $repo_name"

  # Find all directories in child skills (top-level skills)
  find "$skills_dir" -mindepth 1 -maxdepth 1 -type d -print0 | while IFS= read -r -d '' child_skill_path; do
    skill_name="$(basename "$child_skill_path")"
    
    # Check if it's already a symlink
    if [[ -L "$child_skill_path" ]]; then
      echo "  [SKIP] $skill_name is already a symlink"
      continue
    fi

    # Find matching skill in root
    root_skill_path=$(find "$WORKSPACE_ROOT/.claude/skills" -name "$skill_name" -type d -not -path "*/.git/*" | head -n 1)

    if [[ -n "$root_skill_path" ]]; then
      # Found in root. Compare.
      if diff -r "$child_skill_path" "$root_skill_path" >/dev/null 2>&1; then
        echo "  [LINK] $skill_name (identical to root)"
        if [[ "$DRY_RUN" == "false" ]]; then
          rm -rf "$child_skill_path"
          ln -s "$(realpath --relative-to="$(dirname "$child_skill_path")" "$root_skill_path")" "$child_skill_path"
        fi
      else
        echo "  [MERGE] $skill_name (diverged from root)"
        # For now, we move the child version to a unique path in root to preserve it
        # and then link to it. Real merging should be manual.
        target_in_root="$WORKSPACE_ROOT/.claude/skills/_diverged/$repo_name/$skill_name"
        if [[ "$DRY_RUN" == "false" ]]; then
          mkdir -p "$(dirname "$target_in_root")"
          mv "$child_skill_path" "$target_in_root"
          ln -s "$(realpath --relative-to="$(dirname "$child_skill_path")" "$target_in_root")" "$child_skill_path"
        else
          echo "    would-move to: $target_in_root"
        fi
      fi
    else
      # Not in root. Move to root.
      echo "  [MOVE] $skill_name (unique to $repo_name)"
      target_in_root="$WORKSPACE_ROOT/.claude/skills/incoming/$repo_name/$skill_name"
      if [[ "$DRY_RUN" == "false" ]]; then
        mkdir -p "$(dirname "$target_in_root")"
        mv "$child_skill_path" "$target_in_root"
        ln -s "$(realpath --relative-to="$(dirname "$child_skill_path")" "$target_in_root")" "$child_skill_path"
      else
        echo "    would-move to: $target_in_root"
      fi
    fi
  done
done < <(find "$WORKSPACE_ROOT" -mindepth 1 -maxdepth 1 -type d -print0)

echo "Done."
