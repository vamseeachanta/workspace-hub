# pytest.ini Universal Configuration Templates

> Standardized pytest configuration for all 25 workspace-hub repositories
> Version: 1.0.0
> Created: 2025-01-13

## 📦 Package Contents

This directory contains a complete, production-ready pytest configuration system for workspace-hub:

### Configuration Files

| File | Purpose | Usage |
|------|---------|-------|
| **pytest.ini** | Universal base template | Copy as starting point, customize as needed |
| **pytest.tier1.ini** | Tier 1 override (85% coverage) | Use for production-critical repos |
| **pytest.tier2.ini** | Tier 2 override (80% coverage) | Use for active development repos |
| **pytest.tier3.ini** | Tier 3 override (75% coverage) | Use for maintenance/experimental repos |

### Documentation Files

| File | Purpose |
|------|---------|
| **PYTEST_DEPLOYMENT_GUIDE.md** | Complete deployment and customization guide |
| **PYTEST_QUICK_REFERENCE.md** | One-page cheat sheet for developers |
| **README_PYTEST.md** | This file - overview and quick start |

### Automation Scripts

| File | Purpose |
|------|---------|
| **deploy_pytest_config.sh** | Automated deployment script for all 25 repos |

## 🚀 Quick Start (60 seconds)

### Step 1: Identify Your Repository's Tier

```bash
# Tier 1 (Production Critical - 85% coverage required)
# - digitalmodel, energy, frontierdeepwater

# Tier 2 (Active Development - 80% coverage required)
# - aceengineercode, assetutilities, worldenergydata, rock-oil-field, teamresumes

# Tier 3 (Maintenance/Experimental - 75% coverage required)
# - All others
```

### Step 2: Copy Template to Your Repository

```bash
# Navigate to your repository
cd /path/to/your/repository

# Copy the appropriate tier template
cp /mnt/github/workspace-hub/docs/templates/pytest.tier2.ini pytest.ini
```

### Step 3: Verify Installation

```bash
# Verify configuration is loaded
pytest --co

# Show all available markers
pytest --markers

# Run tests
pytest tests/ -v
```

### Step 4: Commit to Git

```bash
# Stage and commit
git add pytest.ini
git commit -m "Add pytest.ini configuration

- Universal template from workspace-hub
- Coverage threshold: 80% (adjust per tier)
- Supports parallel execution with -n 8"

# Push to remote
git push origin feature-branch
```

## 📋 Repository Tier Mapping

### Tier 1: Production Critical (85% Coverage)
**Repositories requiring strictest quality standards:**
- `digitalmodel` - Full-stack application
- `energy` - Energy analytics platform
- `frontierdeepwater` - Marine engineering analysis

**Use:** `pytest.tier1.ini`
**Characteristics:** Strict coverage, conservative parallelization, production-grade quality

### Tier 2: Development Active (80% Coverage)
**Actively developed repositories with good quality standards:**
- `aceengineercode` - Engineering code library
- `assetutilities` - Asset management utilities
- `worldenergydata` - Energy data analysis
- `rock-oil-field` - Oil field analysis
- `teamresumes` - Resume management

**Use:** `pytest.tier2.ini`
**Characteristics:** Balanced coverage, standard parallelization, good iteration speed

### Tier 3: Maintenance & Experimental (75% Coverage)
**Maintenance mode and experimental repositories:**
- All repositories not in Tier 1 or Tier 2
- Includes: doris, saipem, hobbies, sd-work, investments, etc.

**Use:** `pytest.tier3.ini`
**Characteristics:** Pragmatic coverage, maximum parallelization, flexible constraints

## 🎯 Key Features

