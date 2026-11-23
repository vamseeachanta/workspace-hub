#!/bin/bash
# Sync statusline configuration to all workspace-hub repositories
# Usage: ./scripts/sync_statusline.sh [--all | --git-only]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="$(cd "$SCRIPT_DIR/../.." && pwd)"
SOURCE_SCRIPT="$WORKSPACE_HUB/.claude/statusline-command.sh"

echo "=== Syncing Statusline to All Repos ==="
echo "Source: $SOURCE_SCRIPT"
echo ""

# Auto-detect repos: directories with .git or existing .claude folder
REPOS=()
for dir in "$WORKSPACE_HUB"/*/; do
    name=$(basename "$dir")
    # Skip internal/system directories
    [[ "$name" =~ ^(_|node_modules|logs|data|reports|.git) ]] && continue
    # Include if it's a git repo OR has .claude folder
    if [ -d "$dir/.git" ] || [ -d "$dir/.claude" ]; then
        REPOS+=("$name")
    fi
done

synced=0
skipped=0

for repo in "${REPOS[@]}"; do
    repo_path="$WORKSPACE_HUB/$repo"
    target_dir="$repo_path/.claude"
    target_script="$target_dir/statusline-command.sh"

    if [ -d "$repo_path" ]; then
        # Create .claude directory if needed
        mkdir -p "$target_dir"

        # Copy the statusline script
        cp "$SOURCE_SCRIPT" "$target_script"
        chmod +x "$target_script"

        # Check if settings.json exists and update it
        settings_file="$target_dir/settings.json"
        if [ -f "$settings_file" ]; then
            # Check if statusLine already configured
            if grep -q '"statusLine"' "$settings_file"; then
                echo "✓ $repo - statusLine already configured"
            else
                # Add statusLine to settings.json using jq
                if command -v jq &> /dev/null; then
                    tmp=$(mktemp)
                    jq '. + {"statusLine": {"type": "command", "command": ".claude/statusline-command.sh"}}' "$settings_file" > "$tmp" && mv "$tmp" "$settings_file"
                    echo "✓ $repo - added statusLine to settings.json"
                else
                    echo "! $repo - jq not found, manual update needed"
                fi
            fi
        else
            # Create minimal settings.json with statusLine
            echo '{
  "statusLine": {
    "type": "command",
    "command": ".claude/statusline-command.sh"
  }
}' > "$settings_file"
            echo "✓ $repo - created settings.json with statusLine"
        fi

        ((synced++))
    else
        echo "- $repo - not found, skipped"
        ((skipped++))
    fi
done

echo ""
echo "=== Summary ==="
echo "Synced: $synced repos"
echo "Skipped: $skipped repos"
echo ""
echo "Statusline format: model | workspace | [████░░░░] pct%"
echo "Colors: green (<70%), yellow (70-85%), red (>85%)"
