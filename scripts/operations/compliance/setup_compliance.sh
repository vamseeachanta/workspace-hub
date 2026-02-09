#!/bin/bash

# ABOUTME: Setup script for AI usage guidelines compliance infrastructure
# ABOUTME: Creates missing directories and files required for compliance

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

REPO_PATH="${1:-.}"
HUB_ROOT="$HUB_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Setting Up Compliance Infrastructure${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Create required directories
echo -e "${BLUE}Creating required directories...${NC}"
mkdir -p "$REPO_PATH/scripts"
mkdir -p "$REPO_PATH/config/input"
mkdir -p "$REPO_PATH/docs/pseudocode"
mkdir -p "$REPO_PATH/templates"
mkdir -p "$REPO_PATH/src"
mkdir -p "$REPO_PATH/tests"
mkdir -p "$REPO_PATH/data/raw"
mkdir -p "$REPO_PATH/data/processed"
mkdir -p "$REPO_PATH/data/results"
mkdir -p "$REPO_PATH/reports"
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Copy guideline documents if they don't exist
echo -e "${BLUE}Setting up guideline documents...${NC}"

if [ ! -f "$REPO_PATH/docs/AI_USAGE_GUIDELINES.md" ]; then
    if [ -f "$HUB_ROOT/docs/AI_USAGE_GUIDELINES.md" ]; then
        cp "$HUB_ROOT/docs/AI_USAGE_GUIDELINES.md" "$REPO_PATH/docs/"
        echo -e "${GREEN}✓ Copied AI_USAGE_GUIDELINES.md${NC}"
    else
        echo -e "${YELLOW}⚠ AI_USAGE_GUIDELINES.md not found in workspace-hub${NC}"
    fi
fi

if [ ! -f "$REPO_PATH/docs/AI_AGENT_GUIDELINES.md" ]; then
    if [ -f "$HUB_ROOT/docs/AI_AGENT_GUIDELINES.md" ]; then
        cp "$HUB_ROOT/docs/AI_AGENT_GUIDELINES.md" "$REPO_PATH/docs/"
        echo -e "${GREEN}✓ Copied AI_AGENT_GUIDELINES.md${NC}"
    else
        echo -e "${YELLOW}⚠ AI_AGENT_GUIDELINES.md not found in workspace-hub${NC}"
    fi
fi

if [ ! -f "$REPO_PATH/docs/DEVELOPMENT_WORKFLOW.md" ]; then
    if [ -f "$HUB_ROOT/docs/DEVELOPMENT_WORKFLOW.md" ]; then
        cp "$HUB_ROOT/docs/DEVELOPMENT_WORKFLOW.md" "$REPO_PATH/docs/"
        echo -e "${GREEN}✓ Copied DEVELOPMENT_WORKFLOW.md${NC}"
    else
        echo -e "${YELLOW}⚠ DEVELOPMENT_WORKFLOW.md not found in workspace-hub${NC}"
    fi
fi
echo ""

# Copy templates if they don't exist
echo -e "${BLUE}Setting up templates...${NC}"

TEMPLATE_FILES=(
    "user_prompt.md"
    "input_config.yaml"
    "pseudocode.md"
    "run_tests.sh"
    "workflow.sh"
)

for template in "${TEMPLATE_FILES[@]}"; do
    if [ ! -f "$REPO_PATH/templates/$template" ]; then
        if [ -f "$HUB_ROOT/templates/$template" ]; then
            cp "$HUB_ROOT/templates/$template" "$REPO_PATH/templates/"
            echo -e "${GREEN}✓ Copied template: $template${NC}"
        else
            echo -e "${YELLOW}⚠ Template not found: $template${NC}"
        fi
    fi
done
echo ""

# Make scripts executable
echo -e "${BLUE}Making scripts executable...${NC}"
find "$REPO_PATH/scripts" -name "*.sh" -exec chmod +x {} \;
find "$REPO_PATH/templates" -name "*.sh" -exec chmod +x {} \;
echo -e "${GREEN}✓ Scripts made executable${NC}"
echo ""

# Create .gitignore if it doesn't exist
if [ ! -f "$REPO_PATH/.gitignore" ]; then
    echo -e "${BLUE}Creating .gitignore...${NC}"
    cat > "$REPO_PATH/.gitignore" << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
venv/
ENV/
env/

# Data
data/raw/*.csv
data/processed/*.csv
data/results/*.csv
*.db
*.sqlite

# Reports
reports/*.html
reports/*.pdf

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Compliance reports
compliance_report.txt
EOF
    echo -e "${GREEN}✓ Created .gitignore${NC}"
fi
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Compliance Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Run: ./scripts/verify_compliance.sh"
echo "  2. Review: docs/AI_USAGE_GUIDELINES.md"
echo "  3. Update: CLAUDE.md with enforcement rules"
echo ""
