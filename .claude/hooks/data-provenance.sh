#!/usr/bin/env bash
# data-provenance.sh — Data file access provenance snapshot
# Trigger: Stop event
# Output: .claude/state/provenance/provenance_<SESSION_TAG>.yaml
#
# SCOPE: Detect data file accesses from session transcript and record
#        provenance metadata: LFS status, sha256, row count, source system.
#        Silent when no data files detected.
#
# Platform: Linux, macOS, Windows (Git Bash/MINGW)
# Dependencies: bash, jq, git, sha256sum (Linux) or shasum (macOS), wc

set -uo pipefail

# --- Workspace resolution (relative, portable) ---
detect_workspace_hub() {
    if [[ -n "${WORKSPACE_HUB:-}" ]]; then
        echo "$WORKSPACE_HUB"
        return
    fi
    # Resolve relative to this script's location: hooks/ -> .claude/ -> workspace-hub/
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local candidate="$(cd "$script_dir/../.." && pwd)"
    if [[ -d "$candidate/.claude" ]]; then
        echo "$candidate"
        return
    fi
    # Fallback: common locations
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
    echo "$HOME/.claude"
}

# --- Find the latest session transcript ---
find_latest_transcript() {
    local claude_dir="$HOME/.claude/projects"
    [[ ! -d "$claude_dir" ]] && return 1

    # Narrow search to current project dir if possible (much faster than scanning all)
    # Claude uses format like "D--workspace-hub-digitalmodel" for "D:\workspace-hub\digitalmodel"
    # Drive letter is uppercase, path separators become single dash
    local cwd_path
    cwd_path=$(pwd)
    # Extract drive letter and uppercase it; convert path separators to single dash
    local project_key
    project_key=$(echo "$cwd_path" | sed 's|^/\(.\)/|\U\1--|; s|/|-|g')
    local search_dirs=()
    if [[ -d "$claude_dir/$project_key" ]]; then
        search_dirs=("$claude_dir/$project_key")
    else
        # Also try case-insensitive match on Windows
        local match
        match=$(ls -d "$claude_dir"/*/ 2>/dev/null | while read -r d; do
            local base=$(basename "$d")
            if [[ "${base,,}" == "${project_key,,}" ]]; then
                echo "$d"
                break
            fi
        done)
        if [[ -n "$match" && -d "$match" ]]; then
            search_dirs=("${match%/}")
        else
            # Fallback: search all project dirs (slower but works)
            for d in "$claude_dir"/*/; do
                [[ -d "$d" ]] && search_dirs+=("${d%/}")
            done
            search_dirs+=("$claude_dir")
        fi
    fi

    # Use ls -t to find most recent .jsonl (fast, avoids stat per file)
    local latest=""
    for search_dir in "${search_dirs[@]}"; do
        local candidate
        candidate=$(ls -t "$search_dir"/*.jsonl 2>/dev/null | head -1)
        if [[ -n "$candidate" && -f "$candidate" ]]; then
            latest="$candidate"
            break
        fi
    done

    [[ -n "$latest" ]] && echo "$latest"
}

WS_HUB="$(detect_workspace_hub)"
PROVENANCE_DIR="${WS_HUB}/.claude/state/provenance"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE_TAG=$(date +%Y%m%d)
SESSION_TAG="${DATE_TAG}_$(date +%H%M%S)"

# Ensure output directory exists
mkdir -p "$PROVENANCE_DIR" 2>/dev/null

# --- Read stdin first (hook may pipe data), before any other reads ---
HOOK_INPUT=""
if [[ ! -t 0 ]]; then
    HOOK_INPUT=$(cat 2>/dev/null || true)
fi

# Extract session_id from HOOK_INPUT if present
SESSION_ID="unknown"
if [[ -n "$HOOK_INPUT" ]]; then
    SESSION_ID=$(echo "$HOOK_INPUT" | jq -r '.session_id // "unknown"' 2>/dev/null || echo "unknown")
fi

# Allow explicit transcript path via env var (useful for testing)
CLEANUP_TEMP=false
if [[ -n "${DATA_PROVENANCE_TRANSCRIPT:-}" && -f "${DATA_PROVENANCE_TRANSCRIPT:-}" ]]; then
    TRANSCRIPT="$DATA_PROVENANCE_TRANSCRIPT"
    CLEANUP_TEMP=false
elif [[ -n "$HOOK_INPUT" ]]; then
    # Use piped stdin — printf preserves newlines better than echo
    TRANSCRIPT=$(mktemp)
    printf '%s\n' "$HOOK_INPUT" > "$TRANSCRIPT"
    CLEANUP_TEMP=true
else
    # Find latest session transcript
    TRANSCRIPT=$(find_latest_transcript)
    if [[ -z "${TRANSCRIPT:-}" || ! -f "${TRANSCRIPT:-}" ]]; then
        exit 0
    fi
    CLEANUP_TEMP=false
fi

# --- Data extension and dir patterns ---
DATA_EXT_PATTERN='\.(csv|parquet|nc|xlsx|xls|json|geojson|feather|arrow|h5|hdf5)$'
DATA_DIR_PATTERN='worldenergydata/data|bsee|metocean|era5|ndbc|rig.fleet|production'

# --- Extract data file paths from transcript ---
# 1. Read tool: file_path matching data extensions
# 2. Bash tool: command referencing data paths (extension OR known dir prefix)
DATA_PATHS=$(jq -r '
    select(.type == "assistant")
    | .message.content[]?
    | select(.type == "tool_use")
    | if .name == "Read" then
        .input.file_path // ""
        | select(test("\\.(csv|parquet|nc|xlsx|xls|json|geojson|feather|arrow|h5|hdf5)$"; "i"))
      elif .name == "Bash" then
        # Extract paths from command string: words containing data extensions or known dir prefixes
        (.input.command // "")
        | [ scan("[^\\s\"'"'"']+") ]
        | .[]
        | select(
            test("\\.(csv|parquet|nc|xlsx|xls|json|geojson|feather|arrow|h5|hdf5)$"; "i")
            or test("worldenergydata/data|bsee|metocean|era5|ndbc|rig.fleet|production"; "i")
          )
      else empty end
' "$TRANSCRIPT" 2>/dev/null | sort -u || true)

if [[ -z "$DATA_PATHS" ]]; then
    # No data files detected — silent exit
    [[ "$CLEANUP_TEMP" == "true" ]] && rm -f "$TRANSCRIPT" 2>/dev/null
    exit 0
fi

# --- Determine sha256 command (cross-platform) ---
sha256_of_file() {
    local fpath="$1"
    case "$(uname -s)" in
        Darwin*)
            shasum -a 256 "$fpath" 2>/dev/null | awk '{print $1}'
            ;;
        *)
            sha256sum "$fpath" 2>/dev/null | awk '{print $1}'
            ;;
    esac
}

# --- Determine project name ---
PROJECT="unknown"
if command -v git &>/dev/null; then
    PROJECT=$(git -C "$WS_HUB" rev-parse --show-toplevel 2>/dev/null | xargs basename 2>/dev/null || echo "unknown")
fi

# --- Build YAML output ---
OUTPUT_FILE="${PROVENANCE_DIR}/provenance_${SESSION_TAG}.yaml"

{
    printf 'session_id: %s\n' "$SESSION_ID"
    printf 'timestamp: %s\n' "$TIMESTAMP"
    printf 'project: %s\n' "$PROJECT"
    printf 'data_sources:\n'
} > "$OUTPUT_FILE"

while IFS= read -r fpath; do
    [[ -z "$fpath" ]] && continue

    # --- Source system heuristic ---
    source_system="unknown"
    if echo "$fpath" | grep -qi 'bsee'; then
        source_system="BSEE API"
    elif echo "$fpath" | grep -qi 'era5'; then
        source_system="ERA5 Copernicus"
    elif echo "$fpath" | grep -qi 'ndbc'; then
        source_system="NOAA NDBC"
    elif echo "$fpath" | grep -qi 'metocean'; then
        source_system="metocean study"
    fi

    # --- Vintage: extract 4-digit year(s) from basename ---
    bname=$(basename "$fpath")
    vintage=$(echo "$bname" | grep -oE '[0-9]{4}' | head -1 || true)
    [[ -z "$vintage" ]] && vintage="null"

    # --- LFS and sha256 ---
    lfs_status="materialized"
    sha256_val="null"

    if command -v git &>/dev/null && git lfs pointer --check "$fpath" &>/dev/null 2>&1; then
        lfs_status="stub"
        # Extract oid from pointer file content
        oid=$(grep -oE 'sha256:[a-f0-9]+' "$fpath" 2>/dev/null | head -1 || true)
        if [[ -n "$oid" ]]; then
            sha256_val="${oid#sha256:}"
        fi
    elif [[ -f "$fpath" ]]; then
        computed=$(sha256_of_file "$fpath")
        [[ -n "$computed" ]] && sha256_val="$computed"
    fi

    # --- Row count ---
    row_count="null"
    if [[ -f "$fpath" ]]; then
        ext="${fpath##*.}"
        ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
        case "$ext_lower" in
            csv)
                total_lines=$(wc -l < "$fpath" 2>/dev/null | tr -d ' ')
                if [[ -n "$total_lines" && "$total_lines" -gt 0 ]]; then
                    row_count=$(( total_lines - 1 ))
                fi
                ;;
            # parquet, nc, h5, hdf5, feather, arrow: leave null (binary formats)
        esac
    fi

    # --- Emit YAML record ---
    {
        printf '  - path: "%s"\n' "$fpath"
        printf '    source_system: "%s"\n' "$source_system"
        if [[ "$vintage" == "null" ]]; then
            printf '    vintage: null\n'
        else
            printf '    vintage: "%s"\n' "$vintage"
        fi
        printf '    lfs_status: %s\n' "$lfs_status"
        if [[ "$sha256_val" == "null" ]]; then
            printf '    sha256: null\n'
        else
            printf '    sha256: "%s"\n' "$sha256_val"
        fi
        printf '    row_count: %s\n' "$row_count"
        printf '    transformations: []\n'
    } >> "$OUTPUT_FILE"

done <<< "$DATA_PATHS"

echo "data-provenance: ${SESSION_TAG} — provenance written to provenance_${SESSION_TAG}.yaml"

# Cleanup temp file if we created one
[[ "$CLEANUP_TEMP" == "true" ]] && rm -f "$TRANSCRIPT" 2>/dev/null

exit 0
