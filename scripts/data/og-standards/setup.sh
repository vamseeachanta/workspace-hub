#!/bin/bash
# ABOUTME: O&G Standards Knowledge System Setup Script
# ABOUTME: Installs dependencies and configures the system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STANDARDS_DIR="/mnt/ace/O&G-Standards"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}     O&G Standards Knowledge System - Setup${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
if [ -z "$PYTHON_VERSION" ]; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Check pip
echo -e "${YELLOW}Checking pip...${NC}"
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo -e "${RED}✗ pip not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip found${NC}"

# Install Python dependencies
echo ""
echo -e "${YELLOW}Installing Python dependencies...${NC}"

DEPS=(
    "PyMuPDF"            # PDF text extraction
    "pyyaml"             # YAML config
    "sentence-transformers"  # Local embeddings
    "anthropic"          # Claude API
    "openai"             # OpenAI API (optional)
)

for dep in "${DEPS[@]}"; do
    echo -n "  Installing $dep..."
    pip install --quiet "$dep" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${YELLOW}⚠ (may need manual install)${NC}"
    fi
done

# Check standards directory
echo ""
echo -e "${YELLOW}Checking standards directory...${NC}"
if [ -d "$STANDARDS_DIR" ]; then
    PDF_COUNT=$(find "$STANDARDS_DIR" -name "*.pdf" -type f 2>/dev/null | wc -l)
    echo -e "${GREEN}✓ Standards directory exists with $PDF_COUNT PDFs${NC}"
else
    echo -e "${YELLOW}⚠ Standards directory not found at $STANDARDS_DIR${NC}"
    echo "  Create it or update path in config.yaml"
fi

# Check database
echo ""
echo -e "${YELLOW}Checking database...${NC}"
if [ -f "$STANDARDS_DIR/_inventory.db" ]; then
    DOC_COUNT=$(sqlite3 "$STANDARDS_DIR/_inventory.db" "SELECT COUNT(*) FROM documents" 2>/dev/null || echo "0")
    echo -e "${GREEN}✓ Database exists with $DOC_COUNT documents${NC}"
else
    echo -e "${YELLOW}○ Database not initialized${NC}"
    echo "  Run: python inventory.py"
fi

# Check API keys
echo ""
echo -e "${YELLOW}Checking API keys...${NC}"
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo -e "${GREEN}✓ ANTHROPIC_API_KEY is set${NC}"
else
    echo -e "${YELLOW}○ ANTHROPIC_API_KEY not set (required for AI answers)${NC}"
    echo "  Add to ~/.bashrc: export ANTHROPIC_API_KEY='your-key'"
fi

if [ -n "$OPENAI_API_KEY" ]; then
    echo -e "${GREEN}✓ OPENAI_API_KEY is set${NC}"
else
    echo -e "${YELLOW}○ OPENAI_API_KEY not set (optional)${NC}"
fi

# Create symlinks
echo ""
echo -e "${YELLOW}Creating command symlinks...${NC}"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

COMMANDS=("og" "og-rag" "og-status" "og-service" "og-ingest")
for cmd in "${COMMANDS[@]}"; do
    if [ -f "$SCRIPT_DIR/$cmd" ]; then
        ln -sf "$SCRIPT_DIR/$cmd" "$BIN_DIR/$cmd" 2>/dev/null
        echo -e "  ${GREEN}✓${NC} $cmd"
    fi
done

# Check if bin dir is in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo -e "${YELLOW}Add to PATH by running:${NC}"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo "  # Add to ~/.bashrc for persistence"
fi

# Summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo "  1. Set ANTHROPIC_API_KEY for AI-powered answers"
echo "  2. Run 'og-status' to check system status"
echo "  3. Run 'og-service start-all' to start processing"
echo "  4. Use 'og <query>' for quick searches"
echo "  5. Use 'og-rag <question>' for AI Q&A"
echo ""
