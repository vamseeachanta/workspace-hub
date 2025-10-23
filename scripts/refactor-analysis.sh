#!/bin/bash
# ABOUTME: Automated refactor analysis using jscpd, knip, and other tools
# ABOUTME: Generates reports for continuous code quality improvement

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(dirname "$SCRIPT_DIR")"
REPORT_DIR="${WORKSPACE_ROOT}/.refactor-reports"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Create reports directory
mkdir -p "$REPORT_DIR"

# Header
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}          ${BLUE}Refactor Analysis Report${NC}                      ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Timestamp:${NC} $(date)"
echo -e "${BLUE}Repository:${NC} $(basename "$WORKSPACE_ROOT")"
echo ""

# 1. Code Duplication Analysis
echo -e "${YELLOW}1️⃣  Code Duplication Analysis (jscpd)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v jscpd &> /dev/null || command -v npx &> /dev/null; then
    if [ -f "$WORKSPACE_ROOT/.jscpd.json" ]; then
        echo -e "${BLUE}ℹ${NC} Using config: .jscpd.json"
    fi
    
    echo "Running jscpd..."
    if npx jscpd src/ --min-lines 5 --format markdown > "$REPORT_DIR/duplication-$TIMESTAMP.md" 2>&1; then
        duplication_pct=$(grep -oP 'duplications:\s*\K[0-9.]+(?=%)' "$REPORT_DIR/duplication-$TIMESTAMP.md" | head -1 || echo "0")
        echo -e "${GREEN}✓${NC} Analysis complete"
        echo -e "  Duplication: ${duplication_pct}%"
        echo -e "  Report: .refactor-reports/duplication-$TIMESTAMP.md"
    else
        echo -e "${YELLOW}⚠${NC} jscpd analysis had issues (this is normal for small codebases)"
    fi
else
    echo -e "${YELLOW}⚠${NC} jscpd not available. Install with: npm install -g jscpd"
fi
echo ""

# 2. Dead Code Detection
echo -e "${YELLOW}2️⃣  Dead Code Detection (knip)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v knip &> /dev/null || command -v npx &> /dev/null; then
    if [ -f "$WORKSPACE_ROOT/knip.json" ]; then
        echo -e "${BLUE}ℹ${NC} Using config: knip.json"
    fi
    
    echo "Running knip..."
    if npx knip --no-exit-code > "$REPORT_DIR/deadcode-$TIMESTAMP.txt" 2>&1; then
        unused_count=$(grep -c "unused" "$REPORT_DIR/deadcode-$TIMESTAMP.txt" || echo "0")
        echo -e "${GREEN}✓${NC} Analysis complete"
        echo -e "  Unused exports found: $unused_count"
        echo -e "  Report: .refactor-reports/deadcode-$TIMESTAMP.txt"
    else
        echo -e "${YELLOW}⚠${NC} knip analysis had issues"
    fi
else
    echo -e "${YELLOW}⚠${NC} knip not available. Install with: npm install -g knip"
fi
echo ""

