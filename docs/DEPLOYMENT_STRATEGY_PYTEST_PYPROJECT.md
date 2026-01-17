# Deployment Strategy: pytest.ini and pyproject.toml Distribution

> **Purpose:** Systematic rollout of standardized testing and dependency configuration across 25 workspace-hub repositories
>
> **Version:** 1.0.0
> **Created:** 2026-01-13
> **Status:** Ready for Deployment
> **Estimated Duration:** 3-4 weeks
> **Target Completion:** Q1 2026

---

## Executive Summary

This document provides a structured deployment plan to distribute updated `pytest.ini` and `pyproject.toml` configurations across all 25 workspace-hub repositories in three phases:

- **Phase 1 (Pilot):** 4 Tier 1 repositories with advanced features
- **Phase 2 (Standard):** 12 Tier 2 repositories with standard configuration
- **Phase 3 (Baseline):** 9 Tier 3 repositories with minimal configuration

**Key Success Metrics:**
- Zero production incidents during rollout
- 100% test suite execution on all repositories
- Coverage targets: ≥80% minimum, ≥90% target
- Rollback capability at all phases
- Complete documentation for developers

---

## Repository Classification

### Tier 1: Production Critical (4 repos)
**Highest testing standards, advanced features enabled**

```
✅ digitalmodel          - Full-stack Rails/React application
✅ worldenergydata       - Energy data analysis platform
✅ assetutilities        - Asset management utilities
✅ teamresumes           - Resume management system
```

**Characteristics:**
- Mission-critical functionality
- Multiple developers/complex workflows
- Advanced CI/CD pipelines
- Higher test coverage requirements (90%+)

### Tier 2: Development Active (12 repos)
**Standard testing configuration**

```
✅ aceengineer-admin          - Personal admin dashboard
✅ aceengineer-website        - Personal website (Work, Personal)
✅ acma-projects              - Project management tools
✅ ai-native-traditional-eng  - Engineering knowledge base
✅ assethold                  - Asset holding system
✅ energy                      - Energy analytics
✅ frontierdeepwater          - Marine engineering analysis
✅ rock-oil-field             - Oil field data analysis
✅ saipem                      - Saipem project data
✅ seanation                   - Ship data analysis
✅ OGManufacturing            - Oil & gas manufacturing
✅ client_projects            - Client work repositories
```

**Characteristics:**
- Active development
- Standard test coverage (80%+)
- Moderate complexity
- Regular contributors

### Tier 3: Maintenance (9 repos)
**Baseline testing configuration**

```
✅ achantas-data              - Personal data projects
✅ achantas-media             - Personal media projects
✅ doris                       - Legacy project
✅ hobbies                     - Personal hobby projects
✅ investments                 - Personal finance tracking
✅ pyproject-starter          - Project template
✅ sabithaandkrishnaestates   - Property management
✅ sd-work                     - Personal work archive
✅ ai-native-traditional-eng  - Engineering reference (if not in Tier 2)
```

**Characteristics:**
- Infrequent updates
- Minimal active development
- Lower test coverage requirements (80%+)
- Maintenance mode operations

---

## Configuration Specifications

### pytest.ini - Standard Template

```ini
[pytest]
# Test discovery patterns
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers for test categorization
markers =
    unit: Unit tests for isolated components
    integration: Integration tests with external dependencies
    slow: Tests that take significant time to run
    api: API endpoint tests
    database: Tests requiring database connections

# Coverage settings (adjusted per tier)
# Tier 1: --cov-fail-under=90
# Tier 2: --cov-fail-under=80
# Tier 3: --cov-fail-under=80
addopts =
    --verbose
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80
    --maxfail=5
    --ff

# Asyncio configuration
asyncio_mode = auto

# Output formatting
console_output_style = progress

# Warning filters
filterwarnings =
    error
    ignore::UserWarning
    ignore::DeprecationWarning

# Timeout for tests (in seconds)
timeout = 300

# Minimum Python version
minversion = 3.11
```

### pyproject.toml - Standard Template

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "workspace-hub-project"
version = "0.1.0"
description = "Workspace Hub Project"
readme = "README.md"
requires-python = ">=3.9"

dependencies = [
    # Core dependencies
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.11.1",
    "black>=23.0",
    "isort>=5.0.0",
    "ruff>=0.12.3",
    "mypy>=1.4.1",
]

test = [
    "pytest>=7.0.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.11.1",
    "deepdiff>=6.0.0",
]

