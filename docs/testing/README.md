# Tiered Test Profiles

> Three test profiles matched to workflow context: commit, task, and session.

## Quick Reference

| Tier | Script | Target Time | When to Use |
|------|--------|-------------|-------------|
| **1** | `scripts/test/test-commit.sh` | ~5-10s | Before every commit |
| **2** | `scripts/test/test-task.sh <module>` | ~30-60s | During active development on a module |
| **3** | `scripts/test/test-session.sh` | Full suite | End of session or before pushing |

## Tier 1: Pre-Commit

Runs only tests matching files staged for commit. Skips slow, benchmark, and integration tests.

```bash
# Test staged files (default)
scripts/test/test-commit.sh

# Test modified but unstaged files
scripts/test/test-commit.sh --unstaged

# Test all changed files (staged + unstaged)
scripts/test/test-commit.sh --all

# Dry run (show what would execute)
DRY_RUN=1 scripts/test/test-commit.sh
```

**How it works:**
1. Detects changed `.py` files via `git diff` (across workspace-hub and submodules)
2. Groups files by repo (worldenergydata, digitalmodel, etc.)
3. Maps source files to test files using naming conventions
4. Runs matched tests with `-x` (fail-fast), no coverage, 30s timeout

## Tier 2: Per-Task

Runs all tests for a specific module with coverage reporting.

```bash
# Test a specific module
scripts/test/test-task.sh bsee
scripts/test/test-task.sh dynacard
scripts/test/test-task.sh hull_library

# Test multiple modules
scripts/test/test-task.sh bsee hse marine_safety

# Auto-detect modules from git changes
scripts/test/test-task.sh --auto

# Read target repos from a work item
scripts/test/test-task.sh --wrk WRK-119
```

**Available modules** are defined in `scripts/test/config/module-map.yml`.

## Tier 3: Full Session

Runs the complete test suite across all repos (or a subset).

```bash
# All repos
scripts/test/test-session.sh

# Single repo
scripts/test/test-session.sh worldenergydata

# Multiple repos
scripts/test/test-session.sh worldenergydata digitalmodel

# With markdown report
scripts/test/test-session.sh --report
```

## Directory Structure

```
scripts/test/
├── test-commit.sh          # Tier 1
├── test-task.sh            # Tier 2
├── test-session.sh         # Tier 3
├── lib/
│   ├── detect-repo.sh      # File path → repo name
│   ├── map-tests.sh        # Source file → test file(s)
│   ├── invoke-pytest.sh    # Standardized pytest invocation
│   └── report.sh           # Result formatting
└── config/
    ├── worldenergydata.conf # Repo-specific pytest settings
    ├── digitalmodel.conf    # Repo-specific pytest settings
    ├── workspace-hub.conf   # Repo-specific pytest settings
    └── module-map.yml       # Module name → test directory mapping
```

## Repo-Specific Notes

### worldenergydata
- **Venv**: Broken (miniconda3 missing). Uses system `python3` (3.12.3).
- **PYTHONPATH**: `src:../assetutilities/src` (set automatically by invoke-pytest.sh)
- **Plugins**: `pytest-timeout` not installed in system python; Tier 1/2 override addopts
- **384 test files**, 18 markers defined

### digitalmodel
- **Venv**: Healthy, managed by uv 0.10.0 (Python 3.11.14)
- **PYTHONPATH**: Configured in root conftest.py
- **Plugins**: All installed (pytest-xdist, pytest-cov, pytest-timeout, etc.)
- **346 test files**, 27 markers defined

### workspace-hub
- **5 Python test files** (no dedicated venv)
- **No pytest.ini** at root level

## Source-to-Test Mapping

`map-tests.sh` resolves source files to test files using these rules (in order):

1. `src/<pkg>/<module>/foo.py` → `tests/modules/<module>/test_foo.py`
2. `src/<pkg>/<module>/foo.py` → `tests/<module>/test_foo.py`
3. `src/<pkg>/<module>/foo.py` → `tests/unit/<module>/test_foo.py`
4. `src/<pkg>/<module>/foo.py` → `tests/unit/test_foo.py`
5. Fallback: entire module test directory

## Adding New Modules

To add a new module to the test system:

1. Add an entry to `scripts/test/config/module-map.yml`:
   ```yaml
   new_module:
     repo: worldenergydata
     src: src/worldenergydata/new_module
     tests: tests/modules/new_module
   ```

2. Verify: `DRY_RUN=1 scripts/test/test-task.sh new_module`

## Troubleshooting

**"Unknown config option: timeout"** — System python3 lacks pytest-timeout. The tiered scripts override addopts to avoid this. For Tier 3, use a repo with a healthy venv (digitalmodel).

**"No matching test files found"** — The source file doesn't follow the naming convention. Add an explicit entry to module-map.yml or create a test file following the `test_<name>.py` convention.

**Slow conftest.py initialization** — The `TestPerformanceTracker` in worldenergydata conftest reads a SQLite DB on startup (~15s). This is a known overhead. Tier 1 still works but adds latency.
