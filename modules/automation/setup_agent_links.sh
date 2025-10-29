#!/bin/bash

# ABOUTME: Setup agent symlinks for cross-repository agent referencing
# ABOUTME: Creates symlinks from consumer repos to workspace-hub universal agents and domain hub agents

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

WORKSPACE_ROOT="/mnt/github/workspace-hub"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Usage
usage() {
    echo "Usage: $0 <target-repo-path> [options]"
    echo ""
    echo "Setup agent symlinks for a repository"
    echo ""
    echo "Arguments:"
    echo "  target-repo-path    Path to target repository (absolute or relative)"
    echo ""
    echo "Options:"
    echo "  --dry-run           Show what would be done without making changes"
    echo "  --force             Overwrite existing symlinks"
    echo "  --universal-only    Only setup universal agent links"
    echo "  --verbose           Detailed output"
    echo ""
    echo "Examples:"
    echo "  $0 /mnt/github/aceengineer-admin"
    echo "  $0 ../aceengineercode --dry-run"
    echo "  $0 /mnt/github/client_projects --universal-only"
    exit 1
}

# Check arguments
if [ $# -lt 1 ]; then
    usage
fi

TARGET_REPO="$1"
DRY_RUN=false
FORCE=false
UNIVERSAL_ONLY=false
VERBOSE=false

# Parse options
shift
while [ $# -gt 0 ]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            ;;
        --force)
            FORCE=true
            ;;
        --universal-only)
            UNIVERSAL_ONLY=true
            ;;
        --verbose)
            VERBOSE=true
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
    shift
done

# Validate target repo
if [ ! -d "$TARGET_REPO" ]; then
    echo -e "${RED}✗ Target repository not found: $TARGET_REPO${NC}"
    exit 1
fi

# Convert to absolute path
TARGET_REPO=$(cd "$TARGET_REPO" && pwd)
REPO_NAME=$(basename "$TARGET_REPO")

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Agent Symlink Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${BLUE}Target Repository:${NC} $REPO_NAME"
echo -e "${BLUE}Target Path:${NC} $TARGET_REPO"
echo -e "${BLUE}Workspace Root:${NC} $WORKSPACE_ROOT"
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}Mode: DRY RUN (no changes will be made)${NC}"
fi
echo ""

# Check if .agent-references.yaml exists
REFERENCES_FILE="$TARGET_REPO/.agent-references.yaml"
if [ ! -f "$REFERENCES_FILE" ]; then
    echo -e "${YELLOW}⚠ No .agent-references.yaml found${NC}"
    echo -e "${YELLOW}  Creating default configuration...${NC}"

    if [ "$DRY_RUN" = false ]; then
        cat > "$REFERENCES_FILE" << 'EOF'
# Agent References Configuration
# This file declares which external agents this repository uses

meta:
  repository: REPO_NAME
  last_updated: "DATE"

universal_agents:
  # From workspace-hub (Tier 1)
  source: "@workspace-hub/.claude/agents/universal/"
  agents:
    - coder
    - reviewer
    - tester
    - planner

domain_agents: []
  # Example:
  # - source: "@digitalmodel/.claude/agents/"
  #   agents:
  #     - orcaflex
  #     - aqwa

local_agents: []
  # Repository-specific agents

orchestration:
  method: "symlink"
  auto_sync: true
  sync_schedule: "daily"
EOF
        # Replace placeholders
        sed -i "s/REPO_NAME/$REPO_NAME/g" "$REFERENCES_FILE"
        sed -i "s/DATE/$(date +%Y-%m-%d)/g" "$REFERENCES_FILE"

        echo -e "${GREEN}✓ Created default .agent-references.yaml${NC}"
    else
        echo -e "${YELLOW}  Would create .agent-references.yaml${NC}"
    fi
    echo ""
fi

# Create agent directories
AGENTS_DIR="$TARGET_REPO/.claude/agents"