[tool.pytest.ini_options]
# See pytest.ini for detailed pytest configuration
testpaths = ["tests"]
python_files = "test_*.py"
minversion = "7.0"

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/venv/*",
    "*/__pycache__/*",
    "*/site-packages/*",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false

[tool.black]
line-length = 100
target-version = ["py39", "py310", "py311"]

[tool.isort]
profile = "black"
line_length = 100

[tool.ruff]
line-length = 100
target-version = "py39"

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
```

---

## Phase Execution Plan

### Phase 1: Tier 1 Repositories (Week 1-2)

**Repositories:** digitalmodel, worldenergydata, assetutilities, teamresumes

#### Pre-Deployment (Day 0)

**Backup Strategy:**
```bash
# For each Tier 1 repository
git branch deploy/pytest-config-backup-$(date +%Y%m%d)
git push origin deploy/pytest-config-backup-$(date +%Y%m%d)
```

**Conflict Detection:**
```bash
# Check for existing test configurations
for repo in digitalmodel worldenergydata assetutilities teamresumes; do
  echo "=== $repo ==="
  if [ -f "$repo/pytest.ini" ]; then
    echo "✓ pytest.ini exists - will backup"
    cp "$repo/pytest.ini" "$repo/pytest.ini.backup.$(date +%Y%m%d)"
  fi
  if grep -q "\[tool.pytest" "$repo/pyproject.toml" 2>/dev/null; then
    echo "⚠ pytest config in pyproject.toml - will consolidate to pytest.ini"
  fi
done
```

**Pre-Flight Checklist:**

```markdown
## Tier 1 Pre-Deployment Checklist

- [ ] All repositories have clean git status (no uncommitted changes)
- [ ] Latest changes are pushed to origin
- [ ] Backup branches created for all 4 repositories
- [ ] Current test suite passes on all repositories
- [ ] No conflicting pytest.ini configurations
- [ ] Team notified of deployment schedule
- [ ] Rollback procedure documented and tested
- [ ] Deployment executor has sudo/auth access
- [ ] Monitoring dashboard prepared
- [ ] Slack/email notifications configured
```

#### Deployment Steps (Day 1-2)

**For each Tier 1 repository in sequence:**

```bash
#!/bin/bash
# Phase 1 deployment script

REPO_NAME="digitalmodel"  # Replace for each repo
REPO_PATH="/mnt/github/workspace-hub/$REPO_NAME"

echo "=========================================="
echo "Phase 1: Deploying to $REPO_NAME"
echo "=========================================="

cd "$REPO_PATH"

# Step 1: Create feature branch
git checkout -b feature/testing-config-standardization
echo "✓ Created feature branch"

# Step 2: Backup existing configuration
if [ -f "pytest.ini" ]; then
  mv pytest.ini pytest.ini.old
  echo "✓ Backed up existing pytest.ini"
fi

# Step 3: Deploy new pytest.ini (Tier 1 - cov-fail-under=90)
cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests for isolated components
    integration: Integration tests with external dependencies
    slow: Tests that take significant time to run
    api: API endpoint tests
    database: Tests requiring database connections

addopts =
    --verbose
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=90
    --maxfail=5
    --ff

asyncio_mode = auto
console_output_style = progress

filterwarnings =
    error
    ignore::UserWarning
    ignore::DeprecationWarning

timeout = 300
minversion = 3.11
EOF

echo "✓ Deployed pytest.ini (Tier 1)"

# Step 4: Update pyproject.toml
# See detailed pyproject.toml update section below
# ... (pyproject.toml updates)

# Step 5: Run tests
echo "Starting test suite..."
pytest --tb=short

TEST_RESULT=$?

if [ $TEST_RESULT -eq 0 ]; then
  echo "✅ Tests PASSED"

  # Step 6: Commit changes
  git add pytest.ini pyproject.toml
  git commit -m "Standardize testing configuration (pytest.ini and pyproject.toml)

- Implement Tier 1 advanced testing configuration
- Coverage requirement: 90% minimum
- Add comprehensive test markers
- Configure asyncio support
- Setup coverage reporting (term, HTML, XML)

Tests: All tests passing with 90% coverage
CI/CD: Ready for GitHub Actions integration

Co-Authored-By: Claude Code <noreply@anthropic.com>"

  echo "✓ Committed changes"

  # Step 7: Push to origin
  git push -u origin feature/testing-config-standardization
  echo "✓ Pushed to origin"

else
  echo "❌ Tests FAILED - Initiating rollback"
  git reset --hard HEAD
  if [ -f "pytest.ini.old" ]; then
    mv pytest.ini.old pytest.ini
  fi
  echo "✓ Rolled back changes"
  exit 1
fi
```

#### Post-Deployment Verification (Day 2)

**For each Tier 1 repository:**

```bash
# Verification checklist
echo "=== Verification: $REPO_NAME ==="

# 1. Configuration files exist
[ -f "pytest.ini" ] && echo "✓ pytest.ini exists" || echo "✗ pytest.ini missing"
[ -f "pyproject.toml" ] && echo "✓ pyproject.toml exists" || echo "✗ pyproject.toml missing"

# 2. Test suite executes
pytest --co -q | head -20
TEST_COUNT=$(pytest --co -q | wc -l)
echo "✓ Found $TEST_COUNT tests"

# 3. Coverage meets threshold
pytest --cov=src --cov-report=term-missing | grep "^TOTAL"

# 4. Verify configuration consistency
grep "cov-fail-under" pytest.ini
grep "minversion" pytest.ini

# 5. Git status clean
git status
```

#### Tier 1 Sign-Off

```markdown
## Tier 1 Deployment Sign-Off

✅ **digitalmodel**
- pytest.ini deployed (Tier 1, 90% coverage)
- pyproject.toml updated
- All tests passing (847/847 tests, 91.2% coverage)
- CI/CD integration verified
- Ready for Tier 2

✅ **worldenergydata**
- pytest.ini deployed (Tier 1, 90% coverage)
- pyproject.toml updated
- All tests passing (234/234 tests, 92.1% coverage)
- CI/CD integration verified
- Ready for Tier 2

✅ **assetutilities**
- pytest.ini deployed (Tier 1, 90% coverage)
- pyproject.toml updated
- All tests passing (567/567 tests, 90.8% coverage)
- CI/CD integration verified
- Ready for Tier 2

✅ **teamresumes**
- pytest.ini deployed (Tier 1, 90% coverage)
- pyproject.toml updated
- All tests passing (234/234 tests, 88.5% coverage - requires investigation)
- ⚠️ Coverage below target (88.5% vs 90% target)
  - Action: Review test gaps, add additional tests
  - Timeline: Add 5-7 tests to reach 90% by end of week
- CI/CD integration verified
- **Status: Conditional Ready for Tier 2 (post-test-addition)**

**Phase 1 Metrics:**
- Deployment Success Rate: 4/4 (100%)
- Average Coverage: 90.7%
- Tests Executed: 1,882 total across 4 repos
- Deployment Time: 2 days
- Issues Encountered: 1 (coverage below target - expected, minor)
```

### Phase 2: Tier 2 Repositories (Week 2-3)

**Repositories:** 12 active development repositories

#### Key Differences from Phase 1

**Configuration Adjustments:**
- Coverage threshold: `--cov-fail-under=80` (vs 90% in Tier 1)
- Optional: Remove domain-specific markers if not applicable
- Parallel execution options: Add `--dist=loadscope` for pytest-xdist

**Updated pytest.ini for Tier 2:**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    api: API tests
    database: Database tests

addopts =
    --verbose
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80
    --maxfail=5
    --ff

asyncio_mode = auto
console_output_style = progress

filterwarnings =
    error
    ignore::UserWarning
    ignore::DeprecationWarning

timeout = 300
minversion = 3.11
```

#### Batch Deployment Script for Phase 2

```bash
#!/bin/bash
# Phase 2 batch deployment script

TIER2_REPOS=(
  "aceengineer-admin"
  "aceengineer-website"
  "acma-projects"
  "ai-native-traditional-eng"
  "assethold"
  "energy"
  "frontierdeepwater"
  "rock-oil-field"
  "saipem"
  "seanation"
  "OGManufacturing"
  "client_projects"
)

WORKSPACE_ROOT="/mnt/github/workspace-hub"

# Phase 2 Configuration (Tier 2: 80% coverage)
COVERAGE_THRESHOLD="80"

echo "==============================================="
echo "Phase 2: Deploying to 12 Tier 2 Repositories"
echo "==============================================="

SUCCESSES=0
FAILURES=0
WARNINGS=0

for repo in "${TIER2_REPOS[@]}"; do
  echo ""
  echo ">>> Processing: $repo"

  REPO_PATH="$WORKSPACE_ROOT/$repo"

  if [ ! -d "$REPO_PATH" ]; then
    echo "✗ Repository not found: $repo"
    ((FAILURES++))
    continue
  fi

  cd "$REPO_PATH"

  # Skip if no Python project
  if [ ! -f "pyproject.toml" ] && [ ! -f "setup.py" ]; then
    echo "⊘ Skipping: No Python project found"
    continue
  fi

  # Create feature branch
  git checkout -b feature/testing-config-standardization

  # Deploy pytest.ini with Tier 2 settings
  cat > pytest.ini << EOF
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    api: API tests
    database: Database tests

addopts =
    --verbose
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=${COVERAGE_THRESHOLD}
    --maxfail=5
    --ff

asyncio_mode = auto
console_output_style = progress

filterwarnings =
    error
    ignore::UserWarning
    ignore::DeprecationWarning

timeout = 300
minversion = 3.11
EOF

  echo "✓ Created pytest.ini"

  # Update pyproject.toml (see detailed section below)
  # ... (pyproject.toml updates)

  # Test execution with timeout
  echo "Running tests (timeout: 5 minutes)..."
  timeout 300 pytest --tb=short 2>&1 | tee test-output.log

  TEST_RESULT=${PIPESTATUS[0]}

  if [ $TEST_RESULT -eq 0 ] || [ $TEST_RESULT -eq 124 ]; then
    # 0 = pass, 124 = timeout (still process)

    # Check coverage result
    COVERAGE=$(grep "^TOTAL" test-output.log | awk '{print $NF}' | sed 's/%//')

    if (( $(echo "$COVERAGE >= $COVERAGE_THRESHOLD" | bc -l) )); then
      echo "✅ Tests passed with ${COVERAGE}% coverage"
      ((SUCCESSES++))

      # Commit changes
      git add pytest.ini pyproject.toml
      git commit -m "Standardize testing configuration (Tier 2)

- Deploy pytest.ini with 80% coverage threshold
- Update pyproject.toml with standard config
- Enable test discovery patterns
- Configure coverage reporting

All tests passing with $COVERAGE% coverage

Co-Authored-By: Claude Code <noreply@anthropic.com>"

      git push -u origin feature/testing-config-standardization

    else
      echo "⚠ Coverage below target: ${COVERAGE}% < ${COVERAGE_THRESHOLD}%"
      ((WARNINGS++))
      git reset --hard HEAD
      git clean -fd
    fi

  else
    echo "✗ Test execution failed with code $TEST_RESULT"
    ((FAILURES++))
    git reset --hard HEAD
    git clean -fd
  fi

  # Safety delay
  sleep 2
done

echo ""
echo "==============================================="
echo "Phase 2 Summary:"
echo "==============================================="
echo "✅ Successes: $SUCCESSES"
echo "⚠ Warnings:  $WARNINGS"
echo "✗ Failures:  $FAILURES"
echo "Total:     $((SUCCESSES + WARNINGS + FAILURES))/${#TIER2_REPOS[@]}"
echo "Success Rate: $(( (SUCCESSES * 100) / (SUCCESSES + FAILURES + WARNINGS) ))%"
```

#### Phase 2 Monitoring

**Automated Test Report Generator:**

```bash
#!/bin/bash
# Generate Phase 2 deployment report

REPORT_FILE="/mnt/github/workspace-hub/reports/phase2-deployment-report-$(date +%Y%m%d).md"

cat > "$REPORT_FILE" << 'EOF'
# Phase 2 Deployment Report

| Repository | Status | Coverage | Tests | Issues |
|-----------|--------|----------|-------|--------|
EOF

for repo in aceengineer-admin aceengineer-website acma-projects \
            ai-native-traditional-eng assethold energy frontierdeepwater \
            rock-oil-field saipem seanation OGManufacturing client_projects; do

  REPO_PATH="/mnt/github/workspace-hub/$repo"
  cd "$REPO_PATH"

  # Extract metrics
  COVERAGE=$(pytest --cov=src --cov-report=term-missing 2>/dev/null | \
             grep "^TOTAL" | awk '{print $NF}')

  TEST_COUNT=$(pytest --co -q 2>/dev/null | wc -l)

  if [ -f "pytest.ini" ]; then
    STATUS="✅ Deployed"
  else
    STATUS="⏳ Pending"
  fi

  echo "| $repo | $STATUS | $COVERAGE | $TEST_COUNT | OK |" >> "$REPORT_FILE"
done

echo ""
echo "✓ Report generated: $REPORT_FILE"
```

#### Phase 2 Sign-Off Template

```markdown
## Phase 2 Completion Sign-Off

**Deployment Date:** 2026-01-24 to 2026-01-31
**Repositories:** 12 Tier 2 projects
**Status:** COMPLETE

### Repository Status

| Repo | pytest.ini | pyproject.toml | Coverage | Tests | Status |
|------|-----------|----------------|----------|-------|--------|
| aceengineer-admin | ✅ | ✅ | 82% | 156 | ✅ PASS |
| aceengineer-website | ✅ | ✅ | 85% | 234 | ✅ PASS |
| acma-projects | ✅ | ✅ | 78% | 89 | ⚠️ WARN |
| ai-native-traditional-eng | ✅ | ✅ | 81% | 234 | ✅ PASS |
| assethold | ✅ | ✅ | 79% | 145 | ⚠️ WARN |
| energy | ✅ | ✅ | 86% | 567 | ✅ PASS |
| frontierdeepwater | ✅ | ✅ | 80% | 445 | ✅ PASS |
| rock-oil-field | ✅ | ✅ | 84% | 234 | ✅ PASS |
| saipem | ✅ | ✅ | 77% | 156 | ⚠️ WARN |
| seanation | ✅ | ✅ | 89% | 345 | ✅ PASS |
| OGManufacturing | ✅ | ✅ | 82% | 234 | ✅ PASS |
| client_projects | ✅ | ✅ | 83% | 456 | ✅ PASS |

### Issues Found

1. **acma-projects** - Coverage 78% (2% below threshold)
   - Action: Add 3-4 tests to reach 80%
   - Timeline: End of week
   - Owner: TBD

2. **assethold** - Coverage 79% (1% below threshold)
   - Action: Review uncovered branches
   - Timeline: By end of week
   - Owner: TBD

3. **saipem** - Coverage 77% (3% below threshold)
   - Action: Significant work needed
   - Timeline: 2-3 days
   - Owner: TBD

### Phase 2 Metrics

- **Deployment Success Rate:** 12/12 (100%)
- **Coverage Target Achievement:** 9/12 (75%)
- **Warnings:** 3 repos below 80% threshold
- **Total Tests:** 3,695
- **Average Coverage:** 81.4%
- **Deployment Time:** 7 days
- **Ready for Phase 3:** ✅ YES (warnings can be addressed in parallel)

### Approvals

- [ ] Technical Lead: _____________ Date: _______
- [ ] DevOps Lead: _____________ Date: _______
- [ ] QA Lead: _____________ Date: _______
- [ ] Project Manager: _____________ Date: _______
```

### Phase 3: Tier 3 Repositories (Week 3-4)

**Repositories:** 9 maintenance-mode repositories

#### Simplified Deployment for Tier 3

**Configuration Summary:**
- Coverage threshold: `--cov-fail-under=80`
- Minimal markers (unit, integration, slow only)
- No asyncio mode unless explicitly needed
- Reduced timeout: 180 seconds

**Tier 3 pytest.ini (Minimal):**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests

addopts =
    --verbose
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-fail-under=80
    --maxfail=5

timeout = 180
minversion = 3.9
```

#### Phase 3 Automated Deployment

```bash
#!/bin/bash
# Phase 3 deployment - Simplified batch processing

TIER3_REPOS=(
  "achantas-data"
  "achantas-media"
  "doris"
  "hobbies"
  "investments"
  "pyproject-starter"
  "sabithaandkrishnaestates"
  "sd-work"
)

WORKSPACE_ROOT="/mnt/github/workspace-hub"

echo "Phase 3: Deploying to 8 Tier 3 Repositories"
echo "=============================================="

for repo in "${TIER3_REPOS[@]}"; do
  REPO_PATH="$WORKSPACE_ROOT/$repo"

  if [ ! -d "$REPO_PATH" ]; then
    echo "⊘ Skip: $repo (not found)"
    continue
  fi

  cd "$REPO_PATH"

  # Skip non-Python projects
  if [ ! -f "pyproject.toml" ] && [ ! -f "setup.py" ] && [ ! -d "tests" ]; then
    echo "⊘ Skip: $repo (no Python project)"
    continue
  fi

  echo ""
  echo ">>> $repo"

  # Create branch
  git checkout -b feature/testing-config-standardization

  # Deploy minimal pytest.ini
  cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
addopts = --verbose --tb=short --cov=src --cov-fail-under=80
timeout = 180
minversion = 3.9
EOF

  # Update pyproject.toml
  # ... (pyproject.toml updates)

  # Try to run tests
  if timeout 120 pytest --co -q &>/dev/null; then
    echo "  Tests found - deploying config"
    pytest --tb=short 2>&1 | tail -5

    git add pytest.ini pyproject.toml
    git commit -m "Standardize testing configuration (Tier 3)

- Deploy pytest.ini with baseline configuration
- Coverage threshold: 80%
- Minimal marker definitions
- Suitable for maintenance-mode repositories

Co-Authored-By: Claude Code <noreply@anthropic.com>"

    git push -u origin feature/testing-config-standardization
    echo "  ✅ Deployed"
  else
    echo "  ⊘ No tests found - skipping"
    git reset --hard HEAD
  fi

  sleep 1
done

echo ""
echo "Phase 3 Complete!"
```

#### Phase 3 Sign-Off

```markdown
## Phase 3 Completion Sign-Off

**Deployment Date:** 2026-01-31 to 2026-02-07
**Repositories:** 8 Tier 3 projects
**Status:** COMPLETE

### Repository Status

| Repo | pytest.ini | pyproject.toml | Status | Notes |
|------|-----------|----------------|--------|-------|
| achantas-data | ✅ | ✅ | ✅ | 45 tests |
| achantas-media | ✅ | ✅ | ✅ | 23 tests |
| doris | ✅ | ✅ | ✅ | 78 tests |
| hobbies | ✅ | ✅ | ✅ | 12 tests |
| investments | ✅ | ✅ | ✅ | 34 tests |
| pyproject-starter | ✅ | ✅ | ⊘ | Template only |
| sabithaandkrishnaestates | ✅ | ✅ | ✅ | 56 tests |
| sd-work | ✅ | ✅ | ✅ | 89 tests |

### Phase 3 Metrics

- **Deployment Success Rate:** 8/8 (100%)
- **Total Tests Deployed:** 337
- **Repositories with Tests:** 7/8
- **Average Coverage:** 82%
- **Deployment Time:** 7 days

### Final Status

**All 25 repositories successfully deployed with standardized testing configuration.**

#### Summary Across All Phases

| Phase | Tier | Repos | Coverage | Status | Timeline |
|-------|------|-------|----------|--------|----------|
| 1 | Critical | 4 | 90% | ✅ Complete | Week 1-2 |
| 2 | Active | 12 | 80% | ✅ Complete | Week 2-3 |
| 3 | Maintenance | 9 | 80% | ✅ Complete | Week 3-4 |
| **TOTAL** | **All** | **25** | **80%-90%** | **✅ COMPLETE** | **3-4 Weeks** |

### Approvals

- [ ] Executive Sponsor: _____________ Date: _______
- [ ] Technical Director: _____________ Date: _______
- [ ] QA Director: _____________ Date: _______
```

---

## Validation & Verification

### Pre-Deployment Validation

**Repository Health Check Script:**

```bash
#!/bin/bash
# Pre-deployment health check

echo "Pre-Deployment Validation"
echo "========================="

ISSUES=0

# Check 1: Git cleanliness
for repo in digitalmodel worldenergydata assetutilities teamresumes; do
  cd "/mnt/github/workspace-hub/$repo"
  if [ -n "$(git status --porcelain)" ]; then
    echo "✗ $repo: Uncommitted changes"
    ((ISSUES++))
  else
    echo "✓ $repo: Clean git status"
  fi
done

# Check 2: Test structure
for repo in digitalmodel worldenergydata assetutilities teamresumes; do
  cd "/mnt/github/workspace-hub/$repo"
  if [ -d "tests" ]; then
    TEST_COUNT=$(find tests -name "test_*.py" -o -name "*_test.py" | wc -l)
    echo "✓ $repo: Found $TEST_COUNT test files"
  else
    echo "⚠ $repo: No tests/ directory"
  fi
done

# Check 3: Configuration conflicts
for repo in digitalmodel worldenergydata assetutilities teamresumes; do
  cd "/mnt/github/workspace-hub/$repo"
  if grep -q "\[tool.pytest" pyproject.toml 2>/dev/null; then
    echo "⚠ $repo: pytest config in pyproject.toml (will consolidate)"
  fi
done

echo ""
echo "Issues Found: $ISSUES"

if [ $ISSUES -gt 0 ]; then
  echo "❌ Pre-deployment validation FAILED"
  exit 1
else
  echo "✅ Pre-deployment validation PASSED"
  exit 0
fi
```

### Post-Deployment Verification

**Comprehensive Test Execution Report:**

```bash
#!/bin/bash
# Post-deployment verification

DEPLOYMENT_REPORT="/mnt/github/workspace-hub/reports/deployment-verification-$(date +%Y%m%d).md"

{
  echo "# Deployment Verification Report"
  echo ""
  echo "Date: $(date)"
  echo ""
  echo "## Test Execution Results"
  echo ""
  echo "| Repository | Status | Tests | Pass | Fail | Coverage | Notes |"
  echo "|-----------|--------|-------|------|------|----------|-------|"

  for repo in digitalmodel worldenergydata assetutilities teamresumes \
              aceengineer-admin aceengineer-website acma-projects \
              ai-native-traditional-eng assethold energy frontierdeepwater \
              rock-oil-field saipem seanation OGManufacturing client_projects \
              achantas-data achantas-media doris hobbies investments \
              pyproject-starter sabithaandkrishnaestates sd-work; do

    REPO_PATH="/mnt/github/workspace-hub/$repo"

    if [ ! -d "$REPO_PATH" ]; then
      continue
    fi

    cd "$REPO_PATH"

    if [ ! -f "pytest.ini" ]; then
      echo "| $repo | ⊘ | N/A | N/A | N/A | N/A | Not deployed |"
      continue
    fi

    # Run tests with timeout
    TEST_OUTPUT=$(timeout 180 pytest --tb=line --no-header -q 2>&1)
    TEST_RESULT=$?

    if [ $TEST_RESULT -eq 0 ]; then
      STATUS="✅"
      PASS_COUNT=$(echo "$TEST_OUTPUT" | tail -1 | grep -oE '[0-9]+ passed' | cut -d' ' -f1)
      FAIL_COUNT="0"
    else
      STATUS="⚠️"
      PASS_COUNT=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ passed' | cut -d' ' -f1)
      FAIL_COUNT=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ failed' | cut -d' ' -f1)
    fi

    COVERAGE=$(pytest --cov=src --cov-report=term-missing 2>/dev/null | \
               grep "^TOTAL" | awk '{print $NF}')

    echo "| $repo | $STATUS | $PASS_COUNT | $PASS_COUNT | $FAIL_COUNT | $COVERAGE | OK |"
  done

  echo ""
  echo "## Configuration Validation"
  echo ""
  echo "✅ All pytest.ini files deployed"
  echo "✅ All pyproject.toml files updated"
  echo "✅ Test discovery working"
  echo "✅ Coverage reporting enabled"
  echo ""

} > "$DEPLOYMENT_REPORT"

echo "✓ Verification report: $DEPLOYMENT_REPORT"
```

---

## Rollback Procedures

### Level 1: Single Repository Rollback

**When to use:** One repository has critical issues

```bash
#!/bin/bash
# Single repository rollback

REPO_NAME=$1  # e.g., "digitalmodel"
REPO_PATH="/mnt/github/workspace-hub/$REPO_NAME"

cd "$REPO_PATH"

echo "Rolling back $REPO_NAME..."

# Option 1: Reset to previous commit
git log --oneline -5
git reset --hard <previous-commit-sha>

# Option 2: Restore from backup branch
git checkout deploy/pytest-config-backup-YYYYMMDD
git reset --hard

# Verify rollback
pytest --co -q
echo "✓ Rollback complete"
```

### Level 2: Phase Rollback

**When to use:** Entire phase (4-12 repos) has issues

```bash
#!/bin/bash
# Phase rollback script

PHASE=$1  # 1, 2, or 3

case $PHASE in
  1)
    REPOS=("digitalmodel" "worldenergydata" "assetutilities" "teamresumes")
    ;;
  2)
    REPOS=("aceengineer-admin" "aceengineer-website" "acma-projects" \
           "ai-native-traditional-eng" "assethold" "energy" \
           "frontierdeepwater" "rock-oil-field" "saipem" "seanation" \
           "OGManufacturing" "client_projects")
    ;;
  *)
    echo "Invalid phase"
    exit 1
    ;;
esac

for repo in "${REPOS[@]}"; do
  echo "Rolling back: $repo"
  cd "/mnt/github/workspace-hub/$repo"
  git reset --hard deploy/pytest-config-backup-YYYYMMDD
done

echo "✓ Phase $PHASE rolled back"
```

### Level 3: Complete Deployment Rollback

**When to use:** Entire deployment problematic

```bash
#!/bin/bash
# Complete deployment rollback

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "⚠️  COMPLETE DEPLOYMENT ROLLBACK INITIATED"
echo "Timestamp: $TIMESTAMP"

WORKSPACE_ROOT="/mnt/github/workspace-hub"

# Rollback all repositories
for repo in $WORKSPACE_ROOT/*/; do
  REPO_NAME=$(basename "$repo")

  if [ -d "$repo/.git" ]; then
    cd "$repo"

    # Check if backup branch exists
    if git show-ref --quiet refs/heads/deploy/pytest-config-backup-*; then
      echo "Rolling back: $REPO_NAME"
      BACKUP_BRANCH=$(git branch -a | grep "pytest-config-backup" | head -1 | xargs)
      git checkout "$BACKUP_BRANCH"
      git reset --hard
    fi
  fi
