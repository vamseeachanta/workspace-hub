#!/usr/bin/env bash
# update-model-ids.sh — Batch update stale AI model IDs across submodules
#
# Usage:
#   ./scripts/maintenance/update-model-ids.sh [--dry-run] [--submodule <name>] [--commit]
#
# Options:
#   --dry-run     Show what would change without modifying files
#   --submodule   Target a specific submodule (default: all)
#   --commit      Auto-commit changes inside each submodule
#   --hub-only    Only update workspace-hub level files (no submodules)
#
# Safety:
#   - Skips symlinks (sed -i destroys symlinks; see MEMORY.md)
#   - Skips .git directories and binary files
#   - Idempotent: running twice produces no additional changes
#   - Replacements ordered to avoid partial matches (e.g., gpt-4.1-mini before gpt-4.1)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUB_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ── Stale -> Latest model ID mappings ───────────────────────────────────────
# ORDER MATTERS: longer/more-specific patterns must come before shorter ones
# to avoid partial-match corruption (e.g., gpt-4.1-mini before gpt-4.1).
#
# Each entry is "old_pattern|replacement". We use fixed-string sed replacements.
# Entries are processed in array order, so gpt-4.1-mini -> gpt-4.1-mini
# is applied before gpt-4.1 -> gpt-4.1 and gpt-4.1-mini is not created
# by the gpt-4.1 replacement.
MODEL_PAIRS=(
    # Claude models — specific dated IDs first, then short aliases
    'claude-sonnet-4-20250514|claude-sonnet-4-5-20250929'
    'claude-3-haiku-20240307|claude-haiku-4-5-20251001'
    'claude-3-5-sonnet|claude-sonnet-4-5'
    # OpenAI models — order matters: longer suffixed variants before shorter stems
    # gpt-4o-mini MUST come before gpt-4o to prevent partial match corruption
    'gpt-3.5-turbo|gpt-4.1-mini'
    'gpt-4o-mini|gpt-4.1-mini'
    'gpt-4-turbo|gpt-4.1'
    'gpt-4o|gpt-4.1'
    # Gemini models
    'gemini-2.0-flash|gemini-2.5-flash'
    'gemini-2.0-pro|gemini-2.5-pro'
)

# Display name mappings (for prose/docs)
DISPLAY_PAIRS=(
    'GPT-3.5 Turbo|GPT-4.1 Mini'
    'GPT-4o Mini|GPT-4.1 Mini'
    'GPT-4 Turbo|GPT-4.1'
    'GPT-4o|GPT-4.1'
    'Gemini 2.0 Flash|Gemini 2.5 Flash'
    'Gemini 2.0 Pro|Gemini 2.5 Pro'
)

# File extensions to scan
FILE_GLOBS="*.sh *.yaml *.yml *.md *.py *.json *.toml"

# ── CLI argument parsing ────────────────────────────────────────────────────
DRY_RUN=false
TARGET_SUBMODULE=""
AUTO_COMMIT=false
HUB_ONLY=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --submodule)
            TARGET_SUBMODULE="$2"
            shift 2
            ;;
        --commit)
            AUTO_COMMIT=true
            shift
            ;;
        --hub-only)
            HUB_ONLY=true
            shift
            ;;
        -h|--help)
            sed -n '2,/^$/{ s/^# //; s/^#$//; p }' "$0"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}" >&2
            echo "Usage: $0 [--dry-run] [--submodule <name>] [--commit] [--hub-only]" >&2
            exit 1
            ;;
    esac
done

if [[ "$HUB_ONLY" == true && -n "$TARGET_SUBMODULE" ]]; then
    echo -e "${RED}Error: --hub-only and --submodule are mutually exclusive${NC}" >&2
    exit 1
fi

# ── Build grep pattern from all stale IDs ───────────────────────────────────
build_grep_pattern() {
    local pattern=""
    for pair in "${MODEL_PAIRS[@]}"; do
        local old="${pair%%|*}"
        if [[ -n "$pattern" ]]; then
            pattern="$pattern|$old"
        else
            pattern="$old"
        fi
    done
    for pair in "${DISPLAY_PAIRS[@]}"; do
        local old="${pair%%|*}"
        pattern="$pattern|$old"
    done
    echo "$pattern"
}