if [ "$DRY_RUN" = false ]; then
    mkdir -p "$AGENTS_DIR/universal"
    mkdir -p "$AGENTS_DIR/external"
    mkdir -p "$AGENTS_DIR/local"
    [ "$VERBOSE" = true ] && echo -e "${GREEN}✓ Created agent directories${NC}"
else
    echo -e "${YELLOW}Would create:${NC}"
    echo "  - $AGENTS_DIR/universal"
    echo "  - $AGENTS_DIR/external"
    echo "  - $AGENTS_DIR/local"
fi

# Function to create symlink
create_symlink() {
    local source=$1
    local target=$2
    local description=$3

    if [ ! -e "$source" ]; then
        [ "$VERBOSE" = true ] && echo -e "${YELLOW}  ⚠ Source not found: $source${NC}"
        return 1
    fi

    if [ -L "$target" ]; then
        if [ "$FORCE" = true ]; then
            if [ "$DRY_RUN" = false ]; then
                rm "$target"
                ln -s "$source" "$target"
                echo -e "${GREEN}  ✓ Updated:${NC} $description"
            else
                echo -e "${YELLOW}  Would update:${NC} $description"
            fi
        else
            [ "$VERBOSE" = true ] && echo -e "${BLUE}  → Exists:${NC} $description"
        fi
    elif [ -e "$target" ]; then
        echo -e "${YELLOW}  ⚠ File exists (not symlink):${NC} $description"
    else
        if [ "$DRY_RUN" = false ]; then
            ln -s "$source" "$target"
            echo -e "${GREEN}  ✓ Created:${NC} $description"
        else
            echo -e "${YELLOW}  Would create:${NC} $description"
        fi
    fi

    return 0
}

# Setup universal agents
echo -e "${BLUE}Setting up universal agents...${NC}"

UNIVERSAL_SOURCE="$WORKSPACE_ROOT/.claude/agents/universal"

