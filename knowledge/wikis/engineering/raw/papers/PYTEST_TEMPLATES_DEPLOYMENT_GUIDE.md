# Pytest & Coverage Templates - Deployment Guide

> **Status:** Complete and ready for distribution
> **Location:** `/mnt/github/workspace-hub/templates/`
> **Commit:** 424746d - Create comprehensive pytest & coverage configuration package
> **Total Files:** 6 files, 2,533 lines
> **Target:** All 26 workspace-hub repositories

## Package Overview

A complete, production-ready pytest and coverage configuration package designed for immediate integration into any workspace-hub repository.

### Files Included

| File | Lines | Purpose | Use When |
|------|-------|---------|----------|
| **README_PYTEST_COVERAGE.md** | 445 | Navigation guide | You're not sure where to start |
| **PYTEST_CONFIG_SNIPPETS.md** | 596 | 7 ready-to-paste configs | You want fastest setup |
| **pytest-coverage-config.toml** | 346 | Complete reference | You need to understand all options |
| **PYTEST_INTEGRATION_GUIDE.md** | 483 | Step-by-step guide | You need detailed instructions |
| **PYTEST_QUICK_REFERENCE.txt** | 254 | Cheat sheet | You need quick lookups while coding |
| **PYTEST_TEMPLATES_SUMMARY.md** | 409 | Package overview | You're exploring available resources |

**Total:** 2,533 lines of documentation and configuration

---

## Quick Start (5 Minutes)

### For Any Repository

1. **Read Navigation Guide**
   ```bash
   cat templates/README_PYTEST_COVERAGE.md
   ```

2. **Choose Your Configuration Type**
   - Open `templates/PYTEST_CONFIG_SNIPPETS.md`
   - Find your repository type (Minimal, Standard, Advanced, Data Science, API, Django, or Web)
   - Note your tier (Tier 1 = 85% coverage, Tier 2-3 = 80%)

3. **Copy Configuration to pyproject.toml**
   ```bash
   # Copy from PYTEST_CONFIG_SNIPPETS.md
   # Paste into your repository's pyproject.toml
   ```

4. **Install Dependencies**
   ```bash
   uv pip install -e ".[test-standard]"
   # Or use test-core, test-advanced, etc. based on choice
   ```

5. **Run Tests**
   ```bash
   pytest --cov
   ```

---

## Integration Paths

### Path 1: Fastest Setup (5 Minutes)

```
README_PYTEST_COVERAGE.md (1 min)
    ↓
PYTEST_CONFIG_SNIPPETS.md (1 min - pick your config)
    ↓
Copy to pyproject.toml (1 min)
    ↓
Install & run (2 min)
```

**Result:** Testing framework operational immediately

### Path 2: Complete Understanding (30 Minutes)

```
README_PYTEST_COVERAGE.md (5 min - overview)
    ↓
pytest-coverage-config.toml (15 min - read comments)
    ↓
PYTEST_CONFIG_SNIPPETS.md (5 min - review options)
    ↓
PYTEST_INTEGRATION_GUIDE.md (5 min - verify understanding)
```

**Result:** Deep understanding of all options and patterns

### Path 3: Learning & Reference (Ongoing)

```
PYTEST_QUICK_REFERENCE.txt (print this)
    ↓
Keep on desk while coding
    ↓
Reference as needed for commands, markers, patterns
    ↓
PYTEST_INTEGRATION_GUIDE.md for detailed examples
```

**Result:** Quick access to information while developing

### Path 4: Troubleshooting (As Needed)

```
PYTEST_INTEGRATION_GUIDE.md → Troubleshooting section
    ↓
Find your issue
    ↓
Follow solution steps
```

**Result:** Issue resolution with examples

---

## Deployment to All Repositories

### One-Time Setup

Create a deployment script to apply these templates to all repositories:

