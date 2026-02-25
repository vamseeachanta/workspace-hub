# pytest.ini Deployment Guide

> Universal pytest Configuration for workspace-hub
> Version: 1.0.0
> Created: 2025-01-13

## Overview

This guide explains how to deploy the standardized pytest.ini template across all 25 Python repositories in workspace-hub. The configuration is modular, tier-aware, and customizable per repository.

**Files in this package:**
- `pytest.ini` - Universal base template (use this as starting point)
- `pytest.tier1.ini` - Tier 1 override (production critical repos)
- `pytest.tier2.ini` - Tier 2 override (active development repos)
- `pytest.tier3.ini` - Tier 3 override (maintenance repos)
- `PYTEST_DEPLOYMENT_GUIDE.md` - This file

## Repository Classification

### Tier 1: Production Critical (85% coverage)
Repositories requiring the highest quality standards:
- **digitalmodel** - Full-stack application
- **energy** - Energy analytics platform
- **frontierdeepwater** - Marine engineering analysis

**Characteristics:** Strict coverage, conservative timeouts, limited parallelization

### Tier 2: Development Active (80% coverage)
Actively developed repositories with good quality standards:
- **aceengineercode** - Engineering code library
- **assetutilities** - Asset management utilities
- **worldenergydata** - Energy data analysis
- **rock-oil-field** - Oil field analysis
- **teamresumes** - Resume management

**Characteristics:** Balanced coverage, moderate timeouts, good parallelization

### Tier 3: Maintenance (75% coverage)
Maintenance and experimental repositories:
- **All others** - Includes: doris, saipem, OGManufacturing, seanation, hobbies, investments, sabithaandkrishnaestates, sd-work, acma-projects, achantas-data, achantas-media, achantas-training, aceengineer-admin, aceengineer-website, client_projects, pyproject-starter, etc.

**Characteristics:** Relaxed coverage, flexible timeouts, full parallelization

## Quick Start

### 1. Identify Your Repository's Tier

```bash
# Check your repository name and find it in the tier list above
# Example: "digitalmodel" → Tier 1

# Or check this file:
cat /mnt/github/workspace-hub/docs/REPOSITORY_TIER_CLASSIFICATION.md
```

### 2. Copy the Appropriate Template

**For Tier 1 (Production Critical):**
```bash
cp pytest.tier1.ini pytest.ini
```

**For Tier 2 (Development Active):**
```bash
cp pytest.tier2.ini pytest.ini
```

**For Tier 3 (Maintenance):**
```bash
cp pytest.tier3.ini pytest.ini
```

**Starting from base (customize as needed):**
```bash
cp pytest.ini pytest.ini
# Edit pytest.ini to adjust fail_under, timeout, etc.
```

### 3. Verify Installation

```bash
# Show pytest configuration
pytest --co

# Show all markers
pytest --markers

# Show all fixtures
pytest --fixtures

# Run tests with verbose output
pytest tests/ -v
```

### 4. Commit to Version Control

```bash
# Add pytest.ini to git
git add pytest.ini

# Commit with descriptive message
git commit -m "Add pytest.ini configuration

- Base coverage threshold: [75/80/85]%
- Test markers: unit, integration, e2e, slow, etc.
- Asyncio mode: auto
- Parallel execution: -n [4/8/12]

Based on workspace-hub universal template"

# Push to remote
git push origin feature-branch
```

## Configuration Details

### Coverage Threshold by Tier

| Tier | Threshold | Usage |
|------|-----------|-------|
| **Tier 1** | 85% | Production critical - non-negotiable |
| **Tier 2** | 80% | Active development - balanced quality |
| **Tier 3** | 75% | Maintenance - pragmatic quality |

**Override locally (development only):**
```bash
# Run tests without coverage enforcement
pytest --no-cov

# Run tests with custom threshold
pytest --cov --cov-fail-under=70

# Generate HTML coverage report
pytest --cov --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Markers Explained

Every test should have at least one PRIMARY marker (unit/integration/e2e) plus optional secondary markers.

**Primary Category (pick one):**
```python
@pytest.mark.unit
def test_calculate_discount():
    """Fast test of single function - <100ms, no I/O."""
    assert calculate_discount(100, 0.1) == 90

@pytest.mark.integration
def test_user_creation_workflow():
    """Test component interaction - <2s, real dependencies."""
    user = create_user("test@example.com")
    assert user.email == "test@example.com"

@pytest.mark.e2e
def test_complete_purchase_flow():
    """Test complete user workflow - slow, full system."""
    login() → add_to_cart() → checkout()
    assert order.status == "completed"
```

**Secondary Characteristics (add as needed):**
```python
@pytest.mark.unit
@pytest.mark.slow  # Takes >2 seconds
def test_something_slow():
    pass

@pytest.mark.integration
@pytest.mark.flaky  # Sometimes fails non-deterministically
def test_sometimes_fails():
    pass

