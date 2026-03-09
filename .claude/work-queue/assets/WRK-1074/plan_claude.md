# WRK-1074 Plan — Claude

## Problem
assetutilities (v0.0.8) has 41 unique import surfaces used across digitalmodel and worldenergydata.
No contract tests exist to catch silent API breakage. A renamed function or changed signature
silently breaks consumers until their own unit tests happen to hit the changed path.

## Approach
Consumer-side contract tests: `tests/contracts/` in each consuming repo, using real assetutilities
(no mocks). Tests assert importability, signatures, and return types of the symbols actually used.
Failure output enriched with assetutilities version + symbol + test name.

## Implementation Steps

### Step 1 — conftest.py (both repos)
`tests/contracts/conftest.py` in digitalmodel and worldenergydata:
- `au_version()` fixture returning `importlib.metadata.version("assetutilities")`
- `pytest_runtest_makereport` hook: on failure, prepend
  `[CONTRACT VIOLATION] symbol=<symbol> au_version=<ver> test=<node_id>` to longrepr
- Register `contracts` marker in `pytest_configure`

### Step 2 — digitalmodel contract tests (4 files)

**test_assetutilities_data_contract.py**
- SaveData: importable; callable; signature has `data` + `file_path` params
- ReadData: importable; callable; signature has `file_path` param
- AttributeDict: importable; subclass of dict; supports attribute access
- Transform: importable; callable

**test_assetutilities_yml_contract.py**
- WorkingWithYAML: importable; instance has `.read_yaml()` and `.save_yaml()` methods
- ymlInput: importable as legacy alias; callable

**test_assetutilities_units_contract.py**
- TrackedQuantity: importable from `assetutilities.units.quantity`; accepts (value, unit)
- unit_checked: importable; is callable (decorator factory)
- UnitMismatchError: importable; is subclass of Exception

**test_assetutilities_common_contract.py**
- FileManagement: importable; has `.check_if_file_exists()` method
- update_deep_dictionary: importable; callable; merges two dicts correctly
- is_file_valid_func, is_dir_valid_func: importable; callable

### Step 3 — worldenergydata contract tests (2 files)

**test_assetutilities_data_contract.py**
- SaveData, ReadData, AttributeDict (mirror of digitalmodel data contract)

**test_assetutilities_engine_contract.py**
- engine: importable from `assetutilities.engine.engine`; is a class or callable
- FileManagement: importable; has file check method
- WorkingWithYAML: importable; has read/write methods

### Step 4 — run-all-tests.sh integration
Add `contracts` test step after unit tests for digitalmodel and worldenergydata:
```bash
PYTHONPATH="src:../assetutilities/src" uv run python -m pytest tests/contracts/ \
  -v --tb=short -m contracts
```
Exit code propagated; contract step failure → run-all-tests.sh non-zero exit.

### Step 5 — docs/api-contracts.md per repo
Table of contracted symbols: module path | symbol | stability (stable/provisional) | notes.
Stability policy: `stable` = no breaking changes without assetutilities major version bump.

## Test Strategy
- All tests use real assetutilities; no mocks; no file I/O; no DB
- Pure import + introspection: `inspect.signature()`, `issubclass()`, `hasattr()`
- `@pytest.mark.contracts` on every test
- Run time: <100ms per file (unit speed)
- PYTHONPATH = `src:../assetutilities/src` consistent across repos
- Module-level `AU_VERSION = importlib.metadata.version("assetutilities")` in each file

## Deferred
- Database contracts (need live DB) → @live_data marker, future WRK
- Excel/PDF module contracts (file I/O fixtures needed) → future WRK
- Engine instantiation tests (heavyweight) → integration tests
- Constants contract: add basic smoke import test only (unlikely to break)

## Risk
- assetutilities installed as git URL in worldenergydata — version pinning gap; note in docs
- ymlInput is a legacy alias; may be removed in a future version — flag as `provisional`