```bash
#!/bin/bash
# scripts/deployment/deploy_pytest_templates.sh

TEMPLATES_DIR="$(pwd)/templates"
REPOS_DIR="$(pwd)"

# List of target repositories
REPOSITORIES=(
    "digitalmodel"
    "energy"
    "frontierdeepwater"
    "aceengineer-code"
    "worldenergydata"
    # ... add all 26 repositories
)

for repo in "${REPOSITORIES[@]}"; do
    if [ -d "$REPOS_DIR/$repo" ]; then
        echo "Deploying pytest templates to $repo..."

        # Copy README as reference
        cp "$TEMPLATES_DIR/README_PYTEST_COVERAGE.md" "$REPOS_DIR/$repo/docs/"

        # Copy config if pyproject.toml exists
        if [ -f "$REPOS_DIR/$repo/pyproject.toml" ]; then
            echo "  ✓ $repo has pyproject.toml"
            echo "  → Copy configuration from PYTEST_CONFIG_SNIPPETS.md"
        fi
    fi
done

echo "✓ Deployment complete"
echo "Next steps: Integrate configurations into each repository's pyproject.toml"
```

---

## Repository Type Selection

### Based on Project Type

| Type | Config | When |
|------|--------|------|
| Scripts/utilities | Minimal | Simple Python scripts |
| Standard projects | Standard | Most Python projects (default) |
| Complex systems | Advanced | Production code, benchmarks |
| Data science | Data Science | Notebooks, exploratory |
| REST APIs | API/FastAPI | FastAPI, REST endpoints |
| Web frameworks | Django | Django projects |
| Mixed | Web/Frontend | JS/TS frontend + Python backend |

### Based on Repository Tier

| Tier | fail_under | Repositories |
|------|-----------|--------------|
| **1 (Production)** | 85% | digitalmodel, energy, frontierdeepwater |
| **2 (Active Dev)** | 80% | aceengineer-website, hobbies, sd-work |
| **3 (Maintenance)** | 80% | doris, saipem, OGManufacturing |

---

## Standard Dependencies Configuration

### Minimal (Test-Only)
```toml
[project.optional-dependencies]
test = [
    "pytest>=7.4.0,<9.0.0",
    "pytest-cov>=4.1.0,<5.0.0",
]
```

### Standard (Recommended)
```toml
[project.optional-dependencies]
test = [
    "pytest>=7.4.0,<9.0.0",
    "pytest-cov>=4.1.0,<5.0.0",
    "pytest-asyncio>=0.21.0,<0.24.0",
    "pytest-mock>=3.11.0,<4.0.0",
]
```

### Advanced (Full Features)
```toml
[project.optional-dependencies]
test = [
    "pytest>=7.4.0,<9.0.0",
    "pytest-cov>=4.1.0,<5.0.0",
    "pytest-asyncio>=0.21.0,<0.24.0",
    "pytest-mock>=3.11.0,<4.0.0",
    "pytest-benchmark>=4.0.0,<5.0.0",
    "hypothesis>=6.92.0,<7.0.0",
    "pytest-xdist>=3.5.0,<4.0.0",
]
```

---

## Coverage Configuration Highlights

### Critical Settings

**Always Configure:**
```toml
[tool.coverage.report]
fail_under = 80  # Or 85 for Tier 1 production repos
```

**Test Location:**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]  # Adjust if using "test" or other name
```

**Source Code Location:**
```toml
[tool.coverage.run]
source = ["src"]  # Adjust if using "app", "lib", etc.
```

---

## Testing Markers

Available test markers for organization:

```python
@pytest.mark.unit              # Unit tests (fast, isolated)
@pytest.mark.integration       # Integration tests
@pytest.mark.slow              # Slow/long-running tests
@pytest.mark.asyncio           # Async/await tests
@pytest.mark.benchmark         # Performance benchmarks
@pytest.mark.property          # Property-based tests
@pytest.mark.external          # Tests needing external services
@pytest.mark.security          # Security-focused tests
```

Run specific markers:
```bash
pytest -m unit                 # Unit tests only
pytest -m "not slow"           # Skip slow tests
pytest -m "unit and not slow"  # Combination
```

---

## Common Installation Commands

```bash
# Minimal setup
uv pip install -e ".[test]"

