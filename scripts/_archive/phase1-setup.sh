#!/bin/bash

# Phase 1 Test Environment Setup Script
# ====================================
# Sets up the test environment for Phase 1 consolidation tasks
# Usage: ./scripts/phase1-setup.sh [environment]

set -e

ENVIRONMENT=${1:-development}
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Phase 1 Test Environment Setup${NC}"
echo "========================================"
echo "Environment: $ENVIRONMENT"
echo "Repository: $REPO_ROOT"
echo ""

# Function to log messages
log_step() {
    echo -e "${GREEN}✓${NC} $1"
}

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Step 1: Verify Python environment
echo -e "${BLUE}Step 1: Verifying Python environment...${NC}"
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 not found"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
log_step "Python available: $PYTHON_VERSION"

# Step 2: Check UV availability
echo -e "${BLUE}Step 2: Checking UV package manager...${NC}"
if ! command -v uv &> /dev/null; then
    log_warn "UV not installed. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi
UV_VERSION=$(uv --version)
log_step "UV available: $UV_VERSION"

# Step 3: Create virtual environment for tests
echo -e "${BLUE}Step 3: Creating test virtual environment...${NC}"
TEST_VENV="$REPO_ROOT/.venv-test"
if [ -d "$TEST_VENV" ]; then
    log_info "Test venv already exists, skipping creation"
else
    uv venv "$TEST_VENV"
    log_step "Test virtual environment created: $TEST_VENV"
fi

# Activate virtual environment
source "$TEST_VENV/bin/activate"

# Step 4: Install testing dependencies
echo -e "${BLUE}Step 4: Installing testing dependencies...${NC}"
uv pip install --quiet pytest pytest-cov pytest-mock pytest-asyncio pytest-benchmark
log_step "Testing frameworks installed"

# Step 5: Install core dependencies
echo -e "${BLUE}Step 5: Installing core dependencies...${NC}"
uv pip install --quiet pyyaml sqlalchemy pandas numpy scipy requests
log_step "Core dependencies installed"

# Step 6: Create test database configuration
echo -e "${BLUE}Step 6: Setting up test database configuration...${NC}"
TEST_CONFIG="$REPO_ROOT/config/test_database.conf"
cat > "$TEST_CONFIG" << 'EOF'
# Test Database Configuration
# Used for Phase 1 testing and validation

[database]
type = sqlite
path = :memory:
timeout = 30
check_same_thread = false

[logging]
level = DEBUG
file = test.log

[testing]
fixture_dir = tests/fixtures
use_sample_data = true
cleanup_after_tests = true
EOF
log_step "Test database config created: $TEST_CONFIG"

# Step 7: Create test fixtures directory
echo -e "${BLUE}Step 7: Creating test fixtures...${NC}"
mkdir -p "$REPO_ROOT/tests/fixtures"
mkdir -p "$REPO_ROOT/tests/fixtures/sample_data"
mkdir -p "$REPO_ROOT/tests/fixtures/expected_outputs"
log_step "Test fixtures directory structure created"

# Step 8: Create baseline performance metrics file
echo -e "${BLUE}Step 8: Initializing performance baseline...${NC}"
BASELINE_FILE="$REPO_ROOT/docs/phase1-performance-baseline.md"
cat > "$BASELINE_FILE" << 'EOF'
# Phase 1 Performance Baseline Metrics

## Baseline Metrics (Established: $(date +%Y-%m-%d))

### Configuration Framework (Task 1.1)
- Configuration loading time: TBD (target: < 500ms)
- Schema validation: TBD (target: < 100ms)
- Test coverage: TBD (target: 90%+)

### Mathematical Solvers (Task 1.2)
- Solver execution time: TBD (target: < 1 second per calculation)
- Numerical accuracy: TBD (target: 0.1% of reference)
- Registry lookup time: TBD (target: < 10ms)

### Common Utilities (Task 1.3)
- Utility function performance: TBD
- Deduplication completeness: TBD (target: 100%)
- Test coverage: TBD (target: 100%)

### Data Models (Task 1.4)
- Model instantiation time: TBD
- Validation time: TBD
- Database operations: TBD
- Test coverage: TBD (target: 100%)

