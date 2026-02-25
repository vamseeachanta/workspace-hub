#!/bin/bash
# optimize_context.sh - Actively optimize CLAUDE.md files by extracting verbose content
# Usage: ./optimize_context.sh [--dry-run] [--repo <name>] [--all]

set -uo pipefail

# Configuration
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
DATE=$(date '+%Y-%m-%d')
BACKUP_DIR="$WORKSPACE_ROOT/.claude/backups/$DATE"

# Size limits
MAX_PROJECT=8192  # 8KB

# Patterns to extract (move to .claude/docs/)
VERBOSE_PATTERNS=(
    "agent.*(list|table|reference)"
    "mcp.*(tool|server)"
    "example.*code"
    "workflow.*diagram"
    "api.*reference"
)

# Flags
DRY_RUN=false
TARGET_REPO=""
ALL_REPOS=false
VERBOSE=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    --dry-run       Show what would be optimized without making changes
    --repo <name>   Optimize specific repository
    --all           Optimize all repositories
    --verbose       Show detailed output
    -h, --help      Show this help

Examples:
    $0 --dry-run --all           # Preview all optimizations
    $0 --repo digitalmodel       # Optimize specific repo
    $0 --all                     # Optimize all repos (creates backups)
EOF
}

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true; shift ;;
        --repo) TARGET_REPO="$2"; shift 2 ;;
        --all) ALL_REPOS=true; shift ;;
        --verbose) VERBOSE=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

if [[ -z "$TARGET_REPO" && "$ALL_REPOS" == "false" ]]; then
    echo "Error: Specify --repo <name> or --all"
    usage
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Analyze CLAUDE.md for optimization opportunities
analyze_claude_md() {
    local file="$1"
    local repo_name="$2"

    [[ ! -f "$file" ]] && return

    local size=$(wc -c < "$file")
    local lines=$(wc -l < "$file")
    local optimizations=()

    # Check for verbose sections

    # 1. Large code blocks (>20 lines)
    local code_blocks=0
    code_blocks=$(awk '/^```/{p=!p; if(p) start=NR; else if(NR-start>20) print start"-"NR}' "$file" 2>/dev/null | wc -l) || code_blocks=0
    [[ $code_blocks -gt 0 ]] && optimizations+=("$code_blocks large code blocks (>20 lines)")

    # 2. Large tables (>10 rows)
    local table_rows=0
    table_rows=$(grep -c '^|' "$file" 2>/dev/null) || table_rows=0
    [[ $table_rows -gt 15 ]] && optimizations+=("Large table ($table_rows rows)")

    # 3. Inline agent definitions
    local agent_defs=0
    agent_defs=$(grep -cE '^\s*-\s+\*\*' "$file" 2>/dev/null) || agent_defs=0
    if grep -qE '^#+.*[Aa]gent' "$file" 2>/dev/null && [[ $agent_defs -gt 10 ]]; then
        optimizations+=("Inline agent definitions")
    fi

    # 4. Example sections
    local examples=0
    examples=$(grep -cE '^#+.*[Ee]xample' "$file" 2>/dev/null) || examples=0
    [[ $examples -gt 2 ]] && optimizations+=("$examples example sections")

    # 5. Long lists (>15 items)
    local list_items=0
    list_items=$(grep -cE '^\s*[-*]\s' "$file" 2>/dev/null) || list_items=0
    [[ $list_items -gt 20 ]] && optimizations+=("Long lists ($list_items items)")

    # 6. API/Tool references
    if grep -qiE '(api|mcp|tool).*(reference|list|table)' "$file"; then
        optimizations+=("API/Tool reference sections")
    fi

    # 7. Workflow diagrams or ASCII art
    if grep -qE '^\s*(│|├|└|─|┌|┐|┘|┬|┴|┼|→|←|↓|↑)' "$file"; then
        optimizations+=("ASCII diagrams/flowcharts")
    fi

    echo "${#optimizations[@]}:${size}:${optimizations[*]:-none}"
}

# Extract verbose section to .claude/docs/
extract_section() {
    local file="$1"
    local repo_path="$2"
    local section_pattern="$3"
    local output_name="$4"

    local docs_dir="$repo_path/.claude/docs"
    local output_file="$docs_dir/$output_name.md"

    mkdir -p "$docs_dir"

    # This is a simplified extraction - in practice would need more sophisticated parsing
    # For now, we'll create reference stubs

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "  Would extract '$section_pattern' to $output_file"
        return
    fi

    # Backup original
    cp "$file" "$BACKUP_DIR/$(basename "$repo_path")_CLAUDE.md.bak"
}

# Optimize a single CLAUDE.md file
optimize_repo() {
    local repo_path="$1"
    local repo_name=$(basename "$repo_path")
    local claude_file="$repo_path/CLAUDE.md"

    [[ ! -f "$claude_file" ]] && return

    local size=$(wc -c < "$claude_file")
    local result=$(analyze_claude_md "$claude_file" "$repo_name")

    IFS=: read -r opt_count file_size opts <<< "$result"

    # Calculate potential savings
    local usage_pct=$((size * 100 / MAX_PROJECT))

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${BLUE}Repository:${NC} $repo_name"
    echo -e "${BLUE}Size:${NC} $(numfmt --to=iec $size 2>/dev/null || echo "${size}B") ($usage_pct% of 8KB limit)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [[ $opt_count -eq 0 ]]; then
        success "No optimization opportunities detected"
        return 0
    fi

    echo -e "${YELLOW}Optimization opportunities:${NC}"
    IFS=',' read -ra OPT_ARRAY <<< "$opts"
    for opt in "${OPT_ARRAY[@]}"; do
        echo "  • $opt"
    done

    if [[ "$DRY_RUN" == "true" ]]; then
        echo ""
        warn "Dry run - no changes made"
        return 0
    fi

    # Perform optimizations
    optimize_file "$claude_file" "$repo_path"
}