# Standard setup (recommended)
uv pip install -e ".[test]"  # Uses test group from optional-dependencies

# With development tools
uv pip install -e ".[test,dev]"

# Advanced setup with benchmarking
uv pip install -e ".[test,dev]"  # Includes test-advanced
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
    - run: pip install uv
    - run: uv pip install -e ".[test]"
    - run: pytest --cov --cov-fail-under=80
```

See `PYTEST_INTEGRATION_GUIDE.md` for full CI/CD examples.

---

## Verification Checklist

Before deploying to production, verify:

- [ ] `pyproject.toml` has `[project.optional-dependencies]` section
- [ ] `[tool.pytest.ini_options]` configured with testpaths
- [ ] `[tool.coverage.run]` configured with correct source paths
- [ ] `[tool.coverage.report]` has `fail_under` set (80 or 85)
- [ ] `tests/` directory exists with `__init__.py`
- [ ] At least one test file exists (e.g., `tests/test_basic.py`)
- [ ] `pytest --cov` runs successfully
- [ ] Coverage meets threshold
- [ ] GitHub Actions workflow includes test step (if using CI/CD)

---

## Quick Reference

### Most Important Commands

```bash
# Run tests
pytest

# Run with coverage
pytest --cov

# View coverage HTML report
pytest --cov --cov-report=html
open htmlcov/index.html

# Run specific test type
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Run tests and fail if coverage below threshold
pytest --cov --cov-fail-under=80
```

### Most Important Files

| File | Use For |
|------|---------|
| `PYTEST_CONFIG_SNIPPETS.md` | Fastest setup (pick your config) |
| `PYTEST_QUICK_REFERENCE.txt` | Quick lookups while coding |
| `README_PYTEST_COVERAGE.md` | Navigation and overview |
| `PYTEST_INTEGRATION_GUIDE.md` | Detailed examples and troubleshooting |
| `pytest-coverage-config.toml` | Understanding all options |

---

## Support & Resources

### In This Package
- **Quick Start:** README_PYTEST_COVERAGE.md
- **Copy-Paste Configs:** PYTEST_CONFIG_SNIPPETS.md
- **Learning Guide:** PYTEST_INTEGRATION_GUIDE.md
- **Cheat Sheet:** PYTEST_QUICK_REFERENCE.txt (print this!)
- **Package Overview:** PYTEST_TEMPLATES_SUMMARY.md

### External Resources
- **Pytest Docs:** https://docs.pytest.org/
- **Coverage.py:** https://coverage.readthedocs.io/
- **Workspace Standards:** @docs/modules/standards/TESTING_FRAMEWORK_STANDARDS.md

---

## Next Steps

1. **For Individual Repository Setup:**
   - Read `README_PYTEST_COVERAGE.md`
   - Pick configuration from `PYTEST_CONFIG_SNIPPETS.md`
   - Copy to `pyproject.toml`
   - Install dependencies and run tests

2. **For Organization-Wide Deployment:**
   - Use deployment script above
   - Customize per repository tier and type
   - Verify with checklist
   - Track completion status

3. **For CI/CD Integration:**
   - See `PYTEST_INTEGRATION_GUIDE.md` CI/CD section
   - Update `.github/workflows/test.yml`
   - Configure coverage thresholds
   - Test locally first

---

## Document Locations

All templates are available in:

```
/mnt/github/workspace-hub/templates/
├── README_PYTEST_COVERAGE.md
├── PYTEST_CONFIG_SNIPPETS.md
├── PYTEST_INTEGRATION_GUIDE.md
├── PYTEST_QUICK_REFERENCE.txt
├── PYTEST_TEMPLATES_SUMMARY.md
└── pytest-coverage-config.toml
```

---

**Status:** ✅ Complete and ready for immediate deployment to all 26 workspace-hub repositories

**Last Updated:** 2025-01-13
**Commit:** 424746d