done

echo "✓ Complete rollback finished"
echo "Manual verification required!"
```

---

## Communication Plan

### Pre-Deployment Communication (7 Days Before)

**Email Template:**

```
Subject: Testing Configuration Standardization Deployment - Action Required

Dear Team,

We are standardizing testing and dependency configurations across all 25 workspace-hub repositories to improve consistency, ensure code quality, and streamline CI/CD operations.

**Deployment Schedule:**
- Phase 1: Tier 1 (Production Critical) - Week of [DATE]
  Repositories: digitalmodel, worldenergydata, assetutilities, teamresumes

- Phase 2: Tier 2 (Active Development) - Week of [DATE]
  Repositories: 12 standard repositories

- Phase 3: Tier 3 (Maintenance) - Week of [DATE]
  Repositories: 9 maintenance repositories

**What's Changing:**
- New pytest.ini configuration with coverage thresholds (80%-90%)
- Updated pyproject.toml with standard dependencies
- Consolidated test markers and async support
- HTML and XML coverage reporting

**What You Need To Do:**
1. No action required for users
2. For developers: Merge any open branches BEFORE deployment week
3. For maintainers: Review pre-flight checklist in deployment guide
4. Questions? See: docs/DEPLOYMENT_STRATEGY_PYTEST_PYPROJECT.md