GREP_PATTERN="$(build_grep_pattern)"

# ── Discover target directories ─────────────────────────────────────────────
discover_targets() {
    local targets=()

    # Always include hub-level files (non-submodule)
    targets+=("workspace-hub|$HUB_ROOT")

    if [[ "$HUB_ONLY" == true ]]; then
        printf '%s\n' "${targets[@]}"
        return
    fi

    # Discover submodules via .gitmodules
    if [[ -f "$HUB_ROOT/.gitmodules" ]]; then
        while IFS= read -r line; do
            if [[ "$line" =~ path[[:space:]]*=[[:space:]]*(.*) ]]; then
                local sm_path="${BASH_REMATCH[1]}"
                local sm_name
                sm_name="$(basename "$sm_path")"
                local sm_full="$HUB_ROOT/$sm_path"

                # Filter to specific submodule if requested
                if [[ -n "$TARGET_SUBMODULE" && "$sm_name" != "$TARGET_SUBMODULE" ]]; then
                    continue
                fi

                # Only include initialized submodules (directory exists and is non-empty)
                if [[ -d "$sm_full/.git" || -f "$sm_full/.git" ]]; then
                    targets+=("$sm_name|$sm_full")
                fi
            fi
        done < "$HUB_ROOT/.gitmodules"
    fi

    if [[ -n "$TARGET_SUBMODULE" ]]; then
        # Check we actually found it
        local found=false
        for t in "${targets[@]}"; do
            if [[ "${t%%|*}" == "$TARGET_SUBMODULE" ]]; then
                found=true
                break
            fi
        done
        if [[ "$found" != true ]]; then
            echo -e "${RED}Error: submodule '$TARGET_SUBMODULE' not found or not initialized${NC}" >&2
            exit 1
        fi
    fi

    printf '%s\n' "${targets[@]}"
}

# ── Find candidate files in a directory ─────────────────────────────────────
find_candidate_files() {
    local dir="$1"
    local name_args=()

    # Build -name arguments for find
    local first=true
    for glob in $FILE_GLOBS; do
        if [[ "$first" == true ]]; then
            name_args+=( "-name" "$glob" )
            first=false
        else
            name_args+=( "-o" "-name" "$glob" )
        fi
    done

    # Find files, skip .git directories, skip binary files
    # For workspace-hub root, also skip submodule directories
    local prune_args=( "-path" "*/.git" "-prune" )

    if [[ "$dir" == "$HUB_ROOT" ]]; then
        # When scanning hub root, prune all submodule directories
        if [[ -f "$HUB_ROOT/.gitmodules" ]]; then
            while IFS= read -r line; do
                if [[ "$line" =~ path[[:space:]]*=[[:space:]]*(.*) ]]; then
                    local sm_path="${BASH_REMATCH[1]}"
                    prune_args+=( "-o" "-path" "$dir/$sm_path" "-prune" )
                fi
            done < "$HUB_ROOT/.gitmodules"
        fi
    fi

    find "$dir" \( "${prune_args[@]}" \) -o -type f \( "${name_args[@]}" \) -print 2>/dev/null
}

