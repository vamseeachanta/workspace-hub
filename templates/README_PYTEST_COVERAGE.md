# Pytest & Coverage Configuration - Complete Reference

> Everything you need to add testing to any workspace-hub repository

## 📁 Files in This Package

### 1. **pytest-coverage-config.toml** (MAIN REFERENCE)
Complete, fully-commented pytest and coverage configuration with all options explained.

**Use this when:**
- You need complete documentation of every setting
- You want to understand what each option does
- You're setting up a complex testing framework

**Contents:**
- Test dependencies (core, standard, advanced, dev)
- Pytest core configuration
- Coverage run/report/html/xml/json settings
- Advanced features (benchmark, hypothesis, xdist)

### 2. **PYTEST_CONFIG_SNIPPETS.md** (QUICK START)
Copy-paste ready configurations for 7 different repository types.

**Use this when:**
- You want the fastest setup possible
- You want to pick a config and go
- You already know what you need

**Contents:**
- 1. Minimal Config (starting out)
- 2. Standard Config (most projects)
- 3. Advanced Config (complex projects)
- 4. Data Science Config (notebooks)
- 5. API/FastAPI Config
- 6. Django Config
- 7. Frontend Config
- Tier-based configurations (Tier 1, 2, 3)

### 3. **PYTEST_INTEGRATION_GUIDE.md** (DETAILED WALKTHROUGH)
Step-by-step integration guide with examples, testing patterns, and troubleshooting.

**Use this when:**
- You need help integrating pytest into CI/CD
- You want testing examples and patterns
- You're troubleshooting test issues
- You need to set up GitHub Actions

**Contents:**
- Quick start (5 minutes)
- Test organization structure
- Writing tests (examples)
- CI/CD integration (GitHub Actions)
- Common commands reference
- Troubleshooting guide
- Advanced usage patterns

### 4. **README_PYTEST_COVERAGE.md** (THIS FILE)
High-level overview and navigation guide.

---

## 🚀 Quick Start (Choose Your Path)

### Path A: "I want the fastest setup"
1. Open **PYTEST_CONFIG_SNIPPETS.md**
2. Pick a config that matches your project type (1-7)
3. Copy it into your `pyproject.toml`
4. Adjust `fail_under` based on your tier (80 or 85)
5. Run: `uv pip install -e ".[test]"` then `pytest --cov`

### Path B: "I want to understand everything"
1. Open **pytest-coverage-config.toml**
2. Read comments for each section
3. Copy sections into your `pyproject.toml`
4. Refer to **PYTEST_INTEGRATION_GUIDE.md** for examples

### Path C: "I need help with CI/CD or troubleshooting"
1. Open **PYTEST_INTEGRATION_GUIDE.md**
2. Find your use case or problem
3. Follow the provided solution
4. Reference templates in PYTEST_CONFIG_SNIPPETS.md

---

## 📊 Configuration Overview

```
[project.optional-dependencies]
├── test-core           # Minimal: pytest, pytest-cov
├── test-standard       # Most common: + asyncio, mock
├── test-advanced       # Complex: + benchmark, hypothesis, xdist
└── dev                 # Tools: black, ruff, mypy, isort

[tool.pytest.ini_options]
├── testpaths          # Where tests live
├── python_files       # Test file naming patterns
├── addopts            # Default command-line options
├── markers            # Test categorization
└── filterwarnings     # Warning handling

[tool.coverage.run]
├── source             # Code to measure
├── omit               # Paths to skip
├── branch             # Branch coverage?
└── parallel           # Parallel test runs?

[tool.coverage.report]
├── exclude_lines      # Lines to ignore
├── show_missing       # Show which lines not covered?
├── precision          # Percentage decimals
└── fail_under         # Minimum threshold (80-85)

[tool.coverage.html]
└── directory          # Where to save reports

[tool.coverage.xml]
└── output             # For CI/CD integration
```

---

## 🎯 Repository Tier Configuration

Your repository tier determines the coverage threshold:

### Tier 1: Work/Production Repositories
**Examples**: digitalmodel, energy, frontierdeepwater, aceengineercode

```toml
[tool.coverage.report]
fail_under = 85
```

**Requirements:**
- All new code must have tests
- Coverage must not decrease
- Integration tests required

### Tier 2: Active Development Repositories
**Examples**: aceengineer-website, hobbies, sd-work