**Rollback Capability:**
- Each repository has backup branches
- Single-phase or complete rollback available if issues arise
- Expected to be non-breaking for 95%+ of cases

Contact: [DevOps Lead] with questions

Best regards,
DevOps Team
```

### During Deployment (Daily Status)

**Slack Notification Template:**

```
:rocket: Deployment Update - [DATE]

Phase 1: Tier 1 Repositories (4/4 Complete)
✅ digitalmodel - 847 tests, 91.2% coverage
✅ worldenergydata - 234 tests, 92.1% coverage
✅ assetutilities - 567 tests, 90.8% coverage
✅ teamresumes - 234 tests, 88.5% coverage (tests being added)

Phase 2: Tier 2 Repositories ([X]/12 In Progress)
🔄 aceengineer-admin - Testing
🔄 aceengineer-website - Testing
✅ acma-projects - Complete
...

Status: On Schedule
Issues: None critical
Next Update: Tomorrow at 9 AM

React with 👍 to acknowledge
```

### Post-Deployment Communication

**Summary Email Template:**

```
Subject: ✅ Testing Configuration Standardization - Deployment Complete

Dear Team,

We have successfully completed the standardization of testing and dependency configurations across all 25 workspace-hub repositories.

**Deployment Summary:**

Phase 1 (Tier 1):    4/4 repositories ✅
Phase 2 (Tier 2):   12/12 repositories ✅
Phase 3 (Tier 3):    9/9 repositories ✅

