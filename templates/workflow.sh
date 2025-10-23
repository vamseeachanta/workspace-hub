#!/bin/bash

# ABOUTME: Complete development workflow automation script
# ABOUTME: Orchestrates all phases from user_prompt.md to implementation

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
USER_PROMPT="$REPO_ROOT/user_prompt.md"
CONFIG_DIR="$REPO_ROOT/config/input"
PSEUDOCODE_DIR="$REPO_ROOT/docs/pseudocode"
SCRIPTS_DIR="$REPO_ROOT/scripts"

# Parse arguments
FEATURE_NAME="$1"
AUTO_MODE=false

if [ -z "$FEATURE_NAME" ]; then
    echo "Usage: $0 <feature-name> [--auto]"
    echo ""
    echo "Example: $0 data-analysis-pipeline"
    echo ""
    echo "Options:"
    echo "  --auto    Skip approval prompts (use with caution)"
    exit 1
fi

if [ "$2" = "--auto" ]; then
    AUTO_MODE=true
fi

# Utility function to wait for approval
wait_for_approval() {
    local message="$1"

    if [ "$AUTO_MODE" = true ]; then
        echo -e "${YELLOW}[AUTO MODE] $message${NC}"
        return 0
    fi

    echo ""
    echo -e "${YELLOW}$message${NC}"
    echo -e "${YELLOW}Press ENTER to continue, or Ctrl+C to abort...${NC}"
    read
}

# Utility function to check if AI agent tools are available
check_tools() {
    echo -e "${YELLOW}Checking for AI agent tools...${NC}"

    if command -v droid &> /dev/null; then
        echo -e "${GREEN}✓ Factory.ai (droid) available${NC}"
        HAS_DROID=true
    else
        echo -e "${YELLOW}⚠ Factory.ai (droid) not available${NC}"
        HAS_DROID=false
    fi

    # Note: Claude Code and OpenAI API access is assumed via environment variables
    echo ""
}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Development Workflow: $FEATURE_NAME${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Phase 1: Read user prompt
echo -e "${BLUE}Phase 1: User Requirements${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ ! -f "$USER_PROMPT" ]; then
    echo -e "${RED}✗ $USER_PROMPT not found${NC}"
    echo ""
    echo -e "${YELLOW}Please create user_prompt.md with your requirements.${NC}"
    echo -e "${YELLOW}Template: $REPO_ROOT/templates/user_prompt.md${NC}"
    exit 1
fi

echo -e "${GREEN}✓ User prompt found: $USER_PROMPT${NC}"
echo ""

# Display user prompt summary
echo -e "${BLUE}User Prompt Summary:${NC}"
echo -e "${BLUE}────────────────────${NC}"
head -n 20 "$USER_PROMPT" | grep -v "^#" | grep -v "^$" | head -n 5
echo -e "${BLUE}...${NC}"
echo ""

# Phase 2: Generate YAML configuration
echo -e "${BLUE}Phase 2: YAML Configuration${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

CONFIG_FILE="$CONFIG_DIR/$FEATURE_NAME.yaml"

# Create config directory if it doesn't exist
mkdir -p "$CONFIG_DIR"

echo -e "${YELLOW}Generating YAML configuration...${NC}"
echo ""

# Check for AI agent tools
check_tools

if [ "$HAS_DROID" = true ]; then
    echo -e "${BLUE}Using Factory.ai to generate YAML...${NC}"
    echo ""

    # Use Factory.ai droid to generate YAML
    droid exec "Read $USER_PROMPT and generate a YAML configuration file following the template at $REPO_ROOT/templates/input_config.yaml. Ask clarifying questions before generating. Save to $CONFIG_FILE"
else
    echo -e "${YELLOW}⚠ No AI agent tools available${NC}"
    echo -e "${YELLOW}Please manually create YAML config using template:${NC}"
    echo -e "${YELLOW}  Template: $REPO_ROOT/templates/input_config.yaml${NC}"
    echo -e "${YELLOW}  Output: $CONFIG_FILE${NC}"
    echo ""
    wait_for_approval "Press ENTER when YAML config is ready..."
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}✗ YAML configuration not created${NC}"
    exit 1
fi

echo -e "${GREEN}✓ YAML configuration created: $CONFIG_FILE${NC}"
echo ""

wait_for_approval "Review YAML configuration and approve to continue"

# Phase 3: Generate pseudocode
echo -e "${BLUE}Phase 3: Pseudocode Generation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

PSEUDOCODE_FILE="$PSEUDOCODE_DIR/$FEATURE_NAME.md"

# Create pseudocode directory if it doesn't exist
mkdir -p "$PSEUDOCODE_DIR"

echo -e "${YELLOW}Generating pseudocode...${NC}"
echo ""

if [ "$HAS_DROID" = true ]; then
    echo -e "${BLUE}Using Factory.ai to generate pseudocode...${NC}"
    echo ""

    # Use Factory.ai droid to generate pseudocode
    droid exec "Read $CONFIG_FILE and generate pseudocode following the template at $REPO_ROOT/templates/pseudocode.md. Use language-agnostic notation. Include error handling and performance considerations. Save to $PSEUDOCODE_FILE"
else
    echo -e "${YELLOW}⚠ No AI agent tools available${NC}"
    echo -e "${YELLOW}Please manually create pseudocode using template:${NC}"
    echo -e "${YELLOW}  Template: $REPO_ROOT/templates/pseudocode.md${NC}"
    echo -e "${YELLOW}  Output: $PSEUDOCODE_FILE${NC}"
    echo ""
    wait_for_approval "Press ENTER when pseudocode is ready..."
fi

