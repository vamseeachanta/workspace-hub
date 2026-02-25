#!/bin/bash

# Slash Commands Propagation Script for Agent OS
# This script propagates slash commands and Agent OS configurations across all repositories

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() { echo -e "${GREEN}[✓]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_info() { echo -e "${BLUE}[i]${NC} $1"; }
print_action() { echo -e "${CYAN}[→]${NC} $1"; }

# Configuration
AGENT_OS_HOME="/home/vamsee/.agent-os"
CLAUDE_MD_HOME="/home/vamsee/.claude/CLAUDE.md"

# Files to propagate
INSTRUCTION_FILES=(
    "instructions/plan-product.md"
    "instructions/create-spec.md"
    "instructions/execute-tasks.md"
    "instructions/analyze-product.md"
)

STANDARD_FILES=(
    "standards/tech-stack.md"
    "standards/code-style.md"
    "standards/best-practices.md"
)

# Function to check if a file needs updating
needs_update() {
    local source=$1
    local dest=$2
    
    # If destination doesn't exist, needs update
    [ ! -f "$dest" ] && return 0
    
    # Compare checksums
    if command -v md5sum >/dev/null 2>&1; then
        [ "$(md5sum "$source" | cut -d' ' -f1)" != "$(md5sum "$dest" | cut -d' ' -f1)" ] && return 0
    else
        # Fallback to modification time
        [ "$source" -nt "$dest" ] && return 0
    fi
    
    return 1
}

# Function to propagate files to a repository
propagate_to_repo() {
    local repo=$1
    local updated=0
    
    echo -e "\n${BLUE}━━━ ${YELLOW}$repo${BLUE} ━━━${NC}"
    
    # Check if it's a git repository
    if [ ! -d "$repo/.git" ]; then
        print_warning "Not a git repository, skipping"
        return 1
    fi
    
    # Create .agent-os directory if it doesn't exist
    if [ ! -d "$repo/.agent-os" ]; then
        print_action "Creating .agent-os directory"
        mkdir -p "$repo/.agent-os"
        mkdir -p "$repo/.agent-os/instructions"
        mkdir -p "$repo/.agent-os/standards"
        mkdir -p "$repo/.agent-os/product"
        mkdir -p "$repo/.agent-os/specs"
        ((updated++))
    fi
    
    # Propagate instruction files
    for file in "${INSTRUCTION_FILES[@]}"; do
        source="$AGENT_OS_HOME/$file"
        dest="$repo/.agent-os/$file"
        
        if [ -f "$source" ]; then
            if needs_update "$source" "$dest"; then
                print_action "Updating $file"
                mkdir -p "$(dirname "$dest")"
                cp "$source" "$dest"
                ((updated++))
            fi
        fi
    done
    
    # Propagate standard files
    for file in "${STANDARD_FILES[@]}"; do
        source="$AGENT_OS_HOME/$file"
        dest="$repo/.agent-os/$file"
        
        if [ -f "$source" ]; then
            if needs_update "$source" "$dest"; then
                print_action "Updating $file"
                mkdir -p "$(dirname "$dest")"
                cp "$source" "$dest"
                ((updated++))
            fi
        fi
    done
    
    # Check for CLAUDE.md
    if [ ! -f "$repo/CLAUDE.md" ]; then
        print_action "Creating CLAUDE.md with Agent OS references"
        cat > "$repo/CLAUDE.md" << 'EOF'
## Agent OS Documentation

### Product Context
- **Mission & Vision:** @.agent-os/product/mission.md
- **Technical Architecture:** @.agent-os/product/tech-stack.md
- **Development Roadmap:** @.agent-os/product/roadmap.md
- **Decision History:** @.agent-os/product/decisions.md

### Development Standards
- **Code Style:** @.agent-os/standards/code-style.md
- **Best Practices:** @.agent-os/standards/best-practices.md

### Project Management
- **Active Specs:** @.agent-os/specs/
- **Spec Planning:** Use `@.agent-os/instructions/create-spec.md`
- **Tasks Execution:** Use `@.agent-os/instructions/execute-tasks.md`

## Workflow Instructions

When asked to work on this codebase:

1. **First**, check @.agent-os/product/roadmap.md for current priorities
2. **Then**, follow the appropriate instruction file:
   - For new features: @.agent-os/instructions/create-spec.md
   - For tasks execution: @.agent-os/instructions/execute-tasks.md
3. **Always**, adhere to the standards in the files listed above

## Slash Commands

- `/plan-product` - Initialize product planning
- `/create-spec` - Create a new feature specification
- `/execute-tasks` - Execute tasks from a spec
- `/analyze-product` - Analyze existing codebase

## Important Notes

- Product-specific files in `.agent-os/product/` override any global standards
- Always adhere to established patterns, code style, and best practices documented above.
EOF
        ((updated++))
    fi
    
    if [ $updated -gt 0 ]; then
        print_status "$updated file(s) updated"
        
        # Optionally commit changes
        if [ "$2" = "--commit" ]; then
            cd "$repo"
            if [ -n "$(git status --porcelain .agent-os CLAUDE.md 2>/dev/null)" ]; then
                print_action "Committing Agent OS updates"
                git add .agent-os CLAUDE.md 2>/dev/null
                git commit -m "Update Agent OS configurations and slash commands

- Propagated latest instruction files
- Updated standards and best practices
- Synchronized slash command definitions" 2>/dev/null
                cd ..
            else
                cd ..
            fi
        fi
    else
        print_info "Already up to date"
    fi
    
    return 0
}

# Function to check global Agent OS installation
check_global_installation() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}    Checking Global Agent OS Setup${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    if [ -d "$AGENT_OS_HOME" ]; then
        print_status "Global Agent OS found at $AGENT_OS_HOME"
        
        # Count files
        instructions=$(find "$AGENT_OS_HOME/instructions" -name "*.md" 2>/dev/null | wc -l)
        standards=$(find "$AGENT_OS_HOME/standards" -name "*.md" 2>/dev/null | wc -l)
        
        print_info "Found $instructions instruction files"
        print_info "Found $standards standard files"
    else
        print_error "Global Agent OS not found at $AGENT_OS_HOME"
        return 1
    fi
    
    if [ -f "$CLAUDE_MD_HOME" ]; then
        print_status "Global CLAUDE.md found"
    else
        print_warning "Global CLAUDE.md not found"
    fi
    
    echo ""
    return 0
}

