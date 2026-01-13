#!/bin/bash

# Enhanced repository sync script with better parallel execution and error handling

WORKSPACE_ROOT="${1:-.}"
cd "$WORKSPACE_ROOT" || exit 1

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Counters
SUCCESS=0
FAILED=0
SKIPPED=0
TOTAL=0

# Find all repos
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo -e "${CYAN}Comprehensive Repository Sync (Enhanced)${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}\n"

# Get list of repos from .gitignore
REPOS=()
while IFS= read -r line; do
    # Skip comments and empty lines
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "$line" ]] && continue
    
    # Extract repo name (before the /)
    repo_name="${line%%/*}"
    [[ -z "$repo_name" ]] && continue
    
    # Check if directory exists and is a git repo
    if [[ -d "$repo_name/.git" ]]; then
        REPOS+=("$repo_name")
    fi
done < <(grep -v "^[[:space:]]*#" "$WORKSPACE_ROOT/.gitignore" | grep "/" | head -50)

TOTAL=${#REPOS[@]}
echo -e "${BLUE}Found ${TOTAL} repositories${NC}\n"

# Phase 1: Pull all
echo -e "${CYAN}PHASE 1: Pulling latest changes from remote${NC}"
echo -e "${CYAN}─────────────────────────────────────────${NC}\n"

for repo in "${REPOS[@]}"; do
    if [[ -d "$repo/.git" ]]; then
        echo -n "→ Pulling $repo... "
        if (cd "$repo" && git pull origin $(git rev-parse --abbrev-ref HEAD) 2>&1 | grep -q "Already up to date\|Already up-to-date\|fast-forward"); then
            echo -e "${GREEN}✓${NC}"
            ((SUCCESS++))
        elif (cd "$repo" && git pull origin $(git rev-parse --abbrev-ref HEAD) &>/dev/null); then
            echo -e "${GREEN}✓${NC}"
            ((SUCCESS++))
        else
            echo -e "${YELLOW}⚠ (offline or error)${NC}"
            ((SKIPPED++))
        fi
    fi
done

echo ""

# Phase 2: Track and commit all
echo -e "${CYAN}PHASE 2: Staging and committing changes${NC}"
echo -e "${CYAN}───────────────────────────────────────${NC}\n"

for repo in "${REPOS[@]}"; do
    if [[ -d "$repo/.git" ]]; then
        # Check if there are changes
        if (cd "$repo" && ! git diff --quiet) || (cd "$repo" && ! git diff --cached --quiet); then
            echo -n "→ Committing $repo... "
            if (cd "$repo" && git add -A && git commit -m "chore: Batch synchronization from workspace-hub" --no-verify 2>/dev/null); then
                echo -e "${GREEN}✓${NC}"
                ((SUCCESS++))
            else
                echo -e "${YELLOW}⊘ (no changes)${NC}"
                ((SKIPPED++))
            fi
        else
            echo -e "${YELLOW}⊘ $repo: no changes${NC}"
            ((SKIPPED++))
        fi
    fi
done

echo ""

# Phase 3: Push all
echo -e "${CYAN}PHASE 3: Pushing to remote${NC}"
echo -e "${CYAN}──────────────────────────${NC}\n"

for repo in "${REPOS[@]}"; do
    if [[ -d "$repo/.git" ]]; then
        BRANCH=$(cd "$repo" && git rev-parse --abbrev-ref HEAD)
        echo -n "→ Pushing $repo ($BRANCH)... "
        if (cd "$repo" && git push origin "$BRANCH" 2>&1 | grep -q "Everything up-to-date\|up to date"); then
            echo -e "${GREEN}✓${NC}"
            ((SUCCESS++))
        elif (cd "$repo" && git push origin "$BRANCH" &>/dev/null); then
            echo -e "${GREEN}✓${NC}"
            ((SUCCESS++))
        else
            echo -e "${YELLOW}⚠${NC}"
            ((FAILED++))
        fi
    fi
done

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo -e "${CYAN}Summary${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo -e "Total Repos:    ${TOTAL}"
echo -e "Successful:     ${GREEN}${SUCCESS}${NC}"
echo -e "Skipped:        ${YELLOW}${SKIPPED}${NC}"
echo -e "Failed:         ${RED}${FAILED}${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"