@pytest.mark.integration
@pytest.mark.database  # Requires database
def test_with_database(db_session):
    pass

@pytest.mark.integration
@pytest.mark.api  # Makes API calls
def test_api_integration():
    pass
```

### Running Tests with Markers

```bash
# Run only unit tests (fast)
pytest -m unit

# Run unit and integration (skip e2e)
pytest -m "unit or integration"

# Skip slow tests (development iteration)
pytest -m "not slow"

# Skip tests requiring external services
pytest -m "not (database or api or selenium or llm)"

# Run only critical integration tests
pytest -m "integration and not slow"

# Rerun failed tests 3 times (for flaky tests)
pytest --reruns 3 -m flaky
```

### Parallel Execution

Requires: `pip install pytest-xdist`

```bash
# Auto-detect CPU count
pytest -n auto

# Tier 1: Limited parallelization (4 workers)
pytest -n 4

# Tier 2: Balanced parallelization (8 workers)
pytest -n 8

# Tier 3: Maximum parallelization (12 workers)
pytest -n 12

# Check what pytest-xdist options are available
pytest --help | grep -A 20 "xdist"
```

**NOTE:** Parallel execution may not work with:
- Database transactions (use test transactions instead)
- Shared file I/O (use temporary directories)
- Pytest plugins that modify test collection

### Coverage Reports

```bash
# Generate terminal report (missing lines)
pytest --cov=src --cov-report=term-missing

# Generate HTML report (visual coverage)
pytest --cov=src --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Generate XML for CI/CD (Codecov, Coveralls, etc.)
pytest --cov=src --cov-report=xml

# Combine multiple coverage reports
coverage combine
coverage report
```

## Installation Instructions

### 1. Install Required Packages

```bash
# Core testing
pip install pytest>=7.4.0

# Coverage reporting
pip install pytest-cov>=4.1.0

# Async test support
pip install pytest-asyncio>=0.21.0

# Mocking utilities
pip install pytest-mock>=3.11.1

# Parallel execution (optional)
pip install pytest-xdist>=3.3.0

# Test timeouts
pip install pytest-timeout>=2.1.0

# Performance benchmarking (optional)
pip install pytest-benchmark>=4.0.0

# Or install all at once
pip install pytest pytest-cov pytest-asyncio pytest-mock pytest-xdist pytest-timeout pytest-benchmark
```

### 2. Create pytest.ini in Repository Root

```bash
# Copy appropriate tier template
cp /path/to/pytest.tier2.ini ./pytest.ini

# Edit if needed
nano pytest.ini

# Verify configuration
pytest --co
```

### 3. Create conftest.py for Fixtures (if needed)

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {"key": "value"}

@pytest.fixture
def mock_service(mocker):
    """Mock external service."""
    return mocker.MagicMock()
```

## Customization Guide

### Add Repository-Specific Markers

Edit your local `pytest.ini`:

```ini
[pytest]
markers =
    # Standard markers (inherited)
    unit: Unit tests
    integration: Integration tests

    # Your custom markers
    economic_analysis: Economic calculation tests
    marine_simulation: Marine engineering simulations
    data_pipeline: ETL pipeline tests
```

### Override Settings Per Repository

Create `pytest.ini` in repository root with only the overrides:

```ini
# Override just the coverage threshold
[pytest]
fail_under = 78

# Override timeout for your slow tests
timeout = 600

# Add custom markers
markers =
    custom_marker: Your custom marker
```

### Skip Tests Locally

Temporarily disable markers during development:

```bash
# Skip slow tests while developing
alias pytest-fast='pytest -m "not slow"'
pytest-fast

# Skip flaky tests
pytest -m "not flaky"

# Skip external service tests
pytest -m "not (api or selenium or llm)"
```

## Continuous Integration Setup

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-xdist pytest-timeout

    - name: Run tests
      run: |
        # Run tests with coverage
        pytest --cov=src --cov-fail-under=80 -n 8

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
```

### Adjustments Per Tier

**Tier 1 (Production Critical):**
```yaml
# Stricter requirements
pytest --cov=src --cov-fail-under=85 -n 4
# Skip nothing - run all tests
# Fail on any warning
```

**Tier 2 (Development Active):**
```yaml
# Balanced requirements
pytest --cov=src --cov-fail-under=80 -n 8
# Skip slow e2e tests
# Allow some warnings
```

**Tier 3 (Maintenance):**
```yaml
# More relaxed
pytest --cov=src --cov-fail-under=75 -n 12
# Skip expensive tests (selenium, llm, scrapy)
# Focus on core functionality
```

## Troubleshooting

### Problem: "Unknown marker" error

**Cause:** Marker not defined in pytest.ini

**Solution:** Add marker to `markers` section in pytest.ini
```ini
markers =
    my_marker: Description of marker