```toml
[tool.coverage.report]
fail_under = 80
```

**Requirements:**
- New features should have tests
- Coverage should not decrease
- Can defer comprehensive testing initially

### Tier 3: Maintenance Repositories
**Examples**: doris, saipem, OGManufacturing

```toml
[tool.coverage.report]
fail_under = 80
```

**Requirements:**
- Bug fixes should have tests
- No regression in coverage
- Testing can be less comprehensive

---

## 📚 Test Dependencies Overview

### test-core (Minimal)
- `pytest` - Test framework
- `pytest-cov` - Coverage integration

**Use for**: Simple scripts, utilities

```bash
uv pip install -e ".[test-core]"
```

### test-standard (Recommended)
- Everything in test-core
- `pytest-asyncio` - Async/await testing
- `pytest-mock` - Mocking utilities

**Use for**: Most Python projects

```bash
uv pip install -e ".[test-standard]"
```

### test-advanced (Full-Featured)
- Everything in test-standard
- `pytest-benchmark` - Performance benchmarking
- `hypothesis` - Property-based testing
- `pytest-xdist` - Parallel execution

**Use for**: Complex projects, production code

```bash
uv pip install -e ".[test-advanced]"
```

### dev (Development Tools)
- `black` - Code formatting
- `ruff` - Fast linting
- `mypy` - Type checking
- `isort` - Import sorting
- `pre-commit` - Git hooks

**Use with test-advanced** for full development setup

```bash
uv pip install -e ".[test-standard,dev]"
```

---

## 🧪 Test Organization

```
repository/
├── src/                         # Source code
│   └── modules/
│       └── my_module.py
│
├── tests/                       # Test files (REQUIRED)
│   ├── __init__.py
│   ├── conftest.py             # Fixtures & config
│   ├── unit/                   # Fast, isolated tests
│   │   └── test_my_module.py
│   ├── integration/            # Multiple components
│   │   └── test_workflow.py
│   ├── performance/            # Benchmarks
│   │   └── test_performance.py
│   └── fixtures/               # Test data
│       └── sample_data.json
│
└── pyproject.toml              # Config (modified)
```

---

## ✅ Testing Workflow

### 1. Install Dependencies
```bash
uv pip install -e ".[test-standard]"
```

### 2. Write Tests
```python
# tests/unit/test_module.py
def test_example():
    assert 1 + 1 == 2
```

### 3. Run Tests
```bash
pytest
```

### 4. Check Coverage
```bash
pytest --cov
```

### 5. Generate Report
```bash
pytest --cov --cov-report=html
open htmlcov/index.html
```

---

## 🔧 Common Test Commands

| Command | Purpose |
|---------|---------|
| `pytest` | Run all tests |
| `pytest -v` | Verbose output |
| `pytest tests/unit/` | Run specific directory |
| `pytest -m unit` | Run tests with marker |
| `pytest -k test_name` | Run matching tests |
| `pytest --cov` | With coverage |
| `pytest --cov --cov-report=html` | HTML report |
| `pytest -m "not slow"` | Skip slow tests |
| `pytest -n auto` | Parallel (requires pytest-xdist) |
| `pytest --pdb` | Drop to debugger on failure |
| `pytest --lf` | Run last failed tests |

---

## 📋 Integration Checklist

- [ ] Choose config type (minimal, standard, advanced)
- [ ] Copy config from PYTEST_CONFIG_SNIPPETS.md
- [ ] Paste into `pyproject.toml`
- [ ] Set `fail_under = 80` or `85` based on tier
- [ ] Create `tests/` directory
- [ ] Create `tests/conftest.py` (optional, for fixtures)
- [ ] Run `uv pip install -e ".[test-standard]"`
- [ ] Run `pytest` to verify setup
- [ ] Write tests for new code
- [ ] Add to CI/CD pipeline (see guide)
- [ ] Set up coverage reporting (Codecov, etc.)

---

## 🎓 Learning Resources

### Files in This Package
1. **pytest-coverage-config.toml** - Complete reference
2. **PYTEST_CONFIG_SNIPPETS.md** - Quick configs
3. **PYTEST_INTEGRATION_GUIDE.md** - Detailed guide

### External Resources
- **pytest docs**: https://docs.pytest.org/
- **coverage.py docs**: https://coverage.readthedocs.io/
- **pytest-cov**: https://pytest-cov.readthedocs.io/
- **hypothesis**: https://hypothesis.readthedocs.io/
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/

