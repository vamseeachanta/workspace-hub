#!/bin/bash

# Deploy AI Orchestration System to All Repositories
# Syncs agent registry, scripts, and documentation to all sub-repositories

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

WORKSPACE_ROOT="/mnt/github/workspace-hub"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Deploy AI Orchestration System${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Counters
TOTAL_REPOS=0
DEPLOYED_COUNT=0
ERROR_COUNT=0

echo -e "${YELLOW}Deploying to all repositories...${NC}"
echo ""

cd "$WORKSPACE_ROOT"

for dir in */; do
    if [ -d "${dir}.git" ]; then
        ((TOTAL_REPOS++))
        REPO_NAME="${dir%/}"

        echo -e "${YELLOW}Deploying to: ${REPO_NAME}${NC}"
        cd "$dir"

        # Create directory structure
        mkdir -p modules/config
        mkdir -p modules/automation
        mkdir -p docs

        # Copy agent registry
        if cp "$WORKSPACE_ROOT/modules/config/ai-agents-registry.json" modules/config/ 2>/dev/null; then
            echo -e "${GREEN}  ✓ Copied agent registry${NC}"
        else
            echo -e "${RED}  ✗ Failed to copy agent registry${NC}"
            ((ERROR_COUNT++))
        fi

        # Copy workflow templates
        if cp "$WORKSPACE_ROOT/modules/config/workflow-templates.json" modules/config/ 2>/dev/null; then
            echo -e "${GREEN}  ✓ Copied workflow templates${NC}"
        else
            echo -e "${RED}  ✗ Failed to copy workflow templates${NC}"
            ((ERROR_COUNT++))
        fi

        # Copy automation scripts
        for script in agent_orchestrator.sh gate_pass_review.sh update_ai_agents_daily.sh; do
            if cp "$WORKSPACE_ROOT/modules/automation/$script" modules/automation/ 2>/dev/null; then
                chmod +x "modules/automation/$script"
                echo -e "${GREEN}  ✓ Copied and made executable: $script${NC}"
            else
                echo -e "${RED}  ✗ Failed to copy: $script${NC}"
                ((ERROR_COUNT++))
            fi
        done

        # Copy documentation
        if cp "$WORKSPACE_ROOT/docs/AI_AGENT_ORCHESTRATION.md" docs/ 2>/dev/null; then
            echo -e "${GREEN}  ✓ Copied orchestration documentation${NC}"
        else
            echo -e "${YELLOW}  ⚠ Skipped documentation (optional)${NC}"
        fi

        # Create symlink to workspace-hub registry (optional - for easy reference)
        if [ ! -L ".workspace-hub-registry" ]; then
            ln -s "$WORKSPACE_ROOT/modules/config/ai-agents-registry.json" .workspace-hub-registry 2>/dev/null || true
        fi

        ((DEPLOYED_COUNT++))
        cd "$WORKSPACE_ROOT"
        echo ""
    fi
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Deployment Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total repositories: ${TOTAL_REPOS}"
echo -e "${GREEN}Successfully deployed: ${DEPLOYED_COUNT}${NC}"
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo -e "${RED}Errors encountered: ${ERROR_COUNT}${NC}"
fi
echo ""

# Run initial daily update to sync everything
echo -e "${YELLOW}Running initial daily update...${NC}"
./modules/automation/update_ai_agents_daily.sh

echo ""
echo -e "${GREEN}✓ Deployment complete!${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo -e "1. Test orchestration: ./modules/automation/agent_orchestrator.sh code-generation \"Test task\""
echo -e "2. Test gate-pass review: ./modules/automation/gate_pass_review.sh specification ."
echo -e "3. View documentation: cat docs/AI_AGENT_ORCHESTRATION.md"
echo -e "4. Setup daily updates: Add to crontab (see documentation)"
