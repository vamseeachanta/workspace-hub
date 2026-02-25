#!/bin/bash

# Git Sync Script for All Repositories
# This script syncs all git repositories in the current directory
# Primarily focuses on propagating Agent OS slash commands and configurations

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# Function to sync a single repository
sync_repo() {
    local repo=$1
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Processing: ${YELLOW}$repo${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    cd "$repo" || {
        print_error "Cannot enter $repo"
        return 1
    }
    
    # Check if it's a git repository
    if [ ! -d .git ]; then
        print_warning "$repo is not a git repository, skipping"
        cd ..
        return 1
    fi
    
    # Store current branch
    current_branch=$(git branch --show-current 2>/dev/null)
    
    # Stash any uncommitted changes
    if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
        print_info "Stashing uncommitted changes..."
        git stash push -m "Auto-stash before sync $(date +%Y-%m-%d_%H:%M:%S)" >/dev/null 2>&1
        stashed=true
    else
        stashed=false
    fi
    
    # Fetch all remotes
    print_info "Fetching from remote..."
    git fetch --all --prune 2>/dev/null || print_warning "Fetch failed or no remote"
    
    # Determine main branch (main or master)
    if git show-ref --verify --quiet refs/heads/main; then
        main_branch="main"
    elif git show-ref --verify --quiet refs/heads/master; then
        main_branch="master"
    else
        print_warning "No main/master branch found"
        cd ..
        return 1
    fi
    
    # Pull latest changes from main branch
    if [ "$current_branch" = "$main_branch" ]; then
        print_info "Pulling latest changes from $main_branch..."
        git pull origin "$main_branch" 2>/dev/null || print_warning "Pull failed or no changes"
    else
        print_info "Not on $main_branch branch (current: $current_branch), skipping pull"
    fi
    
    # Check for Agent OS configurations to propagate
    if [ -d ".agent-os" ]; then
        print_status "Agent OS configuration found"
        
        # Check if there are any uncommitted Agent OS changes
        if git status .agent-os --porcelain 2>/dev/null | grep -q .; then
            print_info "Agent OS changes detected"
        fi
    fi
    
    # Restore stashed changes if any
    if [ "$stashed" = true ]; then
        print_info "Restoring stashed changes..."
        git stash pop >/dev/null 2>&1 || print_warning "Could not restore stash cleanly"
    fi
    
    # Show repository status
    uncommitted=$(git status --porcelain 2>/dev/null | wc -l)
    if [ "$uncommitted" -gt 0 ]; then
        print_warning "$uncommitted uncommitted change(s)"
    else
        print_status "Working tree clean"
    fi
    
    # Check if we're ahead or behind remote
    if [ -n "$current_branch" ]; then
        ahead=$(git rev-list --count @{u}..@ 2>/dev/null || echo "0")
        behind=$(git rev-list --count @..@{u} 2>/dev/null || echo "0")
        
        if [ "$ahead" -gt 0 ]; then
            print_warning "Branch is $ahead commit(s) ahead of remote"
        fi
        if [ "$behind" -gt 0 ]; then
            print_warning "Branch is $behind commit(s) behind remote"
        fi
    fi
    
    cd ..
    return 0
}

# Function to propagate Agent OS configurations
propagate_agent_os() {
    print_info "Checking for Agent OS configurations to propagate..."
    
    # Source directories for Agent OS configurations
    local source_dirs=(
        "/home/vamsee/.agent-os"
        ".agent-os"
    )
    
    # Check if we should propagate
    for source in "${source_dirs[@]}"; do
        if [ -d "$source" ]; then
            print_status "Found Agent OS source at $source"
            
            # Find all repositories with .agent-os directories
            for repo in */; do
                if [ -d "$repo/.git" ] && [ -d "$repo/.agent-os" ]; then
                    print_info "Checking $repo for Agent OS updates..."
                    
                    # Here you can add specific file propagation logic
                    # For example, copying instruction files that should be synchronized
                fi
            done
        fi
    done
}

# Main execution
main() {
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}    Git Repository Sync Tool${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Count repositories
    total_repos=$(find . -maxdepth 2 -type d -name ".git" 2>/dev/null | wc -l)
    print_info "Found $total_repos git repositories"
    
    # Process each repository
    processed=0
    failed=0
    
    for dir in */; do
        if [ -d "$dir/.git" ]; then
            if sync_repo "$dir"; then
                ((processed++))
            else
                ((failed++))
            fi
        fi
    done
    
    # Propagate Agent OS configurations if requested
    if [ "$1" = "--propagate" ] || [ "$1" = "-p" ]; then
        echo ""
        propagate_agent_os
    fi
    
    # Summary
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}    Summary${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    print_status "Successfully processed: $processed repositories"
    if [ "$failed" -gt 0 ]; then
        print_warning "Failed/Skipped: $failed repositories"
    fi
    echo ""
    
    # Show repositories with uncommitted changes
    echo "Repositories with uncommitted changes:"
    for dir in */; do
        if [ -d "$dir/.git" ]; then
            cd "$dir"
            if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
                changes=$(git status --porcelain 2>/dev/null | wc -l)
                echo "  • $dir ($changes changes)"
            fi
            cd ..
        fi
    done
    
    echo ""
    print_info "Sync complete!"
}

# Run the main function
main "$@"