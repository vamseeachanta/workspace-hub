#!/usr/bin/env bash
# resolve-workspace.sh — Portable workspace-hub path resolver
# Source this from any hook script: source "$(dirname "${BASH_SOURCE[0]}")/resolve-workspace.sh"
# Or call: WORKSPACE_HUB=$(bash /path/to/resolve-workspace.sh)
#
# Resolution order:
# 1. $WORKSPACE_HUB env var (already set)
# 2. Script location: hooks/ -> .claude/ -> workspace-hub/
# 3. Git superproject (for submodule repos)
# 4. Git toplevel (for workspace-hub itself)
# 5. Platform-specific fallbacks
#
# Portable across: Windows (Git Bash/MINGW), Linux, macOS
# Other repos symlink to this file or reference via git superproject.

resolve_workspace_hub() {
    # 1. Env var
    if [[ -n "${WORKSPACE_HUB:-}" ]]; then
        echo "$WORKSPACE_HUB"
        return
    fi

    # 2. Script location (works when script is in workspace-hub/.claude/hooks/)
    if [[ -n "${BASH_SOURCE[0]:-}" ]]; then
        local script_dir
        script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
        local candidate="$(cd "$script_dir/../.." 2>/dev/null && pwd)"
        if [[ -d "$candidate/.claude/hooks" ]]; then
            echo "$candidate"
            return
        fi
    fi

    # 3. Git superproject (for submodule repos like digitalmodel)
    local superproject
    superproject=$(git rev-parse --show-superproject-working-tree 2>/dev/null)
    if [[ -n "$superproject" && -d "$superproject/.claude" ]]; then
        echo "$superproject"
        return
    fi

    # 4. Git toplevel (for workspace-hub itself)
    local toplevel
    toplevel=$(git rev-parse --show-toplevel 2>/dev/null)
    if [[ -n "$toplevel" && -d "$toplevel/.claude/hooks" ]]; then
        echo "$toplevel"
        return
    fi

    # 5. Platform fallbacks
    case "$(uname -s)" in
        MINGW*|MSYS*|CYGWIN*)
            for dir in "/d/workspace-hub" "/c/workspace-hub" "/c/github/workspace-hub"; do
                [[ -d "$dir/.claude" ]] && echo "$dir" && return
            done
            ;;
        *)
            for dir in "$HOME/workspace-hub" "$HOME/github/workspace-hub"; do
                [[ -d "$dir/.claude" ]] && echo "$dir" && return
            done
            ;;
    esac

    # Last resort
    echo "$HOME/.claude"
}

# When sourced, export the variable. When executed, print it.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    resolve_workspace_hub
else
    export WORKSPACE_HUB="$(resolve_workspace_hub)"
fi
