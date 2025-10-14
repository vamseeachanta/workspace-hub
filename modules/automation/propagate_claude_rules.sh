#!/bin/bash
# ABOUTME: Propagates unified Claude rules to all managed repositories
# ABOUTME: Integrates obra's engineering principles with SPARC orchestration

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLAUDE_RULES_SOURCE="$WORKSPACE_ROOT/CLAUDE.md"
BACKUP_SUFFIX=".backup-$(date +%Y%m%d-%H%M%S)"

# Usage information
usage() {
    cat <<EOF
Usage: $0 [OPTIONS] [REPOSITORY_PATH...]

Propagate unified Claude rules to specified repositories or all managed repos.

OPTIONS:
    -h, --help              Show this help message
    -a, --all               Propagate to all managed repositories
    -d, --dry-run           Show what would be done without making changes
    -f, --force             Overwrite existing CLAUDE.md without prompting
    -b, --backup            Create backup before overwriting (default: true)
    --no-backup             Skip backup creation
    -v, --verbose           Verbose output

EXAMPLES:
    # Propagate to specific repository
    $0 /path/to/repo

    # Propagate to all managed repositories (interactive)
    $0 --all

    # Dry run to see what would change
    $0 --all --dry-run

    # Force overwrite with backups
    $0 --all --force --backup

DESCRIPTION:
    This script propagates the unified Claude rules (combining obra's engineering
    principles with SPARC orchestration) to repository CLAUDE.md files.

    The unified rules include:
    - Part 1: Core Engineering Principles (TDD, YAGNI, debugging, collaboration)
    - Part 2: AI Orchestration (SPARC methodology, agent coordination)
    - Part 3: Project-Specific Context (Agent OS, product docs)

    Files updated:
    - CLAUDE.md (root)
    - .claude/CLAUDE.md (if .claude/ directory exists)

EOF
    exit 0
}

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# Check if source rules file exists
check_source_rules() {
    if [[ ! -f "$CLAUDE_RULES_SOURCE" ]]; then
        log_error "Source CLAUDE.md not found at: $CLAUDE_RULES_SOURCE"
        log_error "Please ensure workspace-hub has the unified rules template."
        exit 1
    fi

    # Verify it contains all three parts
    if ! grep -q "# PART 1: CORE ENGINEERING PRINCIPLES" "$CLAUDE_RULES_SOURCE" || \
       ! grep -q "# PART 2: AI ORCHESTRATION & SPARC METHODOLOGY" "$CLAUDE_RULES_SOURCE" || \
       ! grep -q "# PART 3: PROJECT-SPECIFIC CONTEXT" "$CLAUDE_RULES_SOURCE"; then
        log_error "Source CLAUDE.md is missing required sections"
        log_error "Expected: Part 1 (Engineering), Part 2 (Orchestration), Part 3 (Context)"
        exit 1
    fi

    log_success "Verified unified Claude rules source"
}

# Get all git repositories
get_all_repositories() {
    local repos=()
    while IFS= read -r -d '' git_dir; do
        repo_path="$(dirname "$git_dir")"
        # Skip the workspace-hub root itself, but include all nested repos
        if [[ "$repo_path" != "$WORKSPACE_ROOT" ]]; then
            repos+=("$repo_path")
        fi
    done < <(find "$WORKSPACE_ROOT" -type d -name .git -print0 2>/dev/null)

    printf '%s\n' "${repos[@]}"
}

# Backup existing file
backup_file() {
    local file="$1"
    local backup="${file}${BACKUP_SUFFIX}"

    if [[ -f "$file" ]]; then
        cp "$file" "$backup"
        log_info "Backed up: $backup"
        return 0
    fi
    return 1
}