### Workspace Standards
- **Testing Standards**: @docs/modules/standards/TESTING_FRAMEWORK_STANDARDS.md
- **File Organization**: @docs/modules/standards/FILE_ORGANIZATION_STANDARDS.md
- **Development Workflow**: @docs/modules/workflow/DEVELOPMENT_WORKFLOW.md

---

## 🚨 Critical Settings

### fail_under (Coverage Threshold)
**Tier 1 (Production)**: `85` (higher standard)
**Tier 2-3 (Active/Maintenance)**: `80`

```toml
[tool.coverage.report]
fail_under = 80  # Change to 85 for Tier 1
```

### source (What to Measure)
```toml
[tool.coverage.run]
source = ["src"]  # Adjust to match your directory
```

### testpaths (Where to Find Tests)
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]  # Change if using "test" or other name
```

---

## 🎯 Quick Decision Tree

```
Do I need to add testing?
├─ YES → Go to QUICK START (above)
└─ NO → Done!

How complex is my project?
├─ Simple script/utility → Use MINIMAL config
├─ Standard Python project → Use STANDARD config
├─ Complex/production code → Use ADVANCED config
├─ Data science/notebooks → Use DATA SCIENCE config
├─ FastAPI/REST API → Use API config
├─ Django project → Use DJANGO config
└─ Web/frontend → Use FRONTEND config

Do I know my repository tier?
├─ Tier 1 (production) → fail_under = 85
├─ Tier 2 (active dev) → fail_under = 80
└─ Tier 3 (maintenance) → fail_under = 80

Do I need CI/CD integration?
├─ YES → See PYTEST_INTEGRATION_GUIDE.md
└─ NO → Just use locally

Do I need help troubleshooting?
├─ YES → See PYTEST_INTEGRATION_GUIDE.md (troubleshooting section)
└─ NO → You're good to go!
```

---

## 📞 Support

### If you get stuck:

1. **Check PYTEST_INTEGRATION_GUIDE.md** - Likely has your issue
2. **Look at PYTEST_CONFIG_SNIPPETS.md** - Pick the closest config
3. **Review pytest-coverage-config.toml** - Understand individual settings
4. **Check workspace standards** - @docs/modules/standards/TESTING_FRAMEWORK_STANDARDS.md

### Common Issues

| Issue | Solution |
|-------|----------|
| "No tests collected" | Check file naming (test_*.py or *_test.py) |
| "ModuleNotFoundError: No module named 'src'" | Run `uv pip install -e .` |
| Coverage threshold fails | Increase test coverage or lower `fail_under` |
| Tests hang/timeout | Check for infinite loops, mock network calls |
| Async tests fail | Install `pytest-asyncio` |

---

## 🏁 Next Steps

1. **Choose your configuration** from PYTEST_CONFIG_SNIPPETS.md
2. **Copy it into pyproject.toml**
3. **Install dependencies**: `uv pip install -e ".[test-standard]"`
4. **Create tests/ directory**: `mkdir tests`
5. **Write a simple test**: `tests/test_basic.py`
6. **Run tests**: `pytest --cov`
7. **Generate report**: `pytest --cov --cov-report=html`
8. **Integrate to CI/CD**: Follow PYTEST_INTEGRATION_GUIDE.md

---

## 📦 Files Summary

| File | Size | Purpose | When to Use |
|------|------|---------|------------|
| pytest-coverage-config.toml | Full | Complete reference with comments | Understanding all options |
| PYTEST_CONFIG_SNIPPETS.md | Quick | 7 ready-to-use configs | Fastest setup |
| PYTEST_INTEGRATION_GUIDE.md | Detailed | Step-by-step guide + examples | Learning & troubleshooting |
| README_PYTEST_COVERAGE.md | Overview | This file - navigation | Getting started |

---

**Version**: 1.0.0
**Updated**: 2025-01-13
**Part of**: workspace-hub testing standards and templates

---

## 🎉 You're Ready!

Pick a file and get started:
- **Just want to copy-paste?** → PYTEST_CONFIG_SNIPPETS.md
- **Want to understand everything?** → pytest-coverage-config.toml
- **Need help with setup?** → PYTEST_INTEGRATION_GUIDE.md
- **Not sure where to start?** → Read this file again (you're here!)

Happy testing! 🚀