```

### Problem: Tests hang indefinitely

**Cause:** No timeout set or timeout too long

**Solution:** Check timeout setting, increase if needed
```ini
timeout = 600  # seconds
```

### Problem: Coverage threshold not enforced

**Cause:** `--cov` or `--cov-fail-under` not in addopts

**Solution:** Add to addopts in pytest.ini
```ini
addopts = --cov=src --cov-fail-under=80
```

### Problem: Parallel tests fail when they pass individually

**Cause:** Tests have shared state

**Solution:** Use fixtures to isolate state
```python
@pytest.fixture
def clean_database():
    """Provide isolated database for test."""
    db = Database()
    yield db
    db.teardown()

def test_something(clean_database):
    # Uses isolated database
    pass
```

### Problem: Async tests not running

**Cause:** pytest-asyncio not installed or asyncio_mode not set

**Solution:** Install and configure
```bash
pip install pytest-asyncio
```

```ini
[pytest]
asyncio_mode = auto
```

### Problem: Flaky tests fail in CI but pass locally

**Cause:** Timing issues, race conditions, or environment differences

**Solution:**
1. Add `@pytest.mark.flaky` to test
2. Use `pytest --reruns 3` to rerun
3. Fix underlying race condition
4. Add explicit waits or mocks for timing

## Migration from Old Configuration

If your repository already has pytest.ini:

### Step 1: Back up existing configuration
```bash
cp pytest.ini pytest.ini.bak
```

### Step 2: Review differences
```bash
# Compare old vs new
diff pytest.ini.bak pytest.tier2.ini
```

### Step 3: Copy new template
```bash
cp pytest.tier2.ini pytest.ini
```

### Step 4: Add any custom markers back
```bash
# Edit pytest.ini and add back any custom markers
nano pytest.ini
```

### Step 5: Run tests to verify
```bash
pytest tests/ -v
```

### Step 6: Commit changes
```bash
git add pytest.ini
git commit -m "Upgrade pytest.ini to universal template

- Updated to workspace-hub standard configuration
- Maintained existing custom markers
- Coverage threshold: 80%
- Now supports parallel execution with -n 8"

git push origin feature-branch
```

## Best Practices

### ✅ DO

- ✅ Mark every test with at least one primary marker (unit/integration/e2e)
- ✅ Use `@pytest.fixture` for reusable test setup
- ✅ Mock external dependencies (APIs, databases, etc.)
- ✅ Keep unit tests under 100ms each
- ✅ Use descriptive test function names: `test_<feature>_<scenario>`
- ✅ Run `pytest -m unit` frequently during development
- ✅ Run full suite before committing
- ✅ Check coverage with `pytest --cov --cov-report=html`

### ❌ DON'T

- ❌ Create tests without markers
- ❌ Use module-level variables for test state (use fixtures instead)
- ❌ Make real API calls in tests (mock them)
- ❌ Skip failing tests - fix them immediately
- ❌ Commit code with coverage <threshold
- ❌ Ignore flaky test failures (they indicate bugs)
- ❌ Use `time.sleep()` in tests (use explicit waits instead)
- ❌ Forget to rollback database changes (use fixtures)

## Success Metrics

After deploying pytest.ini, you should see:

- ✅ Consistent test discovery across all 25 repositories
- ✅ Coverage threshold enforcement in CI/CD
- ✅ Reduced manual testing effort
- ✅ Faster feedback loop with parallel execution
- ✅ Better test organization with markers
- ✅ Easier onboarding for new developers
- ✅ Confidence in code changes

## Support

### Resources

- Official pytest documentation: https://docs.pytest.org/
- pytest-cov: https://pytest-cov.readthedocs.io/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/
- pytest-xdist: https://pytest-xdist.readthedocs.io/
- workspace-hub testing standards: @docs/modules/standards/TESTING_FRAMEWORK_STANDARDS.md

### Getting Help

```bash
# Show pytest version
pytest --version

# Show all available markers
pytest --markers

# Show all available fixtures
pytest --fixtures

# Get help on specific option
pytest --help | grep <option>

# Check if configuration is loaded
pytest --co -v
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-13 | Initial universal template with tier-specific overrides |

## Files Included

```
docs/templates/
├── pytest.ini              # Universal base template
├── pytest.tier1.ini        # Tier 1 override (85% coverage)
├── pytest.tier2.ini        # Tier 2 override (80% coverage)
├── pytest.tier3.ini        # Tier 3 override (75% coverage)
└── PYTEST_DEPLOYMENT_GUIDE.md  # This file
```

---

**Ready to deploy? Copy the appropriate template to your repository root and commit!**

```bash
# For your repository tier:
cp pytest.tier2.ini pytest.ini  # Example for Tier 2
git add pytest.ini
git commit -m "Add pytest.ini configuration"
git push
```