if [ ! -f "$PSEUDOCODE_FILE" ]; then
    echo -e "${RED}✗ Pseudocode not created${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Pseudocode generated: $PSEUDOCODE_FILE${NC}"
echo ""

# Display pseudocode location for review
echo -e "${BLUE}Review pseudocode:${NC}"
echo -e "${BLUE}  File: $PSEUDOCODE_FILE${NC}"
echo -e "${BLUE}  Or open in editor: vim $PSEUDOCODE_FILE${NC}"
echo ""

wait_for_approval "Review pseudocode and approve to continue"

# Check for approval marker
APPROVAL_FILE="$PSEUDOCODE_FILE.approved"
if [ ! -f "$APPROVAL_FILE" ]; then
    echo -e "${YELLOW}Creating approval marker...${NC}"
    echo "Approved on $(date)" > "$APPROVAL_FILE"
    echo -e "${GREEN}✓ Pseudocode approved${NC}"
    echo ""
fi

# Phase 4-5: TDD Implementation
echo -e "${BLUE}Phase 4-5: TDD Implementation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${YELLOW}Manual implementation required:${NC}"
echo ""
echo -e "${BLUE}Follow TDD workflow:${NC}"
echo -e "  1. Create test directory structure:"
echo -e "     ${YELLOW}mkdir -p tests/unit tests/integration tests/performance${NC}"
echo ""
echo -e "  2. Write failing tests first:"
echo -e "     ${YELLOW}vim tests/unit/test_$FEATURE_NAME.py${NC}"
echo ""
echo -e "  3. Run tests (should fail):"
echo -e "     ${YELLOW}$REPO_ROOT/tests/run_tests.sh --unit${NC}"
echo ""
echo -e "  4. Implement code in src/modules/:"
echo -e "     ${YELLOW}mkdir -p src/modules/$FEATURE_NAME${NC}"
echo -e "     ${YELLOW}vim src/modules/$FEATURE_NAME/implementation.py${NC}"
echo ""
echo -e "  5. Run tests (should pass):"
echo -e "     ${YELLOW}$REPO_ROOT/tests/run_tests.sh --unit${NC}"
echo ""
echo -e "  6. Refactor and keep tests green"
echo ""

wait_for_approval "Press ENTER when implementation is complete..."

# Verify tests exist
if [ ! -d "$REPO_ROOT/tests" ]; then
    echo -e "${YELLOW}⚠ No tests directory found${NC}"
    echo -e "${YELLOW}Skipping test validation${NC}"
    echo ""
else
    # Run tests
    echo -e "${BLUE}Running test suite...${NC}"
    echo ""

    if [ -f "$REPO_ROOT/tests/run_tests.sh" ]; then
        if bash "$REPO_ROOT/tests/run_tests.sh" --all; then
            echo -e "${GREEN}✓ All tests passed${NC}"
            echo ""
        else
            echo -e "${RED}✗ Tests failed${NC}"
            echo -e "${YELLOW}Fix failing tests before proceeding${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠ Test runner not found${NC}"
        echo -e "${YELLOW}Create tests/run_tests.sh from template${NC}"
        echo ""
    fi
fi

# Phase 6: Bash execution script
echo -e "${BLUE}Phase 6: Execution Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

EXEC_SCRIPT="$SCRIPTS_DIR/run_$FEATURE_NAME.sh"

# Create scripts directory if it doesn't exist
mkdir -p "$SCRIPTS_DIR"

echo -e "${YELLOW}Creating execution script...${NC}"
echo ""

# Generate execution script
cat > "$EXEC_SCRIPT" << 'EOFSCRIPT'
#!/bin/bash

# ABOUTME: Execution script for [FEATURE_NAME]
# ABOUTME: Runs feature with YAML configuration input

set -e

CONFIG_FILE="$1"
OUTPUT_DIR="${2:-./reports}"

if [ -z "$CONFIG_FILE" ]; then
    echo "Usage: $0 <config.yaml> [output_dir]"
    exit 1
fi

echo "Running [FEATURE_NAME] pipeline..."
echo "Config: $CONFIG_FILE"
echo "Output: $OUTPUT_DIR"
echo ""

# Execute feature
python src/pipelines/[FEATURE_NAME]_pipeline.py \
    --config "$CONFIG_FILE" \
    --output "$OUTPUT_DIR" \
    --verbose

echo ""
echo "Pipeline completed successfully!"
echo "Output: $OUTPUT_DIR/"
EOFSCRIPT

# Replace [FEATURE_NAME] with actual feature name
sed -i "s/\[FEATURE_NAME\]/$FEATURE_NAME/g" "$EXEC_SCRIPT"

# Make executable
chmod +x "$EXEC_SCRIPT"

echo -e "${GREEN}✓ Execution script created: $EXEC_SCRIPT${NC}"
echo ""

# Final summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Workflow Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${GREEN}✓ All phases completed successfully${NC}"
echo ""

echo -e "${BLUE}Created Files:${NC}"
echo -e "  • User Prompt: ${YELLOW}$USER_PROMPT${NC}"
echo -e "  • YAML Config: ${YELLOW}$CONFIG_FILE${NC}"
echo -e "  • Pseudocode: ${YELLOW}$PSEUDOCODE_FILE${NC}"
echo -e "  • Execution Script: ${YELLOW}$EXEC_SCRIPT${NC}"
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo -e "  1. Review implementation in ${YELLOW}src/modules/$FEATURE_NAME/${NC}"
echo -e "  2. Verify tests in ${YELLOW}tests/${NC}"
echo -e "  3. Run execution script:"
echo -e "     ${YELLOW}$EXEC_SCRIPT $CONFIG_FILE${NC}"
echo ""

echo -e "${GREEN}Development workflow completed! 🚀${NC}"