if [ -d "$UNIVERSAL_SOURCE" ]; then
    # Link entire universal directory structure
    for category_dir in "$UNIVERSAL_SOURCE"/*; do
        if [ -d "$category_dir" ]; then
            category=$(basename "$category_dir")

            # Create category directory
            if [ "$DRY_RUN" = false ]; then
                mkdir -p "$AGENTS_DIR/universal/$category"
            fi

            # Link each agent in category
            for agent_file in "$category_dir"/*.yaml "$category_dir"/*.yml 2>/dev/null; do
                [ -f "$agent_file" ] || continue

                agent_name=$(basename "$agent_file")
                source_path="$agent_file"
                target_path="$AGENTS_DIR/universal/$category/$agent_name"

                create_symlink "$source_path" "$target_path" "universal/$category/$agent_name"
            done
        fi
    done
else
    echo -e "${YELLOW}  ⚠ Universal agents not found at: $UNIVERSAL_SOURCE${NC}"
    echo -e "${YELLOW}    Universal agents may need to be organized first${NC}"
fi

echo ""

# Setup domain agents (if not universal-only)
if [ "$UNIVERSAL_ONLY" = false ]; then
    echo -e "${BLUE}Setting up domain agents...${NC}"

    # Parse .agent-references.yaml for domain agents
    if [ -f "$REFERENCES_FILE" ]; then
        # Extract domain agent sources (simplified parsing)
        # In production, use yq or proper YAML parser

        # Check for digitalmodel agents
        if grep -q "digitalmodel" "$REFERENCES_FILE" 2>/dev/null; then
            echo -e "${BLUE}  Setting up digitalmodel agents...${NC}"

            DIGITALMODEL_SOURCE="/mnt/github/digitalmodel/.claude/agents"
            if [ -d "$DIGITALMODEL_SOURCE" ]; then
                mkdir -p "$AGENTS_DIR/external/engineering"

                # Link common engineering agents
                for agent in orcaflex aqwa freecad gmsh; do
                    if [ -f "$DIGITALMODEL_SOURCE/$agent.yaml" ]; then
                        create_symlink \
                            "$DIGITALMODEL_SOURCE/$agent.yaml" \
                            "$AGENTS_DIR/external/engineering/$agent.yaml" \
                            "external/engineering/$agent"
                    fi
                done
            else
                [ "$VERBOSE" = true ] && echo -e "${YELLOW}    ⚠ digitalmodel agents not found${NC}"
            fi
        fi

        # Check for worldenergydata agents
        if grep -q "worldenergydata" "$REFERENCES_FILE" 2>/dev/null; then
            echo -e "${BLUE}  Setting up worldenergydata agents...${NC}"

            ENERGY_SOURCE="/mnt/github/worldenergydata/.claude/agents"
            if [ -d "$ENERGY_SOURCE" ]; then
                mkdir -p "$AGENTS_DIR/external/energy"

                for agent in drilling-expert oil-and-gas-expert financial-analysis; do
                    if [ -f "$ENERGY_SOURCE/$agent.yaml" ]; then
                        create_symlink \
                            "$ENERGY_SOURCE/$agent.yaml" \
                            "$AGENTS_DIR/external/energy/$agent.yaml" \
                            "external/energy/$agent"
                    fi
                done
            else
                [ "$VERBOSE" = true ] && echo -e "${YELLOW}    ⚠ worldenergydata agents not found${NC}"
            fi
        fi

        # Check for assetutilities agents
        if grep -q "assetutilities" "$REFERENCES_FILE" 2>/dev/null; then
            echo -e "${BLUE}  Setting up assetutilities agents...${NC}"

            FINANCE_SOURCE="/mnt/github/assetutilities/.claude/agents"
            if [ -d "$FINANCE_SOURCE" ]; then
                mkdir -p "$AGENTS_DIR/external/finance"

                for agent in finance-analytics workflow-automation; do
                    if [ -f "$FINANCE_SOURCE/$agent.yaml" ] || [ -d "$FINANCE_SOURCE/$agent" ]; then
                        if [ -f "$FINANCE_SOURCE/$agent.yaml" ]; then
                            create_symlink \
                                "$FINANCE_SOURCE/$agent.yaml" \
                                "$AGENTS_DIR/external/finance/$agent.yaml" \
                                "external/finance/$agent"
                        fi
                    fi
                done
            else
                [ "$VERBOSE" = true ] && echo -e "${YELLOW}    ⚠ assetutilities agents not found${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}  ⚠ No .agent-references.yaml found, skipping domain agents${NC}"
    fi

    echo ""
fi

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Count symlinks
if [ "$DRY_RUN" = false ]; then
    UNIVERSAL_COUNT=$(find "$AGENTS_DIR/universal" -type l 2>/dev/null | wc -l)
    EXTERNAL_COUNT=$(find "$AGENTS_DIR/external" -type l 2>/dev/null | wc -l)
    LOCAL_COUNT=$(find "$AGENTS_DIR/local" -name "*.yaml" -o -name "*.yml" 2>/dev/null | wc -l)

    echo -e "${GREEN}✓ Setup complete for: $REPO_NAME${NC}"
    echo ""
    echo -e "${BLUE}Agent Links Created:${NC}"
    echo -e "  Universal agents: $UNIVERSAL_COUNT"
    echo -e "  External (domain) agents: $EXTERNAL_COUNT"
    echo -e "  Local agents: $LOCAL_COUNT"
    echo ""
    echo -e "${BLUE}Agent Directories:${NC}"
    echo -e "  $AGENTS_DIR/universal/"
    echo -e "  $AGENTS_DIR/external/"
    echo -e "  $AGENTS_DIR/local/"
    echo ""
    echo -e "${GREEN}✓ Agents ready to use!${NC}"
else
    echo -e "${YELLOW}Dry run complete - no changes made${NC}"
fi

echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo -e "  1. Review: ${YELLOW}.agent-references.yaml${NC}"
echo -e "  2. Verify links: ${YELLOW}ls -la $AGENTS_DIR/universal/${NC}"
echo -e "  3. Use agents: ${YELLOW}claude-flow agent run <name>${NC}"
echo -e "  4. Or via orchestrator: ${YELLOW}agent_orchestrator.sh --agent <name>${NC}"
echo ""
