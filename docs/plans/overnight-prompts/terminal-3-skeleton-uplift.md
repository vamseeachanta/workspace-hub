# Terminal 3 — Codex Seat 2 — SKELETON Package Test Coverage Uplift

We are in /mnt/local-analysis/workspace-hub. Execute these 2 tasks in order.
Use `uv run` for all Python — never bare `python3` or `pip`.
Commit to main and push after each task. Do not branch.
Run `git pull origin main` before every push.
TDD: write tests BEFORE implementation when adding new code.
Do NOT ask the user any questions — make reasonable decisions and document them.

IMPORTANT: Do NOT write to digitalmodel/tests/orcawave/ or digitalmodel/tests/solver/ —
those directories are owned by Terminal 2. Stick to the packages listed below.

## TASK 1: Test Coverage for SKELETON Packages (GH #1589)

### Context
Issue #1589 identifies 4 SKELETON packages with zero test coverage:
- digitalmodel/src/digitalmodel/field_development/
- digitalmodel/src/digitalmodel/geotechnical/
- digitalmodel/src/digitalmodel/nde/
- digitalmodel/src/digitalmodel/reservoir/

Each needs at least 1 test file to move from SKELETON → DEVELOPMENT.

### What to do
For EACH of the 4 packages:
1. Read all source files in the package to understand the API
2. Create test directory: digitalmodel/tests/{package_name}/
3. Write at least one test file per package:
   - digitalmodel/tests/field_development/test_field_development.py
   - digitalmodel/tests/geotechnical/test_geotechnical.py
   - digitalmodel/tests/nde/test_nde.py
   - digitalmodel/tests/reservoir/test_reservoir.py
   - Plus __init__.py in each test directory
4. Test strategy per package:
   - Import tests (verify package is importable)
   - Class instantiation tests (create objects with valid params)
   - Config/schema validation tests (if Pydantic models exist)
   - Edge case tests (empty input, invalid types)
5. Mock any external dependencies (databases, APIs, file I/O to /mnt)
6. Run: `uv run pytest digitalmodel/tests/field_development/ digitalmodel/tests/geotechnical/ digitalmodel/tests/nde/ digitalmodel/tests/reservoir/ -v`

### Acceptance criteria
- 4 new test directories with at least 1 test file each
- At least 3 test functions per package (12+ total)
- All tests pass
- No tests require external resources (databases, network, /mnt paths)
- All 4 packages move from SKELETON → DEVELOPMENT

### Commit message
test(packages): add tests for field_development, geotechnical, nde, reservoir — SKELETON → DEVELOPMENT (#1589)

---

## TASK 2: Web Package Test Coverage (GH #1584)

### Context
Issue #1584: The web package at digitalmodel/src/digitalmodel/web/ has 69 source files
and 0 tests. This is the largest untested package. Full coverage is not expected overnight —
focus on the top 10 most important modules.

### What to do
1. Read the web package directory listing to understand structure
2. Identify the 10 most important/central modules (by import count or size)
3. Create digitalmodel/tests/web/ directory
4. Write test files for at least 5 key modules:
   - digitalmodel/tests/web/test_core.py (or whatever the main entry module is)
   - digitalmodel/tests/web/test_config.py (if config models exist)
   - digitalmodel/tests/web/test_utils.py (utility functions)
   - digitalmodel/tests/web/test_routes.py (if web routes exist — test routing logic)
   - digitalmodel/tests/web/test_data_models.py (request/response models)
   - digitalmodel/tests/web/__init__.py
5. Focus on import tests, model validation, and pure function unit tests
6. Mock all network/HTTP calls — no live requests
7. Run: `uv run pytest digitalmodel/tests/web/ -v`

### Acceptance criteria
- digitalmodel/tests/web/ directory with at least 5 test files
- At least 20 test functions total
- All tests pass without network access
- Web package moves from SKELETON → DEVELOPMENT

### Commit message
test(web): add test suite for web package — SKELETON → DEVELOPMENT (#1584)

---

## After all tasks
Post a brief progress comment on each GitHub issue (#1589, #1584) in repo vamseeachanta/workspace-hub:
"Overnight agent run (2026-04-01): [artifact] committed. See [path]."
