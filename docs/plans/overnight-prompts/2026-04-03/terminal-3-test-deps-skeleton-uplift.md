# Terminal 3 — Test Dependencies Fix + SKELETON Package Uplift (Codex Seat 2)

We are in /mnt/local-analysis/workspace-hub. Execute these 4 tasks in order.
Use `uv run` for all Python — never bare `python3` or `pip`.
Commit to `main` and push after each task. Do not branch.
TDD: write tests before implementation; mock external dependencies (no network, no licenses, no mounts).
Run `git pull origin main` before every push.
Do NOT ask the user any questions. Make reasonable decisions autonomously.

IMPORTANT: Do NOT write to any of the following paths — they are owned by other terminals:
- digitalmodel/src/digitalmodel/orcawave/, digitalmodel/tests/orcawave/ (Terminal 1)
- digitalmodel/tests/parametric_hull/, digitalmodel/tests/orcaflex/, digitalmodel/tests/hydrodynamics/ (Terminal 2)
- scripts/document-intelligence/, data/document-index/ (Terminal 4)
- digitalmodel/src/digitalmodel/{web,infrastructure,marine_ops,solvers,hydrodynamics,specialized,signal_processing}/ (Terminal 5 docstrings — except reservoir which T3 refactors)
- config/cron/, scripts/cron/ (Terminal 5)

Only write to:
- digitalmodel/pyproject.toml (ONLY to add test dependencies — do NOT change anything else)
- digitalmodel/tests/web/
- digitalmodel/tests/field_development/
- digitalmodel/tests/geotechnical/
- digitalmodel/tests/nde/
- digitalmodel/tests/reservoir/
- digitalmodel/src/digitalmodel/reservoir/stratigraphic.py (refactor only)

---

## TASK 1: Fix Broken Test Dependencies (GH issue #1647)

### Context
- Several test suites fail because `pint`, `plotly`, and `deepdiff` are not in the dev dependencies
- These are needed by tests but not declared in pyproject.toml

### Steps
1. Check current dev dependencies: read `digitalmodel/pyproject.toml` and look for `[project.optional-dependencies]` or `[tool.uv]` sections
2. Verify which packages are missing:
   ```
   uv run python -c "import pint" 2>&1
   uv run python -c "import plotly" 2>&1
   uv run python -c "import deepdiff" 2>&1
   ```
3. Add missing packages to the dev/test dependency group in `digitalmodel/pyproject.toml`
4. Install: `cd digitalmodel && uv sync --dev` (or equivalent)
5. Verify imports work after install
6. Run a quick existing test to confirm nothing broke: `uv run pytest digitalmodel/tests/ -x --timeout=60 -q 2>&1 | tail -20`

### Commit message
```
fix(deps): add pint, plotly, deepdiff to dev dependencies (#1647)
```

---

## TASK 2: Test Coverage — Web Package (GH issue #1584)

### Context
- `digitalmodel/src/digitalmodel/web/` has 69 source files and 0 tests
- Target: SKELETON → DEVELOPMENT maturity (need at least import tests + basic unit tests)

### Steps
1. Read `digitalmodel/src/digitalmodel/web/` to understand the package structure
2. List all .py files: identify the main modules and their public APIs
3. Create: `digitalmodel/tests/web/__init__.py`
4. Write: `digitalmodel/tests/web/test_web_imports.py`
   - Test: import every submodule without error (parametrize over all .py files)
   - Test: key classes/functions exist in expected modules
5. Write: `digitalmodel/tests/web/test_web_core.py`
   - Pick the 3-5 most important modules and write focused unit tests
   - Mock Flask/web framework dependencies — do NOT require a running server
   - Test: configuration loading, route registration, utility functions
6. Run tests: `uv run pytest digitalmodel/tests/web/ -v`
   - If Flask is not installed, ensure all tests use mocks or skip gracefully with `pytest.importorskip("flask")`

### Commit message
```
test(web): initial test coverage — import tests + core unit tests (#1584)
```

---

## TASK 3: Test Coverage — Remaining SKELETON Packages (GH issue #1589)

### Context
- Packages with zero tests: field_development, geotechnical, nde, reservoir
- Target: at least import smoke tests + 2-3 unit tests per package

### Steps
1. For each package, read the source to understand the API
2. Create test directories and __init__.py for each:
   - `digitalmodel/tests/field_development/__init__.py`
   - `digitalmodel/tests/geotechnical/__init__.py`
   - `digitalmodel/tests/nde/__init__.py`
3. Write import smoke tests for each package:
   - `digitalmodel/tests/field_development/test_field_dev_imports.py`
   - `digitalmodel/tests/geotechnical/test_geotech_imports.py`
   - `digitalmodel/tests/nde/test_nde_imports.py`
4. Write 2-3 focused unit tests per package testing the main public functions
   - Mock matplotlib, plotly, and any heavy dependencies
   - Use `pytest.importorskip()` for optional deps
5. Run all: `uv run pytest digitalmodel/tests/field_development/ digitalmodel/tests/geotechnical/ digitalmodel/tests/nde/ -v`

### Commit message
```
test(packages): SKELETON uplift — field_development, geotechnical, nde smoke + unit tests (#1589)
```

---

## TASK 4: Refactor reservoir/stratigraphic.py (GH issue #1633)

### Context
- `digitalmodel/src/digitalmodel/reservoir/stratigraphic.py` is a raw script (runs on import)
- Needs refactoring into proper importable module with functions/classes

### Steps
1. Read the current `stratigraphic.py` to understand what it does
2. Write tests first: `digitalmodel/tests/reservoir/test_stratigraphic.py`
   - Test: core functions can be imported without side effects
   - Test: main processing function produces expected output shape
   - Test: edge cases (empty input, missing columns)
3. Refactor `stratigraphic.py`:
   - Wrap top-level code in functions
   - Add `if __name__ == "__main__":` guard
   - Add type hints and docstrings to public functions
   - Preserve all existing functionality
4. Also write: `digitalmodel/tests/reservoir/test_reservoir_imports.py`
   - Import smoke tests for the entire reservoir package
5. Run tests: `uv run pytest digitalmodel/tests/reservoir/ -v`

### Commit message
```
refactor(reservoir): stratigraphic.py — raw script to importable module with tests (#1633)
```

---

Post a brief progress comment on GH issues #1647, #1584, #1589, #1633 when each task completes.