# Propagate rules to a single repository
propagate_to_repo() {
    local repo_path="$1"
    local dry_run="${2:-false}"
    local force="${3:-false}"
    local create_backup="${4:-true}"

    log_info "Processing: $repo_path"

    # Skip if not a valid git repository
    if [[ ! -d "$repo_path/.git" ]]; then
        log_warning "Not a git repository, skipping: $repo_path"
        return 1
    fi

    # Target files
    local target_root="$repo_path/CLAUDE.md"
    local target_claude="$repo_path/.claude/CLAUDE.md"

    # Check if files already exist
    local root_exists=false
    local claude_exists=false
    [[ -f "$target_root" ]] && root_exists=true
    [[ -f "$target_claude" ]] && claude_exists=true

    # Dry run mode
    if [[ "$dry_run" == "true" ]]; then
        if [[ "$root_exists" == "true" ]]; then
            log_info "Would update: $target_root"
        else
            log_info "Would create: $target_root"
        fi

        if [[ -d "$repo_path/.claude" ]]; then
            if [[ "$claude_exists" == "true" ]]; then
                log_info "Would update: $target_claude"
            else
                log_info "Would create: $target_claude"
            fi
        fi
        return 0
    fi

    # Interactive confirmation if files exist and not forced
    if [[ "$force" != "true" ]] && [[ "$root_exists" == "true" ]]; then
        read -p "Overwrite $target_root? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_warning "Skipped: $target_root"
            return 0
        fi
    fi

    # Create backup if requested
    if [[ "$create_backup" == "true" ]] && [[ "$root_exists" == "true" ]]; then
        backup_file "$target_root"
    fi

    # Copy to root
    cp "$CLAUDE_RULES_SOURCE" "$target_root"
    log_success "Updated: $target_root"

    # Copy to .claude/ if directory exists
    if [[ -d "$repo_path/.claude" ]]; then
        if [[ "$create_backup" == "true" ]] && [[ "$claude_exists" == "true" ]]; then
            backup_file "$target_claude"
        fi

        cp "$CLAUDE_RULES_SOURCE" "$target_claude"
        log_success "Updated: $target_claude"
    fi

    return 0
}

# Main execution
main() {
    local propagate_all=false
    local dry_run=false
    local force=false
    local create_backup=true
    local verbose=false
    local repos=()

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                ;;
            -a|--all)
                propagate_all=true
                shift
                ;;
            -d|--dry-run)
                dry_run=true
                shift
                ;;
            -f|--force)
                force=true
                shift
                ;;
            -b|--backup)
                create_backup=true
                shift
                ;;
            --no-backup)
                create_backup=false
                shift
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -*)
                log_error "Unknown option: $1"
                usage
                ;;
            *)
                repos+=("$1")
                shift
                ;;
        esac
    done

    # Header
    echo
    log_info "====================================="
    log_info "Claude Rules Propagation Script"
    log_info "====================================="
    echo

    # Check source rules
    check_source_rules
    echo

    # Get repositories to process
    if [[ "$propagate_all" == "true" ]]; then
        log_info "Finding all managed repositories..."
        mapfile -t repos < <(get_all_repositories)
        log_info "Found ${#repos[@]} repositories"
    elif [[ ${#repos[@]} -eq 0 ]]; then
        log_error "No repositories specified"
        log_info "Use --all to propagate to all repos, or provide paths"
        usage
    fi

    # Dry run notification
    if [[ "$dry_run" == "true" ]]; then
        log_warning "DRY RUN MODE - No changes will be made"
        echo
    fi

    # Process each repository
    local success_count=0
    local skip_count=0
    local error_count=0

    for repo in "${repos[@]}"; do
        if propagate_to_repo "$repo" "$dry_run" "$force" "$create_backup"; then
            ((success_count++))
        else
            if [[ $? -eq 1 ]]; then
                ((skip_count++))
            else
                ((error_count++))
            fi
        fi
        echo
    done

    # Summary
    log_info "====================================="
    log_info "Summary"
    log_info "====================================="
    log_success "Successfully processed: $success_count"
    [[ $skip_count -gt 0 ]] && log_warning "Skipped: $skip_count"
    [[ $error_count -gt 0 ]] && log_error "Errors: $error_count"
    echo

    if [[ "$dry_run" == "true" ]]; then
        log_info "This was a dry run. Rerun without --dry-run to apply changes."
    fi

    if [[ $error_count -gt 0 ]]; then
        exit 1
    fi
}

# Run main function
main "$@"