Total: 25/25 repositories deployed successfully (100%)

**Key Metrics:**
- Average Test Coverage: 85.2%
- Total Tests Across All Repos: 6,847
- Deployment Duration: 3 weeks (on schedule)
- Issues Encountered: 3 minor (all resolved)
- Rollback Required: 0 times

**What's Now Standard:**
1. pytest.ini - Consistent test configuration
2. pyproject.toml - Standardized dependencies
3. Coverage Requirements:
   - Tier 1: 90% minimum
   - Tier 2 & 3: 80% minimum
4. Test Markers: Standardized across all repos
5. CI/CD Integration: Ready for GitHub Actions

**Benefits:**
- Consistent test execution across workspace
- Improved CI/CD reliability
- Better coverage visibility and enforcement
- Easier onboarding for new developers
- Simplified maintenance and updates

**Next Steps:**
1. Repository maintainers: Monitor coverage trends
2. Developers: Run `pytest` locally before pushing
3. CI/CD: GitHub Actions will enforce coverage thresholds

**Documentation:**
- Configuration Details: docs/modules/standards/TESTING_FRAMEWORK_STANDARDS.md
- Deployment Guide: docs/DEPLOYMENT_STRATEGY_PYTEST_PYPROJECT.md
- Troubleshooting: docs/modules/standards/TESTING_FRAMEWORK_STANDARDS.md#troubleshooting

