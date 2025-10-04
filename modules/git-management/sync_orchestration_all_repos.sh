#!/bin/bash

# Sync AI Orchestration System to All Repositories and Commit
# Deploys orchestration files and commits changes in each repository

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

WORKSPACE_ROOT="/mnt/github/workspace-hub"
PUSH_TO_REMOTE=${1:-false}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Sync AI Orchestration System${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Counters
TOTAL_REPOS=0
SYNCED_COUNT=0
COMMITTED_COUNT=0
PUSHED_COUNT=0
ERROR_COUNT=0

cd "$WORKSPACE_ROOT"

for dir in */; do
    if [ -d "${dir}.git" ]; then
        ((TOTAL_REPOS++))
        REPO_NAME="${dir%/}"

        echo -e "${YELLOW}Processing: ${REPO_NAME}${NC}"
        cd "$dir"

        # Create directory structure
        mkdir -p modules/config modules/automation docs

        # Copy agent registry
        cp "$WORKSPACE_ROOT/modules/config/ai-agents-registry.json" modules/config/ 2>/dev/null || {
            echo -e "${RED}  ✗ Failed to copy agent registry${NC}"
            ((ERROR_COUNT++))
            cd "$WORKSPACE_ROOT"
            continue
        }

        # Copy workflow templates
        cp "$WORKSPACE_ROOT/modules/config/workflow-templates.json" modules/config/ 2>/dev/null

        # Copy automation scripts
        for script in agent_orchestrator.sh gate_pass_review.sh update_ai_agents_daily.sh; do
            if cp "$WORKSPACE_ROOT/modules/automation/$script" modules/automation/ 2>/dev/null; then
                chmod +x "modules/automation/$script"
            fi
        done

        # Copy documentation
        cp "$WORKSPACE_ROOT/docs/AI_AGENT_ORCHESTRATION.md" docs/ 2>/dev/null || true

        ((SYNCED_COUNT++))
        echo -e "${GREEN}  ✓ Files synced${NC}"

        # Check if there are changes to commit
        if [[ -n $(git status --porcelain) ]]; then
            # Stage orchestration files
            git add modules/config/ai-agents-registry.json \
                    modules/config/workflow-templates.json \
                    modules/automation/*.sh \
                    docs/AI_AGENT_ORCHESTRATION.md 2>/dev/null || true

            # Commit changes
            if git commit -m "Add AI Agent Orchestration System

- Intelligent agent selection for optimal task execution
- Gate-pass reviews at SPARC checkpoints
- Daily capability updates for all agents
- Integration with factory.ai, claude-flow, spec-kit, agent-os

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>" 2>/dev/null; then
                echo -e "${GREEN}  ✓ Committed${NC}"
                ((COMMITTED_COUNT++))

                # Push if requested
                if [ "$PUSH_TO_REMOTE" = "push" ]; then
                    if git push 2>/dev/null; then
                        echo -e "${GREEN}  ✓ Pushed to remote${NC}"
                        ((PUSHED_COUNT++))
                    else
                        echo -e "${YELLOW}  ⚠ Could not push${NC}"
                    fi
                fi
            else
                echo -e "${YELLOW}  → No changes to commit${NC}"
            fi
        else
            echo -e "${BLUE}  → No changes${NC}"
        fi

        cd "$WORKSPACE_ROOT"
        echo ""
    fi
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total repositories: ${TOTAL_REPOS}"
echo -e "${GREEN}Files synced: ${SYNCED_COUNT}${NC}"
echo -e "${GREEN}Committed: ${COMMITTED_COUNT}${NC}"
if [ "$PUSH_TO_REMOTE" = "push" ]; then
    echo -e "${GREEN}Pushed: ${PUSHED_COUNT}${NC}"
fi
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo -e "${RED}Errors: ${ERROR_COUNT}${NC}"
fi
echo ""

if [ "$PUSH_TO_REMOTE" != "push" ]; then
    echo -e "${YELLOW}Changes committed but NOT pushed to remote.${NC}"
    echo -e "${YELLOW}To push, run: $0 push${NC}"
fi

echo -e "${GREEN}✓ Orchestration system sync complete!${NC}"