# ── Apply replacements to a single file ─────────────────────────────────────
process_file() {
    local file="$1"
    local file_changes=0

    # Safety: skip symlinks (sed -i destroys them)
    if [ -L "$file" ]; then
        echo -e "  ${YELLOW}SKIP (symlink):${NC} $file"
        return 0
    fi

    # Safety: skip this script itself (contains stale IDs as mapping constants)
    if [[ "$(realpath "$file")" == "$(realpath "${BASH_SOURCE[0]}")" ]]; then
        return 0
    fi

    # Skip binary files (quick heuristic: check for null bytes in first 512 bytes)
    if head -c 512 "$file" 2>/dev/null | grep -qP '\x00'; then
        return 0
    fi

    # Check if file contains any stale IDs
    if ! grep -qE "$GREP_PATTERN" "$file" 2>/dev/null; then
        return 0
    fi

    if [[ "$DRY_RUN" == true ]]; then
        echo -e "  ${CYAN}Would update:${NC} $file"
        grep -nE "$GREP_PATTERN" "$file" 2>/dev/null | while IFS= read -r match_line; do
            echo -e "    ${YELLOW}$match_line${NC}"
        done
        # Count how many replacement matches exist
        local count
        count=$(grep -cE "$GREP_PATTERN" "$file" 2>/dev/null || true)
        echo "$count"
        return 0
    fi

    # Normal mode: apply replacements via sed
    # Process model ID pairs (order matters — longer matches first)
    for pair in "${MODEL_PAIRS[@]}"; do
        local old="${pair%%|*}"
        local new="${pair#*|}"
        # Use sed with | delimiter to avoid escaping dots in model IDs
        # The dots in model IDs (e.g., gpt-4.1) are literal in the replacement
        # but act as wildcards in the pattern — escape them in the search pattern
        local escaped_old
        escaped_old=$(printf '%s' "$old" | sed 's/[.[\*^$()+?{|\\]/\\&/g')
        if grep -q "$old" "$file" 2>/dev/null; then
            sed -i "s|${escaped_old}|${new}|g" "$file"
            file_changes=$((file_changes + 1))
        fi
    done

    # Process display name pairs
    for pair in "${DISPLAY_PAIRS[@]}"; do
        local old="${pair%%|*}"
        local new="${pair#*|}"
        local escaped_old
        escaped_old=$(printf '%s' "$old" | sed 's/[.[\*^$()+?{|\\]/\\&/g')
        if grep -q "$old" "$file" 2>/dev/null; then
            sed -i "s|${escaped_old}|${new}|g" "$file"
            file_changes=$((file_changes + 1))
        fi
    done

    if [[ $file_changes -gt 0 ]]; then
        echo -e "  ${GREEN}Updated:${NC} $file ($file_changes replacement types applied)"
    fi
    echo "$file_changes"
}

# ── Process a single target directory ───────────────────────────────────────
process_target() {
    local name="$1"
    local dir="$2"
    local target_files_changed=0
    local target_replacements=0
    local commit_sha=""

    echo -e "\n${BOLD}${BLUE}[$name]${NC} $dir"

    if [[ ! -d "$dir" ]]; then
        echo -e "  ${RED}Directory not found, skipping${NC}"
        echo "0|0|"
        return
    fi

    # Find and process candidate files
    local candidates
    candidates=$(find_candidate_files "$dir")

    if [[ -z "$candidates" ]]; then
        echo -e "  ${GREEN}No candidate files found${NC}"
        echo "0|0|"
        return
    fi

    while IFS= read -r file; do
        [[ -z "$file" ]] && continue
        local result
        result=$(process_file "$file")
        if [[ -n "$result" && "$result" -gt 0 ]] 2>/dev/null; then
            target_files_changed=$((target_files_changed + 1))
            target_replacements=$((target_replacements + result))
        fi
    done <<< "$candidates"

    if [[ $target_files_changed -eq 0 ]]; then
        echo -e "  ${GREEN}No stale model IDs found${NC}"
    fi

    # Auto-commit if requested and changes were made
    if [[ "$AUTO_COMMIT" == true && "$DRY_RUN" != true && $target_files_changed -gt 0 ]]; then
        if [[ "$name" == "workspace-hub" ]]; then
            # Commit at hub level
            if cd "$HUB_ROOT" && git diff --quiet 2>/dev/null; then
                echo -e "  ${YELLOW}No uncommitted changes to commit at hub level${NC}"
            else
                git -C "$HUB_ROOT" add -A
                git -C "$HUB_ROOT" commit -m "chore: update AI model IDs to latest versions" \
                    --no-verify 2>/dev/null || true
                commit_sha=$(git -C "$HUB_ROOT" rev-parse --short HEAD 2>/dev/null || echo "unknown")
                echo -e "  ${GREEN}Committed:${NC} $commit_sha"
            fi
        else
            # Commit inside submodule
            if cd "$dir" && git diff --quiet 2>/dev/null; then
                echo -e "  ${YELLOW}No uncommitted changes to commit${NC}"
            else
                git -C "$dir" add -A
                git -C "$dir" commit -m "chore: update AI model IDs to latest versions" \
                    --no-verify 2>/dev/null || true
                commit_sha=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null || echo "unknown")
                echo -e "  ${GREEN}Committed:${NC} $commit_sha"
            fi
        fi
    fi

    echo "${target_files_changed}|${target_replacements}|${commit_sha}"
}