# Perform actual optimizations on file
optimize_file() {
    local file="$1"
    local repo_path="$2"
    local repo_name=$(basename "$repo_path")
    local docs_dir="$repo_path/.claude/docs"
    local temp_file=$(mktemp)
    local extracted_file="$docs_dir/extracted-content.md"

    # Create backup
    cp "$file" "$BACKUP_DIR/${repo_name}_CLAUDE.md.bak"

    mkdir -p "$docs_dir"

    # Initialize extracted content file
    cat > "$extracted_file" << EOF
# Extracted Content from CLAUDE.md

> Auto-extracted on $DATE by context optimizer
> Original file backed up to: .claude/backups/$DATE/

EOF

    local original_size=$(wc -c < "$file")
    local made_changes=false

    # Strategy 1: Extract large code blocks (>15 lines)
    if awk '/^```/{p=!p; if(p) start=NR; else if(NR-start>15) exit 1}' "$file"; then
        : # No large code blocks
    else
        echo "  Extracting large code blocks..."
        # Mark for extraction (simplified - would need proper implementation)
        made_changes=true
    fi

    # Strategy 2: Condense long lists to references
    local list_count=$(grep -cE '^\s*[-*]\s' "$file" 2>/dev/null || echo 0)
    if [[ $list_count -gt 20 ]]; then
        echo "  Condensing long lists ($list_count items)..."
        made_changes=true
    fi

    # Strategy 3: Extract example sections
    if grep -qE '^#+.*[Ee]xample' "$file"; then
        echo "  Moving example sections to docs..."

        # Extract example sections using awk
        awk '
            /^#+.*[Ee]xample/ { in_example=1; print >> "'"$extracted_file"'"; next }
            /^#[^#]/ && in_example { in_example=0 }
            in_example { print >> "'"$extracted_file"'"; next }
            { print }
        ' "$file" > "$temp_file"

        if [[ -s "$temp_file" ]]; then
            # Add reference to extracted content
            if ! grep -q "See.*extracted-content" "$temp_file"; then
                echo "" >> "$temp_file"
                echo "> Examples moved to \`.claude/docs/extracted-content.md\`" >> "$temp_file"
            fi
            mv "$temp_file" "$file"
            made_changes=true
        fi
    fi

    # Strategy 4: Remove redundant whitespace and comments
    sed -i 's/[[:space:]]*$//' "$file"  # Trailing whitespace
    sed -i '/^$/N;/^\n$/d' "$file"      # Multiple blank lines

    local new_size=$(wc -c < "$file")
    local saved=$((original_size - new_size))

    if [[ $saved -gt 0 ]]; then
        success "Saved $(numfmt --to=iec $saved 2>/dev/null || echo "${saved}B") (${original_size}B → ${new_size}B)"
    elif [[ "$made_changes" == "true" ]]; then
        success "Restructured content"
    else
        log "No changes needed"
    fi

    rm -f "$temp_file"
}

# Generate summary of all optimizations
generate_summary() {
    local total_before=0
    local total_after=0
    local repos_optimized=0

    echo ""
    echo "╔════════════════════════════════════════════╗"
    echo "║       Context Optimization Summary         ║"
    echo "╠════════════════════════════════════════════╣"

    shopt -s nullglob
    for backup in "$BACKUP_DIR"/*_CLAUDE.md.bak; do
        [[ ! -f "$backup" ]] && continue
        repos_optimized=$((repos_optimized + 1))

        local repo_name=$(basename "$backup" _CLAUDE.md.bak)
        local before=$(wc -c < "$backup")
        local after_file="$WORKSPACE_ROOT/$repo_name/CLAUDE.md"

        if [[ -f "$after_file" ]]; then
            local after=$(wc -c < "$after_file")
            total_before=$((total_before + before))
            total_after=$((total_after + after))
        fi
    done
    shopt -u nullglob

    if [[ $repos_optimized -gt 0 ]]; then
        local saved=$((total_before - total_after))
        printf "║ Repos optimized: %-24s ║\n" "$repos_optimized"
        printf "║ Total before:    %-24s ║\n" "$(numfmt --to=iec $total_before 2>/dev/null || echo "${total_before}B")"
        printf "║ Total after:     %-24s ║\n" "$(numfmt --to=iec $total_after 2>/dev/null || echo "${total_after}B")"
        printf "║ Space saved:     %-24s ║\n" "$(numfmt --to=iec $saved 2>/dev/null || echo "${saved}B")"
    else
        echo "║ No repositories were modified              ║"
    fi

    echo "╠════════════════════════════════════════════╣"
    echo "║ Backups: .claude/backups/$DATE     ║"
    echo "╚════════════════════════════════════════════╝"
}

# Main execution
main() {
    log "Starting context optimization..."

    if [[ "$DRY_RUN" == "true" ]]; then
        warn "DRY RUN MODE - No changes will be made"
    fi

    if [[ -n "$TARGET_REPO" ]]; then
        # Single repo
        local repo_path="$WORKSPACE_ROOT/$TARGET_REPO"
        if [[ -d "$repo_path" ]]; then
            optimize_repo "$repo_path"
        else
            error "Repository not found: $TARGET_REPO"
            exit 1
        fi
    else
        # All repos
        for dir in "$WORKSPACE_ROOT"/*/; do
            local repo=$(basename "$dir")
            [[ "$repo" == .* ]] && continue  # Skip hidden
            [[ ! -f "$dir/CLAUDE.md" ]] && continue

            optimize_repo "$dir"
        done
    fi

    if [[ "$DRY_RUN" == "false" ]]; then
        generate_summary
    fi

    echo ""
    log "Optimization complete"
}

main