# Main execution
main() {
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}    Agent OS Slash Commands Propagator${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Check global installation
    if ! check_global_installation; then
        print_error "Please ensure Agent OS is properly installed globally"
        exit 1
    fi
    
    # Parse arguments
    COMMIT_CHANGES=false
    DRY_RUN=false
    
    for arg in "$@"; do
        case $arg in
            --commit|-c)
                COMMIT_CHANGES=true
                print_info "Will commit changes to git"
                ;;
            --dry-run|-d)
                DRY_RUN=true
                print_info "Dry run mode - no changes will be made"
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --commit, -c    Commit changes to git"
                echo "  --dry-run, -d   Show what would be changed without making changes"
                echo "  --help, -h      Show this help message"
                echo ""
                exit 0
                ;;
        esac
    done
    
    # Count repositories
    total_repos=$(find . -maxdepth 2 -type d -name ".git" 2>/dev/null | wc -l)
    print_info "Found $total_repos git repositories to process"
    echo ""
    
    # Process each repository
    processed=0
    updated=0
    
    for dir in */; do
        if [ -d "$dir/.git" ]; then
            if [ "$DRY_RUN" = true ]; then
                echo -e "\n${BLUE}━━━ ${YELLOW}$dir${BLUE} (DRY RUN) ━━━${NC}"
                print_info "Would check for updates..."
            else
                if propagate_to_repo "$dir" "$( [ "$COMMIT_CHANGES" = true ] && echo "--commit" )"; then
                    ((processed++))
                fi
            fi
        fi
    done
    
    # Summary
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}    Summary${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if [ "$DRY_RUN" = true ]; then
        print_info "Dry run completed - no changes made"
    else
        print_status "Processed $processed repositories"
        
        # Show which repos have Agent OS
        echo ""
        echo "Repositories with Agent OS:"
        for dir in */; do
            if [ -d "$dir/.agent-os" ]; then
                echo "  ${GREEN}✓${NC} $dir"
            fi
        done
    fi
    
    echo ""
    print_info "Propagation complete!"
    
    # Provide usage tips
    echo ""
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${MAGENTA}    Available Slash Commands:${NC}"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "  /plan-product    - Initialize a new product with Agent OS"
    echo "  /create-spec     - Create a feature specification"
    echo "  /execute-tasks   - Execute tasks from a spec"
    echo "  /analyze-product - Analyze and retrofit existing codebase"
    echo ""
}

# Run the main function
main "$@"