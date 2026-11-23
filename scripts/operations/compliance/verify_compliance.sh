#!/bin/bash

# ABOUTME: Compliance verification script for AI usage guidelines and best practices
# ABOUTME: Checks if repository structure follows workspace-hub standards

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_PATH="${1:-.}"
STRICT_MODE="${2:-false}"
REPORT_FILE="${3:-compliance_report.txt}"

# Compliance checks
COMPLIANCE_SCORE=0
TOTAL_CHECKS=0
FAILED_CHECKS=()
PASSED_CHECKS=()
WARNINGS=()

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}AI Usage Guidelines Compliance Check${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Repository: $REPO_PATH"
echo "Strict Mode: $STRICT_MODE"
echo ""

# Function to check if file exists
check_file_exists() {
    local file="$1"
    local description="$2"
    local required="$3"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [ -f "$REPO_PATH/$file" ]; then
        echo -e "${GREEN}✓${NC} $description: $file"
        PASSED_CHECKS+=("$description")
        COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 1))
        return 0
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}✗${NC} $description: $file (REQUIRED)"
            FAILED_CHECKS+=("$description - Missing: $file")
            return 1
        else
            echo -e "${YELLOW}⚠${NC} $description: $file (OPTIONAL)"
            WARNINGS+=("$description - Missing: $file")
            COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 1))
            return 0
        fi
    fi
}

# Function to check directory structure
check_directory() {
    local dir="$1"
    local description="$2"
    local required="$3"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [ -d "$REPO_PATH/$dir" ]; then
        echo -e "${GREEN}✓${NC} $description: $dir/"
        PASSED_CHECKS+=("$description")
        COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 1))
        return 0
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}✗${NC} $description: $dir/ (REQUIRED)"
            FAILED_CHECKS+=("$description - Missing: $dir/")
            return 1
        else
            echo -e "${YELLOW}⚠${NC} $description: $dir/ (OPTIONAL)"
            WARNINGS+=("$description - Missing: $dir/")
            COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 1))
            return 0
        fi
    fi
}

# Function to check file content
check_file_content() {
    local file="$1"
    local pattern="$2"
    local description="$3"
    local required="$4"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [ ! -f "$REPO_PATH/$file" ]; then
        if [ "$required" = "true" ]; then
            echo -e "${RED}✗${NC} $description: File not found"
            FAILED_CHECKS+=("$description - File not found: $file")
            return 1
        else
            echo -e "${YELLOW}⚠${NC} $description: File not found (OPTIONAL)"
            WARNINGS+=("$description - File not found: $file")
            COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 1))
            return 0
        fi
    fi

    if grep -q "$pattern" "$REPO_PATH/$file"; then
        echo -e "${GREEN}✓${NC} $description"
        PASSED_CHECKS+=("$description")
        COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 1))
        return 0
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}✗${NC} $description: Pattern not found"
            FAILED_CHECKS+=("$description - Pattern not found in $file")
            return 1
        else
            echo -e "${YELLOW}⚠${NC} $description: Pattern not found (OPTIONAL)"
            WARNINGS+=("$description - Pattern not found in $file")
            COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 1))
            return 0
        fi
    fi
}

echo -e "${BLUE}Phase 1: Core Documentation${NC}"
echo "────────────────────────────"
check_file_exists "docs/AI_USAGE_GUIDELINES.md" "AI Usage Guidelines" "true"
check_file_exists "docs/AI_AGENT_GUIDELINES.md" "AI Agent Guidelines" "true"
check_file_exists "docs/DEVELOPMENT_WORKFLOW.md" "Development Workflow" "true"
check_file_exists "CLAUDE.md" "Claude Configuration" "true"
check_file_exists "user_prompt.md" "User Prompt Template" "false"
echo ""

