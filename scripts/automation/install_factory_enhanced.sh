#!/bin/bash

# Factory.ai Enhanced Installation Script
# Deploys droids.yml configurations and enhanced config across all repositories
# Version: 2.0.0

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

WORKSPACE_ROOT="/mnt/github/workspace-hub"
TEMPLATE="$WORKSPACE_ROOT/.drcode/droids-repo-template.yml"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Factory.ai Enhanced Configuration${NC}"
echo -e "${BLUE}Version 2.0.0${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Verify prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v droid &> /dev/null; then
    echo -e "${RED}✗ Droid CLI not installed${NC}"
    echo -e "${YELLOW}Install with: curl -fsSL https://app.factory.ai/cli | sh${NC}"
    exit 1
fi

if [ ! -f "$WORKSPACE_ROOT/.drcode/droids.yml" ]; then
    echo -e "${RED}✗ Workspace droids.yml not found${NC}"
    exit 1
fi

if [ ! -f "$TEMPLATE" ]; then
    echo -e "${RED}✗ Repository template not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Droid CLI v$(droid --version)${NC}"
echo -e "${GREEN}✓ Workspace droids.yml found${NC}"
echo -e "${GREEN}✓ Repository template found${NC}"
echo ""

# Repository type mappings. The values carried client repo names + descriptions
# (#3098), so the map is no longer hardcoded. It is loaded from a gitignored
# per-host file ($REPO_TYPES_FILE or workspace-hub/config/.repo-types.local),
# one entry per line, pipe-delimited:
#     <repo>|<type>|<focus label>|<key tech>
# ('#' comments and blank lines ignored). See config/.repo-types.local.example.
# The value is reassembled to the original "type:focus:tech" colon form so the
# downstream `IFS=':' read` parsing is unchanged. Absent file -> empty map ->
# the per-repo loop processes nothing (safe no-op).
declare -A REPO_TYPES
_rt_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
_types_file="${REPO_TYPES_FILE:-$_rt_root/config/.repo-types.local}"
if [[ -f "$_types_file" ]]; then
    while IFS='|' read -r _repo _type _focus _tech; do
        [[ -z "$_repo" || "$_repo" == \#* ]] && continue
        REPO_TYPES["$_repo"]="${_type}:${_focus}:${_tech}"
    done < "$_types_file"
fi

# Counters
SUCCESS_COUNT=0
UPDATE_COUNT=0
ERROR_COUNT=0

# Deploy enhanced configuration to workspace-hub root
echo -e "${YELLOW}Deploying enhanced workspace configuration...${NC}"

if [ -f "$WORKSPACE_ROOT/.drcode/config-enhanced.json" ]; then
    echo -e "${GREEN}  ✓ Enhanced config.json already exists${NC}"
else
    echo -e "${RED}  ✗ Enhanced config.json not found${NC}"
    ((ERROR_COUNT++))
fi

if [ -f "$WORKSPACE_ROOT/.drcode/droids.yml" ]; then
    DROIDS_SIZE=$(wc -c < "$WORKSPACE_ROOT/.drcode/droids.yml")
    echo -e "${GREEN}  ✓ Workspace droids.yml deployed (${DROIDS_SIZE} bytes)${NC}"
else
    echo -e "${RED}  ✗ Workspace droids.yml missing${NC}"
    ((ERROR_COUNT++))
fi

echo ""
echo -e "${YELLOW}Deploying repository configurations...${NC}"
echo ""

# Process each repository
for repo in "${!REPO_TYPES[@]}"; do
    REPO_PATH="$WORKSPACE_ROOT/$repo/.drcode"

    if [ ! -d "$REPO_PATH" ]; then
        echo -e "${YELLOW}$repo${NC}"
        echo -e "${RED}  ✗ .drcode directory not found${NC}"
        echo -e "${BLUE}  → Run install_factory_all_repos.sh first${NC}"
        ((ERROR_COUNT++))
        echo ""
        continue
    fi

    # Parse repo type info
    IFS=':' read -r REPO_TYPE REPO_FOCUS KEY_TECH <<< "${REPO_TYPES[$repo]}"

    echo -e "${YELLOW}$repo${NC} (${REPO_TYPE})"

    # Check if droids.yml exists
    if [ -f "$REPO_PATH/droids.yml" ]; then
        DROIDS_SIZE=$(wc -c < "$REPO_PATH/droids.yml")
        echo -e "${GREEN}  ✓ droids.yml exists (${DROIDS_SIZE} bytes)${NC}"
        ((UPDATE_COUNT++))
    else
        # Create droids.yml from template
        sed -e "s/__REPO_NAME__/$repo/g" \
            -e "s/__REPO_TYPE__/$REPO_TYPE/g" \
            -e "s/__REPO_FOCUS__/${REPO_FOCUS}/g" \
            -e "s/__KEY_TECH__/${KEY_TECH}/g" \
            "$TEMPLATE" > "$REPO_PATH/droids.yml"

        if [ -f "$REPO_PATH/droids.yml" ]; then
            DROIDS_SIZE=$(wc -c < "$REPO_PATH/droids.yml")
            echo -e "${GREEN}  ✓ droids.yml created (${DROIDS_SIZE} bytes)${NC}"
            ((SUCCESS_COUNT++))
        else
            echo -e "${RED}  ✗ Failed to create droids.yml${NC}"
            ((ERROR_COUNT++))
        fi
    fi

    # Verify config.json exists
    if [ -f "$REPO_PATH/config.json" ]; then
        echo -e "${BLUE}  → config.json exists${NC}"
    else
        echo -e "${RED}  ✗ config.json missing${NC}"
        ((ERROR_COUNT++))
    fi

    echo ""
done

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Deployment Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Newly created droids.yml: ${SUCCESS_COUNT}${NC}"
echo -e "${BLUE}Already configured: ${UPDATE_COUNT}${NC}"
echo -e "${RED}Errors: ${ERROR_COUNT}${NC}"
echo ""

# Repository type breakdown
PYTHON_COUNT=0
WEB_COUNT=0
ENG_COUNT=0

for type_info in "${REPO_TYPES[@]}"; do
    IFS=':' read -r REPO_TYPE _ _ <<< "$type_info"
    case "$REPO_TYPE" in
        python_analysis) ((PYTHON_COUNT++)) ;;
        web_app) ((WEB_COUNT++)) ;;
        engineering) ((ENG_COUNT++)) ;;
    esac
done

echo -e "${BLUE}Repository Types:${NC}"
echo -e "  Python Analysis: ${PYTHON_COUNT}"
echo -e "  Web Applications: ${WEB_COUNT}"
echo -e "  Engineering: ${ENG_COUNT}"
echo ""

if [ $ERROR_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ Enhanced Factory.ai configuration deployed successfully!${NC}"
else
    echo -e "${YELLOW}⚠ Deployment completed with ${ERROR_COUNT} errors${NC}"
fi

echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo -e "  1. Review: ${YELLOW}docs/FACTORY_AI_ENHANCED_GUIDE.md${NC}"
echo -e "  2. Test: ${YELLOW}cd worldenergydata && droid exec 'test'${NC}"
echo -e "  3. Use specialized droids: ${YELLOW}droid --droid feature exec 'add feature'${NC}"
echo ""
echo -e "${BLUE}Integration:${NC}"
echo -e "  • AI Orchestration: ${YELLOW}modules/automation/agent_orchestrator.sh${NC}"
echo -e "  • Gate-Pass Reviews: ${YELLOW}modules/automation/gate_pass_review.sh${NC}"
echo -e "  • Agent Registry: ${YELLOW}modules/config/ai-agents-registry.json${NC}"
echo ""