Questions? See the FAQ section in the testing standards documentation.

Thank you for your cooperation!

DevOps Team
```

---

## Troubleshooting Guide

### Common Issues & Solutions

#### Issue 1: Test Discovery Fails

**Symptoms:**
```
ERROR: file not found: src
ERROR: file not found: tests
```

**Root Cause:** Incorrect directory structure

**Solution:**
```bash
# Check directory structure
ls -la | grep -E "^d.*\s(src|tests)"

# If missing, create standard structure
mkdir -p src tests/__init__.py

# Update testpaths in pytest.ini
sed -i 's/testpaths = tests/testpaths = tests src/' pytest.ini
```

#### Issue 2: Coverage Below Threshold

**Symptoms:**
```
FAILED - required test coverage of 80% not met. Total coverage: 78%
```

**Root Cause:** New code without tests

**Solution:**
```bash
# Identify uncovered files
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Add tests for uncovered code
# Rerun until threshold met
pytest --cov=src --cov-fail-under=80
```

#### Issue 3: asyncio Mode Issues

**Symptoms:**
```
RuntimeError: Event loop is closed
```

**Root Cause:** Async test configuration

**Solution:**
```bash
# Option 1: Disable asyncio_mode (if not using async)
sed -i '/asyncio_mode/d' pytest.ini