echo -e "${BLUE}Phase 2: Required Directory Structure${NC}"
echo "────────────────────────────────────"
check_directory "scripts" "Scripts Directory" "true"
check_directory "config/input" "Config Input Directory" "true"
check_directory "docs/pseudocode" "Pseudocode Directory" "true"
check_directory "templates" "Templates Directory" "true"
check_directory "src" "Source Code Directory" "false"
check_directory "tests" "Tests Directory" "false"
check_directory "data" "Data Directory" "false"
check_directory "reports" "Reports Directory" "false"
echo ""

echo -e "${BLUE}Phase 3: Template Files${NC}"
echo "─────────────────────"
check_file_exists "templates/user_prompt.md" "User Prompt Template" "true"
check_file_exists "templates/input_config.yaml" "YAML Config Template" "true"
check_file_exists "templates/pseudocode.md" "Pseudocode Template" "true"
check_file_exists "templates/run_tests.sh" "Test Runner Template" "true"
check_file_exists "templates/workflow.sh" "Workflow Automation Template" "true"
echo ""

echo -e "${BLUE}Phase 4: CLAUDE.md Content Verification${NC}"
echo "──────────────────────────────────────"
check_file_content "CLAUDE.md" "AI_USAGE_GUIDELINES.md" "References AI Usage Guidelines" "true"
check_file_content "CLAUDE.md" "CRITICAL ENFORCEMENT" "Contains enforcement section" "true"
check_file_content "CLAUDE.md" "MANDATORY COMPLIANCE" "Contains compliance requirements" "true"
check_file_content "CLAUDE.md" "docs/DEVELOPMENT_WORKFLOW.md" "References Development Workflow" "true"
echo ""

echo -e "${BLUE}Phase 5: AI Usage Guidelines Content${NC}"
echo "───────────────────────────────────"
check_file_content "docs/AI_USAGE_GUIDELINES.md" "CRITICAL ENFORCEMENT" "Contains enforcement notice" "true"
check_file_content "docs/AI_USAGE_GUIDELINES.md" "Effectiveness Matrix" "Contains effectiveness matrix" "true"
check_file_content "docs/AI_USAGE_GUIDELINES.md" "⭐⭐⭐⭐⭐" "Contains rating system" "true"
echo ""

echo -e "${BLUE}Phase 6: Git Integration${NC}"
echo "──────────────────────"
check_directory ".git" "Git Repository" "true"
check_file_exists ".gitignore" "Git Ignore File" "true"
check_directory ".git/hooks" "Git Hooks Directory" "false"
echo ""

echo -e "${BLUE}Phase 7: Best Practice Compliance${NC}"
echo "────────────────────────────────"