### Database Integration (Task 1.5)
- Connection pool creation: TBD
- Query execution time: TBD (target: < 500ms typical)
- Connection acquisition: TBD (target: < 100ms)
- Test coverage: TBD (target: 90%+)

## Notes
- Baseline established at start of Phase 1
- Updated after each sprint
- Used for performance regression detection
EOF
log_step "Performance baseline initialized: $BASELINE_FILE"

# Step 9: Create Phase 1 execution log
echo -e "${BLUE}Step 9: Creating Phase 1 execution tracking...${NC}"
EXEC_LOG="$REPO_ROOT/docs/phase1-execution-log.md"
cat > "$EXEC_LOG" << 'EOF'
# Phase 1 Execution Log

## Overview
- Start Date: $(date +%Y-%m-%d)
- Team Lead: [To be assigned]
- Duration: 3 weeks (21 days)
- Target Completion: [To be calculated]

## Weekly Standups

### Week 1: Foundation Tasks Kickoff
- [ ] Monday: Kickoff meeting, team alignment
- [ ] Tuesday: Task 1.1 & 1.2 progress check
- [ ] Wednesday: Mid-week progress report
- [ ] Thursday: Code quality review
- [ ] Friday: Weekly summary and blockers

### Week 2: Parallel Work & Integration
- [ ] Monday: Task status review
- [ ] Tuesday: 1.3 & 1.4 parallel work check
- [ ] Wednesday: Integration testing begins
- [ ] Thursday: Code review updates
- [ ] Friday: Weekly summary

### Week 3: Completion & Integration
- [ ] Monday: Final task completion check
- [ ] Tuesday: Full integration testing
- [ ] Wednesday: Performance benchmarking
- [ ] Thursday: Code review completion
- [ ] Friday: Phase 1 completion review

## Task Progress

### Task 1.1: Configuration Framework
- Status: [Not started]
- Branch: feature/phase1-task-1.1-config-framework
- Assigned: Infrastructure Lead
- Progress: 0%

### Task 1.2: Mathematical Solvers
- Status: [Not started]
- Branch: feature/phase1-task-1.2-solvers-migration
- Assigned: Full-Stack Developer
- Progress: 0%

### Task 1.3: Utilities Deduplication
- Status: [Not started]
- Branch: feature/phase1-task-1.3-utilities-dedup
- Assigned: Both developers (parallel)
- Progress: 0%

### Task 1.4: Data Models
- Status: [Not started]
- Branch: feature/phase1-task-1.4-data-models
- Assigned: Full-Stack Developer
- Progress: 0%

### Task 1.5: Database Layer
- Status: [Not started]
- Branch: feature/phase1-task-1.5-database-layer
- Assigned: Infrastructure Lead
- Progress: 0%

## Blockers & Issues
[To be populated during execution]

## Decisions & Notes
[To be populated during execution]
EOF
log_step "Execution log created: $EXEC_LOG"

# Step 10: Verify GitHub issues
echo -e "${BLUE}Step 10: Verifying GitHub Phase 1 issues...${NC}"
if command -v gh &> /dev/null; then
    log_info "Checking GitHub issues #123-#127..."
    for issue in 123 124 125 126 127; do
        if gh issue view $issue &> /dev/null; then
            log_step "Issue #$issue found"
        else
            log_warn "Issue #$issue not found"
        fi
    done
else
    log_warn "GitHub CLI (gh) not available, skipping issue verification"
fi

# Step 11: Create process documentation
echo -e "${BLUE}Step 11: Creating process documentation...${NC}"
PROCESS_DOC="$REPO_ROOT/docs/phase1-processes.md"
cat > "$PROCESS_DOC" << 'EOF'
# Phase 1 Processes & Workflows

## Daily Standup Process
- **Time**: 9:00 AM UTC (adjust for timezone)
- **Duration**: 15 minutes
- **Format**: Each developer reports:
  1. What was completed yesterday
  2. What will be completed today
  3. Any blockers or dependencies

## Code Review Process
- **Reviewers**: Minimum 2 reviewers per PR
- **Target Review Time**: < 24 hours
- **Coverage Requirement**: 90%+ test coverage minimum
- **Checks**:
  - Automated tests passing
  - Code quality checks passing
  - Performance benchmarks acceptable
  - Documentation updated