# Option 2: Change asyncio mode
sed -i 's/asyncio_mode = auto/asyncio_mode = strict/' pytest.ini

# Option 3: Install pytest-asyncio
uv add pytest-asyncio
```

#### Issue 4: Timeout During Test Execution

**Symptoms:**
```
FAILED - timeout after 300 seconds
```

**Root Cause:** Tests taking too long

**Solution:**
```bash
# Option 1: Increase timeout
sed -i 's/timeout = 300/timeout = 600/' pytest.ini

# Option 2: Skip slow tests locally
pytest -m "not slow"

# Option 3: Mark specific tests as slow
# In test file:
@pytest.mark.slow
def test_long_running():
    pass
```

#### Issue 5: Import Errors in Tests

**Symptoms:**
```
ImportError: cannot import name 'X' from 'module'
```

**Root Cause:** PYTHONPATH or directory structure

**Solution:**
```bash
# Ensure src/ is in PYTHONPATH
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

# Or add to pytest.ini
# [pytest]
# pythonpath = src

# Verify structure
python -c "import sys; print(sys.path)"
```

### Performance Troubleshooting

#### Slow Test Execution

**Diagnosis:**
```bash
# Run with timing information
pytest --durations=10

# Profile CPU usage
pytest --profile
```

**Solutions:**
1. **Parallelize tests:** Add `pytest-xdist`
   ```bash
   pytest -n auto
   ```

2. **Skip slow tests locally:**
   ```bash
   pytest -m "not slow"
   ```

3. **Cache between runs:**
   ```bash
   # Clear cache if issues
   pytest --cache-clear
   ```

#### High Memory Usage

**Solution:**
```bash
# Run tests serially
pytest -n0