# Check if there are any .py files in root (should be in src/)
if ls "$REPO_PATH"/*.py 2>/dev/null | grep -q .; then
    echo -e "${YELLOW}⚠${NC} Python files found in root (should be in src/)"
    WARNINGS+=("Python files in root - should be in src/")
else
    echo -e "${GREEN}✓${NC} No Python files in root directory"
    COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 1))
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# Check if there are any .md files in root (except CLAUDE.md, README.md, user_prompt.md)
ALLOWED_MD_FILES="CLAUDE.md README.md user_prompt.md"
for md_file in "$REPO_PATH"/*.md; do
    if [ -f "$md_file" ]; then
        filename=$(basename "$md_file")
        if ! echo "$ALLOWED_MD_FILES" | grep -q "$filename"; then
            echo -e "${YELLOW}⚠${NC} Markdown file in root: $filename (should be in docs/)"
            WARNINGS+=("Markdown file in root: $filename - should be in docs/")
        fi
    fi
done
echo -e "${GREEN}✓${NC} Root directory organization checked"
COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 1))
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# Check for data files in root
if ls "$REPO_PATH"/*.csv 2>/dev/null | grep -q . || ls "$REPO_PATH"/*.json 2>/dev/null | grep -q .; then
    echo -e "${YELLOW}⚠${NC} Data files found in root (should be in data/)"
    WARNINGS+=("Data files in root - should be in data/")
else
    echo -e "${GREEN}✓${NC} No data files in root directory"
    COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 1))
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

echo ""

# Calculate compliance percentage
COMPLIANCE_PERCENTAGE=$(( (COMPLIANCE_SCORE * 100) / TOTAL_CHECKS ))

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Compliance Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Total Checks: $TOTAL_CHECKS"
echo "Passed: ${#PASSED_CHECKS[@]}"
echo "Failed: ${#FAILED_CHECKS[@]}"
echo "Warnings: ${#WARNINGS[@]}"
echo ""
echo "Compliance Score: $COMPLIANCE_SCORE / $TOTAL_CHECKS ($COMPLIANCE_PERCENTAGE%)"
echo ""

# Print failed checks
if [ ${#FAILED_CHECKS[@]} -gt 0 ]; then
    echo -e "${RED}Failed Checks:${NC}"
    for check in "${FAILED_CHECKS[@]}"; do
        echo "  ✗ $check"
    done
    echo ""
fi

# Print warnings
if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo -e "${YELLOW}Warnings:${NC}"
    for warning in "${WARNINGS[@]}"; do
        echo "  ⚠ $warning"
    done
    echo ""
fi

# Generate report file
{
    echo "AI Usage Guidelines Compliance Report"
    echo "====================================="
    echo ""
    echo "Repository: $REPO_PATH"
    echo "Date: $(date)"
    echo "Compliance Score: $COMPLIANCE_SCORE / $TOTAL_CHECKS ($COMPLIANCE_PERCENTAGE%)"
    echo ""
    echo "Passed Checks: ${#PASSED_CHECKS[@]}"
    echo "Failed Checks: ${#FAILED_CHECKS[@]}"
    echo "Warnings: ${#WARNINGS[@]}"
    echo ""

    if [ ${#FAILED_CHECKS[@]} -gt 0 ]; then
        echo "Failed Checks:"
        for check in "${FAILED_CHECKS[@]}"; do
            echo "  - $check"
        done
        echo ""
    fi

    if [ ${#WARNINGS[@]} -gt 0 ]; then
        echo "Warnings:"
        for warning in "${WARNINGS[@]}"; do
            echo "  - $warning"
        done
        echo ""
    fi

    echo "Recommendations:"
    if [ ${#FAILED_CHECKS[@]} -gt 0 ]; then
        echo "  1. Address all failed checks immediately"
        echo "  2. Review docs/AI_USAGE_GUIDELINES.md for requirements"
        echo "  3. Run ./scripts/setup_compliance.sh to auto-create missing files"
    fi
    if [ ${#WARNINGS[@]} -gt 0 ]; then
        echo "  4. Review warnings and consider addressing them"
        echo "  5. Reorganize files according to docs/FILE_ORGANIZATION_STANDARDS.md"
    fi

} > "$REPORT_FILE"

echo "Report saved to: $REPORT_FILE"
echo ""

# Determine exit code
if [ "$STRICT_MODE" = "true" ]; then
    if [ ${#FAILED_CHECKS[@]} -gt 0 ]; then
        echo -e "${RED}✗ COMPLIANCE FAILED (Strict Mode)${NC}"
        echo ""
        echo "Fix all failed checks and run again."
        exit 1
    elif [ "$COMPLIANCE_PERCENTAGE" -lt 90 ]; then
        echo -e "${YELLOW}⚠ COMPLIANCE WARNING (Strict Mode)${NC}"
        echo ""
        echo "Compliance is below 90%. Please address warnings."
        exit 1
    else
        echo -e "${GREEN}✓ COMPLIANCE PASSED (Strict Mode)${NC}"
        exit 0
    fi
else
    if [ ${#FAILED_CHECKS[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠ COMPLIANCE WARNINGS PRESENT${NC}"
        echo ""
        echo "Please address failed checks when possible."
        exit 0
    else
        echo -e "${GREEN}✓ COMPLIANCE PASSED${NC}"
        exit 0
    fi
fi
