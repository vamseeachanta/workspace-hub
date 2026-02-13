#!/usr/bin/env bash
# detect-repo.sh — Given a file path, identify which repo it belongs to.
# Usage: detect-repo.sh <file_path>
# Returns: repo name (worldenergydata, digitalmodel, workspace-hub) or empty

set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/mnt/local-analysis/workspace-hub}"

detect_repo() {
    local file_path="$1"

    # Normalize to absolute path
    if [[ "$file_path" != /* ]]; then
        file_path="${WORKSPACE_ROOT}/${file_path}"
    fi

    # Check known submodule directories
    if [[ "$file_path" == */worldenergydata/* ]]; then
        echo "worldenergydata"
    elif [[ "$file_path" == */digitalmodel/* ]]; then
        echo "digitalmodel"
    elif [[ "$file_path" == */assetutilities/* ]]; then
        echo "assetutilities"
    elif [[ "$file_path" == */aceengineer-website/* ]]; then
        echo "aceengineer-website"
    elif [[ "$file_path" == */aceengineer-admin/* ]]; then
        echo "aceengineer-admin"
    elif [[ "$file_path" == */assethold/* ]]; then
        echo "assethold"
    else
        # Default to workspace-hub for files at root level
        echo "workspace-hub"
    fi
}

# Run if called directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 1 ]]; then
        echo "Usage: detect-repo.sh <file_path>" >&2
        exit 1
    fi
    detect_repo "$1"
fi
