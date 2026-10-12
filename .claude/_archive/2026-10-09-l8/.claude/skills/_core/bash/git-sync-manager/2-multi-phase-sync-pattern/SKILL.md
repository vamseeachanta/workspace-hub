---
name: git-sync-manager-2-multi-phase-sync-pattern
description: 'Sub-skill of git-sync-manager: 2. Multi-Phase Sync Pattern.'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# 2. Multi-Phase Sync Pattern

## 2. Multi-Phase Sync Pattern


Execute git operations in ordered phases:

```bash
#!/bin/bash
# ABOUTME: Multi-phase git synchronization
# ABOUTME: Executes pull → commit → push in controlled phases

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Counters
SUCCESS=0
FAILED=0
SKIPPED=0

# ─────────────────────────────────────────────────────────────────
# Phase 1: Pull
# ─────────────────────────────────────────────────────────────────

phase_pull() {
    local repos=("$@")

    echo -e "${CYAN}PHASE 1: Pulling latest changes${NC}"
    echo -e "${CYAN}─────────────────────────────────${NC}"

    for repo in "${repos[@]}"; do
        if [[ -d "$repo/.git" ]]; then
            echo -n "→ Pulling $repo... "

            local branch
            branch=$(cd "$repo" && git rev-parse --abbrev-ref HEAD 2>/dev/null)

            if (cd "$repo" && git pull origin "$branch" 2>&1 | grep -qE "Already up.to" ); then
                echo -e "${GREEN}✓ (up to date)${NC}"
                ((SUCCESS++))
            elif (cd "$repo" && git pull origin "$branch" &>/dev/null); then
                echo -e "${GREEN}✓ (updated)${NC}"
                ((SUCCESS++))
            else
                echo -e "${YELLOW}⚠ (offline or error)${NC}"
                ((SKIPPED++))
            fi
        fi
    done
}

# ─────────────────────────────────────────────────────────────────
# Phase 2: Commit
# ─────────────────────────────────────────────────────────────────

phase_commit() {
    local repos=("$@")
    local message="${COMMIT_MESSAGE:-chore: Batch synchronization}"

    echo -e "\n${CYAN}PHASE 2: Staging and committing changes${NC}"
    echo -e "${CYAN}───────────────────────────────────────${NC}"

    for repo in "${repos[@]}"; do
        if [[ -d "$repo/.git" ]]; then
            # Check for changes (staged or unstaged)
            local has_changes=false

            if ! (cd "$repo" && git diff --quiet 2>/dev/null); then
                has_changes=true
            fi
            if ! (cd "$repo" && git diff --cached --quiet 2>/dev/null); then
                has_changes=true
            fi

            if [[ "$has_changes" == "true" ]]; then
                echo -n "→ Committing $repo... "

                if (cd "$repo" && git add -A && git commit -m "$message" --no-verify 2>/dev/null); then
                    echo -e "${GREEN}✓${NC}"
                    ((SUCCESS++))
                else
                    echo -e "${YELLOW}⊘ (commit failed)${NC}"
                    ((SKIPPED++))
                fi
            else
                echo -e "${YELLOW}⊘ $repo: no changes${NC}"
                ((SKIPPED++))
            fi
        fi
    done
}

# ─────────────────────────────────────────────────────────────────
# Phase 3: Push
# ─────────────────────────────────────────────────────────────────

phase_push() {
    local repos=("$@")

    echo -e "\n${CYAN}PHASE 3: Pushing to remote${NC}"
    echo -e "${CYAN}──────────────────────────${NC}"

    for repo in "${repos[@]}"; do
        if [[ -d "$repo/.git" ]]; then
            local branch
            branch=$(cd "$repo" && git rev-parse --abbrev-ref HEAD 2>/dev/null)

            echo -n "→ Pushing $repo ($branch)... "

            if (cd "$repo" && git push origin "$branch" 2>&1 | grep -qE "Everything up-to-date|up to date"); then
                echo -e "${GREEN}✓ (up to date)${NC}"
                ((SUCCESS++))
            elif (cd "$repo" && git push origin "$branch" &>/dev/null); then
                echo -e "${GREEN}✓ (pushed)${NC}"
                ((SUCCESS++))
            else
                echo -e "${RED}✗${NC}"
                ((FAILED++))
            fi
        fi
    done
}

# ─────────────────────────────────────────────────────────────────
# Full Sync
# ─────────────────────────────────────────────────────────────────

full_sync() {
    local repos=("$@")

    phase_pull "${repos[@]}"
    phase_commit "${repos[@]}"
    phase_push "${repos[@]}"

    # Summary
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════${NC}"
    echo -e "${CYAN}Summary${NC}"
    echo -e "${CYAN}═══════════════════════════════════════${NC}"
    echo -e "Total Repos:    ${#repos[@]}"
    echo -e "Successful:     ${GREEN}${SUCCESS}${NC}"
    echo -e "Skipped:        ${YELLOW}${SKIPPED}${NC}"
    echo -e "Failed:         ${RED}${FAILED}${NC}"
}
```
