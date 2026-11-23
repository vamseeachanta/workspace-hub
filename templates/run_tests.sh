#!/bin/bash

# ABOUTME: TDD test runner script for workspace-hub workflow
# ABOUTME: Executes unit, integration, and performance tests with coverage reporting

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TESTS_DIR="$REPO_ROOT/tests"
COVERAGE_MIN=80
WATCH_MODE=false
VERBOSE=false
TEST_TYPE="all"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --watch)
            WATCH_MODE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --unit)
            TEST_TYPE="unit"
            shift
            ;;
        --integration)
            TEST_TYPE="integration"
            shift
            ;;
        --performance)
            TEST_TYPE="performance"
            shift
            ;;
        --all)
            TEST_TYPE="all"
            shift
            ;;
        --coverage-min)
            COVERAGE_MIN="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --unit            Run only unit tests"
            echo "  --integration     Run only integration tests"
            echo "  --performance     Run only performance tests"
            echo "  --all             Run all tests (default)"
            echo "  --watch           Watch mode - rerun tests on file changes"
            echo "  --verbose, -v     Verbose output"
            echo "  --coverage-min N  Minimum coverage percentage (default: 80)"
            echo "  --help, -h        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}TDD Test Suite Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}✗ pytest not found${NC}"
    echo -e "${YELLOW}Install with: pip install pytest pytest-cov${NC}"
    exit 1
fi

# Function to run tests
run_tests() {
    local test_path="$1"
    local test_name="$2"

    echo -e "${YELLOW}Running $test_name...${NC}"
    echo ""

    if [ "$VERBOSE" = true ]; then
        PYTEST_ARGS="-v -s"
    else
        PYTEST_ARGS="-v"
    fi

    if pytest "$test_path" $PYTEST_ARGS; then
        echo -e "${GREEN}✓ $test_name passed${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ $test_name failed${NC}"
        echo ""
        return 1
    fi
}

# Function to run tests with coverage
run_tests_with_coverage() {
    local test_path="$1"
    local test_name="$2"

    echo -e "${YELLOW}Running $test_name with coverage...${NC}"
    echo ""

    PYTEST_ARGS="-v"
    if [ "$VERBOSE" = true ]; then
        PYTEST_ARGS="$PYTEST_ARGS -s"
    fi

    if pytest "$test_path" $PYTEST_ARGS \
        --cov=src \
        --cov-report=term \
        --cov-report=html \
        --cov-fail-under="$COVERAGE_MIN"; then
        echo -e "${GREEN}✓ $test_name passed with ≥${COVERAGE_MIN}% coverage${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ $test_name failed or coverage < ${COVERAGE_MIN}%${NC}"
        echo ""
        return 1
    fi
}

# Main test execution
if [ "$WATCH_MODE" = true ]; then
    echo -e "${BLUE}Watch mode enabled${NC}"
    echo -e "${YELLOW}Watching for file changes...${NC}"
    echo ""

    # Install pytest-watch if not available
    if ! command -v ptw &> /dev/null; then
        echo -e "${YELLOW}Installing pytest-watch...${NC}"
        pip install pytest-watch
    fi

    ptw --runner "pytest -v --cov=src --cov-report=term"
    exit 0
fi

# Track overall success
ALL_PASSED=true

# Run tests based on type
if [ "$TEST_TYPE" = "unit" ] || [ "$TEST_TYPE" = "all" ]; then
    if [ -d "$TESTS_DIR/unit" ]; then
        if ! run_tests_with_coverage "$TESTS_DIR/unit" "Unit Tests"; then
            ALL_PASSED=false
        fi
    else
        echo -e "${YELLOW}⚠ No unit tests directory found${NC}"
        echo ""
    fi
fi

if [ "$TEST_TYPE" = "integration" ] || [ "$TEST_TYPE" = "all" ]; then
    if [ -d "$TESTS_DIR/integration" ]; then
        if ! run_tests "$TESTS_DIR/integration" "Integration Tests"; then
            ALL_PASSED=false
        fi
    else
        echo -e "${YELLOW}⚠ No integration tests directory found${NC}"
        echo ""
    fi
fi

if [ "$TEST_TYPE" = "performance" ] || [ "$TEST_TYPE" = "all" ]; then
    if [ -d "$TESTS_DIR/performance" ]; then
        echo -e "${YELLOW}Running Performance Tests...${NC}"
        echo ""

        # Performance tests with duration reporting
        if pytest "$TESTS_DIR/performance" -v --durations=10; then
            echo -e "${GREEN}✓ Performance tests passed${NC}"
            echo ""
        else
            echo -e "${RED}✗ Performance tests failed${NC}"
            echo ""
            ALL_PASSED=false
        fi
    else
        echo -e "${YELLOW}⚠ No performance tests directory found${NC}"
        echo ""
    fi
fi

# Final summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ "$ALL_PASSED" = true ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo -e "${BLUE}Coverage report: file://$(pwd)/htmlcov/index.html${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo -e "${YELLOW}Review the errors above and fix failing tests${NC}"
    echo ""
    exit 1
fi