# ── Main ────────────────────────────────────────────────────────────────────
main() {
    echo -e "${BOLD}========================================${NC}"
    echo -e "${BOLD} AI Model ID Updater${NC}"
    echo -e "${BOLD}========================================${NC}"
    echo -e "Hub root:  $HUB_ROOT"
    echo -e "Mode:      $(if [[ "$DRY_RUN" == true ]]; then echo -e "${YELLOW}DRY RUN${NC}"; else echo -e "${GREEN}LIVE${NC}"; fi)"
    echo -e "Scope:     $(if [[ "$HUB_ONLY" == true ]]; then echo "hub-only"; elif [[ -n "$TARGET_SUBMODULE" ]]; then echo "submodule: $TARGET_SUBMODULE"; else echo "all"; fi)"
    echo -e "Commit:    $(if [[ "$AUTO_COMMIT" == true ]]; then echo "yes"; else echo "no"; fi)"
    echo ""
    echo -e "${BOLD}Stale model ID mappings:${NC}"
    for pair in "${MODEL_PAIRS[@]}"; do
        local old="${pair%%|*}"
        local new="${pair#*|}"
        echo -e "  $old  ${CYAN}->${NC}  $new"
    done
    for pair in "${DISPLAY_PAIRS[@]}"; do
        local old="${pair%%|*}"
        local new="${pair#*|}"
        echo -e "  $old  ${CYAN}->${NC}  $new"
    done

    # Collect targets
    local targets
    targets=$(discover_targets)

    # Summary accumulators
    local total_targets=0
    local total_files=0
    local total_replacements=0
    local summary_lines=()

    while IFS= read -r target_entry; do
        [[ -z "$target_entry" ]] && continue
        local name="${target_entry%%|*}"
        local dir="${target_entry#*|}"
        total_targets=$((total_targets + 1))

        # Capture the last line of output as the result (files|replacements|sha)
        local output
        output=$(process_target "$name" "$dir")

        # The result line is the last line of output
        local result_line
        result_line=$(echo "$output" | tail -1)

        # Print all lines except the last (those are the visual output)
        echo "$output" | head -n -1

        local files_changed="${result_line%%|*}"
        local rest="${result_line#*|}"
        local replacements="${rest%%|*}"
        local sha="${rest#*|}"

        total_files=$((total_files + files_changed))
        total_replacements=$((total_replacements + replacements))

        local sha_col=""
        if [[ -n "$sha" ]]; then
            sha_col="  ($sha)"
        fi
        summary_lines+=("$(printf "  %-25s %3d files  %3d replacements%s" "$name" "$files_changed" "$replacements" "$sha_col")")
    done <<< "$targets"

    # Print summary
    echo ""
    echo -e "${BOLD}========================================${NC}"
    echo -e "${BOLD} Summary${NC}"
    echo -e "${BOLD}========================================${NC}"
    for line in "${summary_lines[@]}"; do
        echo "$line"
    done
    echo -e "  ────────────────────────────────────────"
    printf "  %-25s %3d files  %3d replacements\n" "TOTAL" "$total_files" "$total_replacements"
    echo ""

    if [[ "$DRY_RUN" == true && $total_replacements -gt 0 ]]; then
        echo -e "${YELLOW}Dry run complete. Re-run without --dry-run to apply changes.${NC}"
    elif [[ $total_replacements -eq 0 ]]; then
        echo -e "${GREEN}All model IDs are already up to date.${NC}"
    else
        echo -e "${GREEN}Done. $total_files file(s) updated with $total_replacements replacement(s).${NC}"
    fi
}

main
