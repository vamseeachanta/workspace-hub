# Pytest & Coverage Templates - Complete Package

**Status:** ✅ Complete and ready for distribution
**Date:** 2025-01-13
**Total Content:** 2,533 lines across 6 files
**Target:** All 26 workspace-hub repositories

---

## Quick Navigation

### 🚀 **I want to start NOW** (5 minutes)
→ Read: `README_PYTEST_COVERAGE.md` (overview)
→ Copy from: `PYTEST_CONFIG_SNIPPETS.md` (your repository type)
→ Paste into: `pyproject.toml`
→ Done! 🎉

### 📚 **I want to understand EVERYTHING** (30 minutes)
1. `README_PYTEST_COVERAGE.md` - Overview
2. `pytest-coverage-config.toml` - Complete reference
3. `PYTEST_CONFIG_SNIPPETS.md` - See all options
4. `PYTEST_INTEGRATION_GUIDE.md` - Examples & patterns

### 🔍 **I want QUICK REFERENCE while coding**
→ Print: `PYTEST_QUICK_REFERENCE.txt`
→ Keep on desk
→ Look up commands and patterns

### 🛠️ **I need to INTEGRATE into CI/CD**
→ Read: `PYTEST_INTEGRATION_GUIDE.md` → CI/CD section
→ Copy: GitHub Actions example
→ Customize: For your workflow

### 🧩 **I'm not sure WHAT I NEED**
→ Read: `PYTEST_TEMPLATES_SUMMARY.md`
→ Answers: Which file for my situation?

---

## File Guide

| File | Lines | Purpose | Best For |
|------|-------|---------|----------|
| **README_PYTEST_COVERAGE.md** | 445 | High-level overview & navigation | First-time users |
| **PYTEST_CONFIG_SNIPPETS.md** | 596 | 7 copy-paste ready configurations | Fastest setup |
| **PYTEST_INTEGRATION_GUIDE.md** | 483 | Step-by-step with examples | Learning & troubleshooting |
| **PYTEST_QUICK_REFERENCE.txt** | 254 | Cheat sheet (print this!) | Quick lookups |
| **PYTEST_TEMPLATES_SUMMARY.md** | 409 | Package overview & decision tree | Understanding what's available |
| **pytest-coverage-config.toml** | 346 | Complete reference with comments | Understanding all options |

---

## What's Included

### ✅ Test Dependencies
- `test-core`: Minimal (pytest, pytest-cov)
- `test-standard`: Recommended (+ asyncio, mock)
- `test-advanced`: Full-featured (+ benchmark, hypothesis, xdist)
- `dev`: Development tools (black, ruff, mypy, isort, pre-commit)

### ✅ Pytest Configuration
- `[tool.pytest.ini_options]` with testpaths, markers, addopts
- Test discovery patterns (test_*.py, *_test.py)
- Built-in markers: unit, integration, slow, asyncio, benchmark, property, external, security

### ✅ Coverage Configuration
- `[tool.coverage.run]` with source, omit, branch, parallel
- `[tool.coverage.report]` with fail_under, exclude_lines, precision
- Multiple report formats: terminal, HTML, XML, JSON
- Tier-based thresholds: 85% (Tier 1) or 80% (Tier 2-3)

### ✅ 7 Ready-to-Use Configurations
1. Minimal - Starting out
2. Standard - Most projects (recommended)
3. Advanced - Complex systems
4. Data Science - Notebooks
5. API/FastAPI - REST APIs
6. Django - Web frameworks
7. Web/Frontend - JS/TS with Python backend

### ✅ GitHub Actions Integration
- Complete CI/CD workflow example
- Coverage threshold enforcement
- Codecov integration

---

## Setup Steps (Quick)

### For Any Repository

```bash
# 1. Choose your configuration
# Read PYTEST_CONFIG_SNIPPETS.md and pick your type

# 2. Copy to pyproject.toml
# Paste the configuration section into your project

# 3. Install dependencies
uv pip install -e ".[test-standard]"

# 4. Run tests
pytest --cov

# 5. Generate report
pytest --cov --cov-report=html
open htmlcov/index.html
```

---

## Key Commands

```bash
# Run all tests
pytest

# With coverage
pytest --cov

# Specific test type
pytest -m unit              # Unit tests only
pytest -m "not slow"        # Skip slow tests

# HTML coverage report
pytest --cov --cov-report=html

# View report
open htmlcov/index.html (macOS)
start htmlcov/index.html (Windows)
```

---

## Critical Settings to Customize

### 1. Coverage Threshold (Most Important!)
```toml
[tool.coverage.report]
fail_under = 80  # Use 85 for Tier 1 production repos
```

### 2. Test Directory Location
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]  # Change to "test" if needed
```

### 3. Source Code Location
```toml
[tool.coverage.run]
source = ["src"]  # Change to "app", "lib", etc. if different
```

---

## Repository Tier Selection

| Tier | Coverage | Examples |
|------|----------|----------|
| **Tier 1** (Production) | 85% | digitalmodel, energy, frontierdeepwater |
| **Tier 2** (Active Dev) | 80% | aceengineer-website, hobbies, sd-work |
| **Tier 3** (Maintenance) | 80% | doris, saipem, OGManufacturing |

---

## Deployment Information

**Git Commit:** 424746d - Create comprehensive pytest & coverage configuration package

**Files Location:**
```
/mnt/github/workspace-hub/templates/
├── INDEX.md (this file)
├── README_PYTEST_COVERAGE.md
├── PYTEST_CONFIG_SNIPPETS.md
├── PYTEST_INTEGRATION_GUIDE.md
├── PYTEST_QUICK_REFERENCE.txt
├── PYTEST_TEMPLATES_SUMMARY.md
└── pytest-coverage-config.toml
```

**Deployment Guide:**
See: `/mnt/github/workspace-hub/docs/PYTEST_TEMPLATES_DEPLOYMENT_GUIDE.md`

---

## Support & Help

### Questions?

| Question | File |
|----------|------|
| Where do I start? | `README_PYTEST_COVERAGE.md` |
| How do I set up fastest? | `PYTEST_CONFIG_SNIPPETS.md` |
| What commands do I need? | `PYTEST_QUICK_REFERENCE.txt` |
| Can you explain everything? | `pytest-coverage-config.toml` |
| I need detailed examples | `PYTEST_INTEGRATION_GUIDE.md` |
| What's in this package? | `PYTEST_TEMPLATES_SUMMARY.md` |

### Common Issues?

See: `PYTEST_INTEGRATION_GUIDE.md` → Troubleshooting section

---

## Next Steps

1. ✅ **For Setup:** Follow "Quick Setup Steps" above
2. ✅ **For Learning:** Read files in order shown under "Best For"
3. ✅ **For Reference:** Print `PYTEST_QUICK_REFERENCE.txt`
4. ✅ **For Deployment:** See `PYTEST_TEMPLATES_DEPLOYMENT_GUIDE.md`

---

**Ready to get testing!** 🚀

Choose your starting point from the Quick Navigation section above.
