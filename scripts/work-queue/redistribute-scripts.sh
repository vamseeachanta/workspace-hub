#!/usr/bin/env bash
# redistribute-scripts.sh — Move stage-specific scripts to folder-skill directories
# WRK-5112: Two-tier folder-skill architecture
#
# Usage:
#   bash scripts/work-queue/redistribute-scripts.sh [--dry-run]
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPTS_DIR="$REPO_ROOT/scripts/work-queue"
STAGES_DIR="$REPO_ROOT/.claude/skills/workspace-hub/stages"
MAPPING="$SCRIPTS_DIR/script-stage-mapping.yaml"
DRY_RUN="${1:-}"

if [[ ! -f "$MAPPING" ]]; then
    echo "ERROR: Mapping file not found: $MAPPING" >&2
    exit 1
fi

moved=0
skipped=0
errors=0

# Parse stage-specific section from mapping YAML
# Simple parser: look for lines under stage_specific with stage-NN-name pattern
current_stage=""
while IFS= read -r line; do
    # Skip comments and empty lines
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line// /}" ]] && continue

    # Detect stage header (e.g., "  stage-01-capture:")
    if [[ "$line" =~ ^[[:space:]]+(stage-[0-9]+-[a-z-]+): ]]; then
        current_stage="${BASH_REMATCH[1]}"
        continue
    fi

    # Detect script entry (e.g., "    - script-name.sh")
    if [[ -n "$current_stage" && "$line" =~ ^[[:space:]]+-[[:space:]]+([a-zA-Z0-9_.-]+) ]]; then
        script_name="${BASH_REMATCH[1]}"
        src="$SCRIPTS_DIR/$script_name"
        dest_dir="$STAGES_DIR/$current_stage/scripts"
        dest="$dest_dir/$script_name"

        if [[ ! -f "$src" ]]; then
            echo "SKIP: $script_name (not found at $src)"
            ((skipped++)) || true
            continue
        fi

        if [[ -L "$src" ]]; then
            echo "SKIP: $script_name (already a symlink)"
            ((skipped++)) || true
            continue
        fi

        if [[ "$DRY_RUN" == "--dry-run" ]]; then
            echo "DRY-RUN: $script_name → $current_stage/scripts/"
            ((moved++)) || true
            continue
        fi

        # Create scripts directory if needed
        mkdir -p "$dest_dir"

        # Move script to stage folder
        mv "$src" "$dest"

        # Create relative symlink from old location to new
        rel_path=$(realpath --relative-to="$SCRIPTS_DIR" "$dest")
        ln -s "$rel_path" "$src"

        echo "MOVED: $script_name → $current_stage/scripts/ (symlink created)"
        ((moved++)) || true
    fi

    # Stop processing when we hit shared: or utility: sections
    if [[ "$line" =~ ^shared: || "$line" =~ ^utility: ]]; then
        break
    fi
done < "$MAPPING"

echo ""
echo "━━━ Summary ━━━"
echo "Moved:   $moved"
echo "Skipped: $skipped"
echo "Errors:  $errors"