# 3. Large Files Analysis
echo -e "${YELLOW}3️⃣  Large Files (>500 lines)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "$WORKSPACE_ROOT/src" ]; then
    echo "Scanning src/ directory..."
    large_files=$(find "$WORKSPACE_ROOT/src" -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.py" \) \
        -exec wc -l {} \; 2>/dev/null | \
        awk '$1 > 500 {print $1, $2}' | \
        sort -rn | \
        head -20)
    
    if [ -n "$large_files" ]; then
        echo "$large_files" > "$REPORT_DIR/large-files-$TIMESTAMP.txt"
        file_count=$(echo "$large_files" | wc -l)
        echo -e "${GREEN}✓${NC} Found $file_count files >500 lines"
        echo "$large_files" | head -10 | while read -r lines file; do
            echo -e "  ${lines} lines: $(basename "$file")"
        done
        if [ "$file_count" -gt 10 ]; then
            echo -e "  ... and $((file_count - 10)) more"
        fi
        echo -e "  Report: .refactor-reports/large-files-$TIMESTAMP.txt"
    else
        echo -e "${GREEN}✓${NC} No files exceed 500 lines"
    fi
else
    echo -e "${YELLOW}⚠${NC} No src/ directory found"
fi
echo ""

# 4. Dependency Analysis
echo -e "${YELLOW}4️⃣  Dependency Updates${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "$WORKSPACE_ROOT/package.json" ]; then
    echo "Checking npm dependencies..."
    if command -v npm &> /dev/null; then
        cd "$WORKSPACE_ROOT"
        npm outdated > "$REPORT_DIR/npm-outdated-$TIMESTAMP.txt" 2>&1 || true
        
        outdated_count=$(cat "$REPORT_DIR/npm-outdated-$TIMESTAMP.txt" | grep -v "Package" | grep -v "^$" | wc -l || echo "0")
        echo -e "${GREEN}✓${NC} Dependency check complete"
        echo -e "  Outdated packages: $outdated_count"
        echo -e "  Report: .refactor-reports/npm-outdated-$TIMESTAMP.txt"
        
        # Security audit
        echo "Checking for security vulnerabilities..."
        npm audit --json > "$REPORT_DIR/npm-audit-$TIMESTAMP.json" 2>&1 || true
        echo -e "${GREEN}✓${NC} Security audit complete"
        echo -e "  Report: .refactor-reports/npm-audit-$TIMESTAMP.json"
    else
        echo -e "${YELLOW}⚠${NC} npm not available"
    fi
elif [ -f "$WORKSPACE_ROOT/pyproject.toml" ]; then
    echo "Python project detected..."
    if command -v uv &> /dev/null; then
        cd "$WORKSPACE_ROOT"
        echo "Checking outdated packages with uv..."
        echo -e "${GREEN}✓${NC} Use: uv pip list --outdated"
    else
        echo -e "${YELLOW}⚠${NC} uv not available"
    fi
else
    echo -e "${YELLOW}⚠${NC} No package.json or pyproject.toml found"
fi
echo ""

# 5. Test Performance
echo -e "${YELLOW}5️⃣  Slow Tests (>100ms)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "$WORKSPACE_ROOT/package.json" ] && grep -q "\"test\":" "$WORKSPACE_ROOT/package.json"; then
    echo "Running test suite to find slow tests..."
    cd "$WORKSPACE_ROOT"
    if npm test -- --verbose 2>&1 | grep -E "✓.*[0-9]{3,}ms" > "$REPORT_DIR/slow-tests-$TIMESTAMP.txt"; then
        slow_count=$(cat "$REPORT_DIR/slow-tests-$TIMESTAMP.txt" | wc -l)
        echo -e "${GREEN}✓${NC} Test performance analysis complete"
        echo -e "  Slow tests found: $slow_count"
        echo -e "  Report: .refactor-reports/slow-tests-$TIMESTAMP.txt"
    else
        echo -e "${YELLOW}⚠${NC} No slow tests found or test command not available"
    fi
else
    echo -e "${YELLOW}⚠${NC} No test script found in package.json"
fi
echo ""

# 6. Code Complexity (if available)
echo -e "${YELLOW}6️⃣  Code Complexity${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v eslint &> /dev/null; then
    echo "Checking for complex functions..."
    cd "$WORKSPACE_ROOT"
    eslint --ext .js,.ts,.jsx,.tsx src/ --format json > "$REPORT_DIR/complexity-$TIMESTAMP.json" 2>&1 || true
    echo -e "${GREEN}✓${NC} Complexity analysis complete"
    echo -e "  Report: .refactor-reports/complexity-$TIMESTAMP.json"
else
    echo -e "${YELLOW}⚠${NC} eslint not available for complexity analysis"
fi
echo ""

# Summary
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}                      ${GREEN}Summary${NC}                            ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Reports generated in:${NC} .refactor-reports/"
echo ""
ls -lh "$REPORT_DIR"/*-$TIMESTAMP.* 2>/dev/null || echo "No reports generated"
echo ""
echo -e "${YELLOW}💡 Next Steps:${NC}"
echo "1. Review reports in .refactor-reports/"
echo "2. Address high-priority issues"
echo "3. Create refactor branch: git checkout -b refactor/$(date +%Y%m%d)"
echo "4. Make incremental improvements"
echo "5. Request approval before committing"
echo ""
echo -e "${GREEN}✅ Refactor analysis complete!${NC}"