### Comprehensive Test Marker System
```python
# Primary markers (pick one)
@pytest.mark.unit              # Fast single function tests
@pytest.mark.integration       # Component interaction tests
@pytest.mark.e2e              # Complete workflow tests

# Secondary markers (add as needed)
@pytest.mark.slow             # Tests taking >2 seconds
@pytest.mark.flaky            # Non-deterministic tests
@pytest.mark.database         # Tests requiring database
@pytest.mark.api              # Tests making API calls
@pytest.mark.selenium         # Browser automation tests
@pytest.mark.scrapy           # Web scraping tests
@pytest.mark.llm              # LLM API tests
```

### Intelligent Coverage Thresholds
- **Tier 1**: 85% (production must be thoroughly tested)
- **Tier 2**: 80% (good balance of quality and velocity)
- **Tier 3**: 75% (pragmatic for maintenance work)

### Parallel Test Execution
- **Tier 1**: Limited to 4 workers (safe)
- **Tier 2**: Standard 8 workers (balanced)
- **Tier 3**: Maximum 12 workers (fast)

Requires: `pip install pytest-xdist`

### Async Test Support
```python
# Automatically runs with asyncio_mode = auto
async def test_async_function():
    result = await get_data()
    assert result is not None
```

Requires: `pip install pytest-asyncio`

### Coverage Reporting
```bash
# Terminal report with missing lines
pytest --cov=src --cov-report=term-missing

# HTML report for visual inspection
pytest --cov=src --cov-report=html
open htmlcov/index.html

# XML for CI/CD integration (Codecov, etc.)
pytest --cov=src --cov-report=xml
```

## 📚 Documentation Guide

### For Quick Reference
Start with: **PYTEST_QUICK_REFERENCE.md**
- One-page cheat sheet
- Common commands
- Quick examples
- Print and keep visible

### For Complete Information
See: **PYTEST_DEPLOYMENT_GUIDE.md**
- Detailed setup instructions
- Customization guide
- CI/CD integration examples
- Troubleshooting guide
- Best practices

### For Quick Start in Repository
See: This README
- Quick 60-second setup
- Tier mapping
- Key features overview
- Common commands

## ⚙️ Installation

### Install Required Packages

```bash
# Core testing framework
pip install pytest>=7.4.0

# Code coverage reporting
pip install pytest-cov>=4.1.0

# Async test support
pip install pytest-asyncio>=0.21.0

# Mocking utilities
pip install pytest-mock>=3.11.1

# Parallel execution (optional)
pip install pytest-xdist>=3.3.0

# Test timeouts
pip install pytest-timeout>=2.1.0

# Or install all at once:
pip install pytest pytest-cov pytest-asyncio pytest-mock pytest-xdist pytest-timeout
```

### Copy Configuration

```bash
# For your specific tier
cp pytest.tier2.ini pytest.ini

# Verify configuration
pytest --co
```

## 🎓 Common Commands

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific file
pytest tests/test_module.py

# Run by marker (fast unit tests)
pytest -m unit

# Run excluding slow tests
pytest -m "not slow"
```

### Coverage Checking

```bash
# Generate coverage report
pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Enforce coverage threshold
pytest --cov --cov-fail-under=80
```

### Parallel Execution

```bash
# Use all CPU cores
pytest -n auto

# Tier 1: 4 workers
pytest -n 4

# Tier 2: 8 workers
pytest -n 8

# Tier 3: 12 workers
pytest -n 12
```

### Debugging

```bash
# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Drop to debugger on failure
pytest --pdb

# Show slowest 10 tests
pytest --durations=10
```

## 🔧 Customization Examples

### Add Custom Markers

Edit your `pytest.ini`:

```ini
[pytest]
markers =
    # Standard markers
    unit: Unit tests

    # Custom markers
    economics: Economic analysis tests
    marine: Marine engineering tests
```

### Override Coverage Threshold

```ini
[pytest]
# Override for your repository
fail_under = 78
```

### Change Timeout

```ini
[pytest]
# Increase for slow repository
timeout = 600
```

### Enable/Disable Parallel Execution

```ini
[pytest]
# Use more workers
addopts = -n 12