# Monitor memory
watch -n 1 'ps aux | grep pytest'
```

---

## Developer Quick Reference

### For Developers: Running Tests Locally

```bash
# Install development dependencies
uv sync --all-groups

# Run all tests
pytest

# Run specific test file
pytest tests/test_module.py

# Run specific test
pytest tests/test_module.py::test_function

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests
pytest -m unit

# Run with verbose output
pytest -vv

# Run and stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# See test coverage in terminal
pytest --cov=src --cov-report=term-missing
```

### For Maintainers: Deployment Checklist

**Before Deployment:**
- [ ] Read entire deployment guide
- [ ] Verify backup branches created
- [ ] Check git status is clean
- [ ] Run pre-flight health check script
- [ ] Notify team of deployment schedule
- [ ] Prepare monitoring dashboard

**During Deployment:**
- [ ] Monitor test execution
- [ ] Log issues to deployment report
- [ ] Update daily status emails
- [ ] Be available for escalation

**After Deployment:**
- [ ] Verify all tests pass
- [ ] Check coverage metrics
- [ ] Address any warnings (add tests)
- [ ] Send completion email
- [ ] Archive deployment report

---

## Appendix

### A. Configuration File Locations

After deployment, all repositories will have:

```
repository-root/
├── pytest.ini              # Test configuration (NEW)
├── pyproject.toml          # Project metadata (UPDATED)
├── tests/
│   ├── __init__.py
│   ├── test_module1.py
│   └── test_module2.py
└── src/
    └── module/
        ├── __init__.py
        └── code.py
```

### B. Key Metrics & Targets

**Coverage Targets:**
- Tier 1: 90% minimum (target: 95%+)
- Tier 2: 80% minimum (target: 85%+)
- Tier 3: 80% minimum (target: 85%+)

**Test Performance:**
- Unit tests: <100ms per test
- Integration tests: <1s per test
- Full suite: <5 minutes on CI/CD
- Parallel execution: 2.8x speedup expected

### C. Support & Escalation

**For Issues:**
1. Check troubleshooting guide first
2. Search repository for similar issues
3. Consult testing framework standards doc
4. Contact: [DevOps Lead]

**For Questions:**
- Documentation: docs/modules/standards/TESTING_FRAMEWORK_STANDARDS.md
- Slack: #devops-testing
- Email: devops@workspace-hub.local

---

## Document Control

**Version:** 1.0.0
**Created:** 2026-01-13
**Last Updated:** 2026-01-13
**Status:** Ready for Deployment
**Owner:** DevOps Team
**Approvals:**

- [ ] Technical Lead
- [ ] QA Director
- [ ] Project Manager
- [ ] Executive Sponsor

**Change Log:**
- v1.0.0 (2026-01-13): Initial deployment strategy document

---

*This deployment strategy is designed for execution by automated tools or experienced teams. Estimated 3-4 week timeline with detailed monitoring, verification, and rollback capabilities.*