## Testing Requirements
- **Unit Tests**: 100% for new code
- **Integration Tests**: All module interactions
- **Performance Tests**: Specified in task specs
- **Coverage Target**: 90%+ minimum

## Merge Criteria
- [ ] All tests passing (local + CI/CD)
- [ ] 2+ approved reviews
- [ ] Coverage >= 90%
- [ ] No merge conflicts
- [ ] Documentation updated
- [ ] Task specification checkboxes complete

## Escalation Path
1. **Technical Issues**: Tag Infrastructure Lead
2. **Design Issues**: Team discussion in standup
3. **Timeline Issues**: Escalate to project lead
4. **Blockers**: Immediate escalation

## Tools & Access
- **GitHub**: Issues, PRs, project board
- **CI/CD**: GitHub Actions (phase1-consolidation.yml)
- **Communication**: Daily standups + Slack/chat
- **Documentation**: /docs/PHASE_1_TASK_SPECIFICATIONS.md
EOF
log_step "Process documentation created: $PROCESS_DOC"

# Step 12: Create pre-execution checklist
echo -e "${BLUE}Step 12: Creating pre-execution checklist...${NC}"
CHECKLIST="$REPO_ROOT/docs/phase1-preflight-checklist.md"
cat > "$CHECKLIST" << 'EOF'
# Phase 1 Pre-Execution Checklist

## ✓ Infrastructure Setup
- [x] GitHub Actions CI/CD workflow created (phase1-consolidation.yml)
- [x] Feature branches created for all 5 tasks
- [x] Test environment prepared
- [x] Virtual environment configured
- [x] Test fixtures directory structure created
- [x] Performance baseline initialized

## ✓ Documentation Ready
- [x] PHASE_1_TASK_SPECIFICATIONS.md (2,000+ lines)
- [x] ACEENGINEERCODE_CONSOLIDATION_MIGRATION_PLAN.md
- [x] Process documentation (phase1-processes.md)
- [x] Execution log (phase1-execution-log.md)
- [x] Performance baseline (phase1-performance-baseline.md)

## ✓ GitHub Issues
- [x] Issue #123: Task 1.1 Configuration Framework
- [x] Issue #124: Task 1.2 Mathematical Solvers
- [x] Issue #125: Task 1.3 Utilities Deduplication
- [x] Issue #126: Task 1.4 Data Models
- [x] Issue #127: Task 1.5 Database Layer

## ⏳ Pending: Team Alignment
- [ ] Confirm Infrastructure Lead availability (Tasks 1.1, 1.5)
- [ ] Confirm Full-Stack Developer availability (Tasks 1.2, 1.4)
- [ ] Schedule kickoff meeting
- [ ] Review PHASE_1_TASK_SPECIFICATIONS.md together
- [ ] Establish daily standup time
- [ ] Set up communication channels

## ⏳ Pending: Environment Configuration
- [ ] Set up test database access (SQL Server clone)
- [ ] Configure database fixtures
- [ ] Set performance benchmarking tools
- [ ] Create GitHub project board for Phase 1

## ✓ Ready to Execute
Once team alignment is complete, Phase 1 execution can begin immediately.

Target Start Date: [To be scheduled]
Target Completion: [3 weeks from start]
EOF
log_step "Pre-execution checklist created: $CHECKLIST"

# Final summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Phase 1 Test Environment Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Setup Summary:"
echo "- Test virtual environment: $TEST_VENV"
echo "- Test database config: $TEST_CONFIG"
echo "- Performance baseline: $BASELINE_FILE"
echo "- Execution log: $EXEC_LOG"
echo "- Process doc: $PROCESS_DOC"
echo "- Preflight checklist: $CHECKLIST"
echo ""
echo "Next Steps:"
echo "1. Review the preflight checklist: $CHECKLIST"
echo "2. Schedule team kickoff meeting"
echo "3. Confirm developer availability"
echo "4. Create GitHub project board"
echo "5. Begin Phase 1 execution"
echo ""
echo "Feature Branches Created:"
git branch | grep "phase1-task" | sed 's/^/  - /'
echo ""
echo -e "${GREEN}Environment ready for Phase 1!${NC}"