# Or disable (run sequentially)
# Remove -n from addopts
```

## 📊 Deployment at Scale

### Automated Deployment Script

For deploying to all 25 repositories at once:

```bash
cd /mnt/github/workspace-hub

# Review script
cat scripts/deploy_pytest_config.sh

# Execute deployment
bash scripts/deploy_pytest_config.sh
```

**Script features:**
- Automatically identifies repository tier
- Copies appropriate template
- Backs up existing pytest.ini
- Optionally commits changes
- Logs all operations

## 🎯 Success Metrics

After deploying pytest.ini, you should see:

✅ **Consistent Test Discovery**
- All repositories use same patterns
- Tests in `tests/` directory found automatically
- File naming: `test_*.py` or `*_test.py`

✅ **Coverage Enforcement**
- CI/CD fails if coverage below threshold
- HTML reports show untested code paths
- Team focuses on testing critical features

✅ **Faster Test Execution**
- Parallel execution with pytest-xdist
- Selective test runs by marker
- Better feedback loop during development

✅ **Better Organization**
- Tests categorized with markers
- Easy to run specific test types
- Clear dependencies documented

✅ **Improved Maintainability**
- Consistent configuration across repos
- Easy onboarding for new developers
- Clear standards and expectations

## 🐛 Troubleshooting

### Unknown Marker Error

**Problem:** `ERROR: Unknown marker: 'my_marker'`

**Solution:** Add marker to `[pytest]` section:
```ini
markers =
    my_marker: My custom marker
```

### Tests Not Discovered

**Problem:** No tests found in `tests/` directory

**Solution:** Verify:
- Directory is named `tests/` (not `test/` or `testing/`)
- Test files start with `test_` or end with `_test.py`
- Files are Python files (`.py` extension)

### Coverage Threshold Not Enforced

**Problem:** Tests pass even with low coverage

**Solution:** Check addopts section:
```ini
addopts = --cov=src --cov-fail-under=80
```

### Parallel Tests Fail

**Problem:** Tests pass individually but fail in parallel

**Solution:** Tests likely have shared state. Use fixtures:
```python
@pytest.fixture
def clean_database():
    db = Database()
    yield db
    db.cleanup()

def test_something(clean_database):
    # Use clean_database fixture
    pass
```

For more troubleshooting: See **PYTEST_DEPLOYMENT_GUIDE.md**

## 📞 Support

### Quick Reference
- **Cheat Sheet**: PYTEST_QUICK_REFERENCE.md
- **Full Guide**: PYTEST_DEPLOYMENT_GUIDE.md

### Online Resources
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [pytest-xdist](https://pytest-xdist.readthedocs.io/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

### Testing Standards
- See: @docs/modules/standards/TESTING_FRAMEWORK_STANDARDS.md

## 📄 Version Information

| Component | Version | Released |
|-----------|---------|----------|
| pytest.ini | 1.0.0 | 2025-01-13 |
| Deployment Guide | 1.0.0 | 2025-01-13 |
| Quick Reference | 1.0.0 | 2025-01-13 |
| Automation Script | 1.0.0 | 2025-01-13 |

## 🚀 Next Steps

1. **Choose your tier**: Identify if your repo is Tier 1, 2, or 3
2. **Copy template**: `cp pytest.tier2.ini pytest.ini`
3. **Install packages**: `pip install pytest pytest-cov pytest-xdist`
4. **Verify setup**: `pytest --co`
5. **Add markers**: Mark each test with `@pytest.mark.unit` or similar
6. **Run tests**: `pytest tests/ -v`
7. **Check coverage**: `pytest --cov --cov-report=html`
8. **Commit**: `git add pytest.ini && git commit -m "Add pytest.ini"`

---

**Ready to standardize testing across workspace-hub? Start with Quick Start above!**

For detailed information, see PYTEST_DEPLOYMENT_GUIDE.md
