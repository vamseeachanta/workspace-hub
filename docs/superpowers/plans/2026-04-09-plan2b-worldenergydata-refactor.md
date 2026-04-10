# Plan 2B: worldenergydata Refactor

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add data resolver for /mnt/ace data, consolidate duplicated modules (bsee, marine_safety), replace print statements with logging, fix packaging, and make mypy block CI.

**Architecture:** New data_resolver module with env var / symlink / fallback resolution. Module consolidation deletes stub directories (modules/bsee has 40 files vs bsee's 526). Print→logging migration uses existing common/logging.py infrastructure.

**Tech Stack:** Python 3.9+, setuptools, pytest, mypy, loguru

**Repo:** `/mnt/local-analysis/workspace-hub/worldenergydata`

---

### Task 1: Create Data Resolver Module

**Files:**
- Create: `src/worldenergydata/common/data_resolver.py`
- Create: `scripts/setup-data-link.sh`
- Modify: `.gitignore` (add data symlink entry)

- [ ] **Step 1: Write the data resolver test**

Create `tests/unit/common/test_data_resolver.py`:
```python
"""Tests for data_resolver module."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from worldenergydata.common.data_resolver import (
    DataNotFoundError,
    get_data_root,
    get_module_data,
    _clear_cache,
)


@pytest.fixture(autouse=True)
def clear_resolver_cache():
    """Clear the cached data root between tests."""
    _clear_cache()
    yield
    _clear_cache()


def test_get_data_root_from_env_var(tmp_path):
    """WED_DATA_ROOT env var takes highest priority."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    with patch.dict(os.environ, {"WED_DATA_ROOT": str(data_dir)}):
        assert get_data_root() == data_dir


def test_get_data_root_from_symlink(tmp_path, monkeypatch):
    """Symlink at project_root/data is second priority."""
    # Create a fake project with data symlink
    project = tmp_path / "project"
    project.mkdir()
    actual_data = tmp_path / "actual_data"
    actual_data.mkdir()
    data_link = project / "data"
    data_link.symlink_to(actual_data)

    monkeypatch.delenv("WED_DATA_ROOT", raising=False)
    # Patch project root detection
    with patch("worldenergydata.common.data_resolver._get_project_root", return_value=project):
        result = get_data_root()
        assert result == actual_data


def test_get_data_root_fallback(tmp_path, monkeypatch):
    """Falls back to project_root/data/ directory."""
    project = tmp_path / "project"
    project.mkdir()
    data_dir = project / "data"
    data_dir.mkdir()

    monkeypatch.delenv("WED_DATA_ROOT", raising=False)
    with patch("worldenergydata.common.data_resolver._get_project_root", return_value=project):
        assert get_data_root() == data_dir


def test_get_data_root_raises_when_missing(tmp_path, monkeypatch):
    """Raises DataNotFoundError when no data directory found."""
    project = tmp_path / "empty_project"
    project.mkdir()

    monkeypatch.delenv("WED_DATA_ROOT", raising=False)
    with patch("worldenergydata.common.data_resolver._get_project_root", return_value=project):
        with pytest.raises(DataNotFoundError, match="No data directory found"):
            get_data_root()


def test_get_module_data(tmp_path):
    """get_module_data returns path to specific module's data."""
    data_dir = tmp_path / "data" / "modules" / "bsee"
    data_dir.mkdir(parents=True)

    with patch.dict(os.environ, {"WED_DATA_ROOT": str(tmp_path / "data")}):
        result = get_module_data("bsee")
        assert result == data_dir


def test_get_module_data_missing_module(tmp_path):
    """get_module_data raises when module directory doesn't exist."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    with patch.dict(os.environ, {"WED_DATA_ROOT": str(data_dir)}):
        with pytest.raises(DataNotFoundError, match="Module data not found: nonexistent"):
            get_module_data("nonexistent")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /mnt/local-analysis/workspace-hub/worldenergydata && uv run pytest tests/unit/common/test_data_resolver.py -v --tb=short 2>&1`
Expected: ImportError — module doesn't exist yet

- [ ] **Step 3: Implement data_resolver.py**

Create `src/worldenergydata/common/data_resolver.py`:
```python
"""Centralized data path resolution for worldenergydata.

Resolution order:
1. WED_DATA_ROOT environment variable (explicit override)
2. Symlink at <project_root>/data → external mount (convention)
3. Fallback to <project_root>/data/ directory (development)

Usage:
    from worldenergydata.common.data_resolver import get_data_root, get_module_data

    data_root = get_data_root()
    bsee_data = get_module_data("bsee")
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


class DataNotFoundError(FileNotFoundError):
    """Raised when data directory cannot be resolved."""


def _get_project_root() -> Path:
    """Find the project root by looking for pyproject.toml."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()


@lru_cache(maxsize=1)
def get_data_root() -> Path:
    """Resolve the data root directory.

    Returns:
        Path to the data root directory.

    Raises:
        DataNotFoundError: If no valid data directory is found.
    """
    # Priority 1: Environment variable
    env_root = os.environ.get("WED_DATA_ROOT")
    if env_root:
        path = Path(env_root)
        if path.is_dir():
            return path
        raise DataNotFoundError(
            f"WED_DATA_ROOT={env_root} is set but directory does not exist"
        )

    # Priority 2: Symlink at project_root/data
    project_root = _get_project_root()
    data_dir = project_root / "data"

    if data_dir.is_symlink():
        target = data_dir.resolve()
        if target.is_dir():
            return target
        raise DataNotFoundError(
            f"data/ symlink points to {target} which does not exist"
        )

    # Priority 3: Fallback to data/ directory
    if data_dir.is_dir():
        return data_dir

    raise DataNotFoundError(
        f"No data directory found. Options:\n"
        f"  1. Set WED_DATA_ROOT=/path/to/data\n"
        f"  2. Create symlink: ln -s /path/to/data {data_dir}\n"
        f"  3. Create directory: mkdir -p {data_dir}"
    )


def get_module_data(module: str) -> Path:
    """Get the data directory for a specific module.

    Args:
        module: Module name (e.g., 'bsee', 'hse', 'sodir').

    Returns:
        Path to the module's data directory.

    Raises:
        DataNotFoundError: If the module data directory doesn't exist.
    """
    root = get_data_root()
    module_path = root / "modules" / module
    if module_path.is_dir():
        return module_path
    raise DataNotFoundError(
        f"Module data not found: {module} (looked in {module_path})"
    )


def _clear_cache() -> None:
    """Clear the cached data root. Used in tests."""
    get_data_root.cache_clear()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /mnt/local-analysis/workspace-hub/worldenergydata && uv run pytest tests/unit/common/test_data_resolver.py -v --tb=short 2>&1`
Expected: 6 passed

- [ ] **Step 5: Create setup-data-link.sh**

Create `scripts/setup-data-link.sh`:
```bash
#!/usr/bin/env bash
# Setup data symlink for worldenergydata
# Usage: ./scripts/setup-data-link.sh [/path/to/data]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEFAULT_TARGET="/mnt/ace/worldenergydata/data"
TARGET="${1:-$DEFAULT_TARGET}"

if [ ! -d "$TARGET" ]; then
    echo "ERROR: Data directory does not exist: $TARGET"
    echo "Usage: $0 /path/to/worldenergydata/data"
    exit 1
fi

LINK="$PROJECT_ROOT/data"

if [ -L "$LINK" ]; then
    CURRENT=$(readlink -f "$LINK")
    if [ "$CURRENT" = "$(readlink -f "$TARGET")" ]; then
        echo "Symlink already correct: data -> $TARGET"
    else
        echo "Updating symlink: data -> $TARGET (was $CURRENT)"
        rm "$LINK"
        ln -s "$TARGET" "$LINK"
    fi
elif [ -d "$LINK" ]; then
    echo "WARNING: data/ is a real directory, not a symlink."
    echo "To use external data, remove it first: rm -rf $LINK"
    exit 1
else
    ln -s "$TARGET" "$LINK"
    echo "Created symlink: data -> $TARGET"
fi

# Verify expected structure
for dir in modules/bsee modules/hse; do
    if [ -d "$TARGET/$dir" ]; then
        echo "  OK: $dir exists"
    else
        echo "  WARN: $dir not found in $TARGET"
    fi
done

echo "Done. Data root: $TARGET"
```

- [ ] **Step 6: Make script executable and commit**

```bash
cd /mnt/local-analysis/workspace-hub/worldenergydata
chmod +x scripts/setup-data-link.sh
git add src/worldenergydata/common/data_resolver.py tests/unit/common/test_data_resolver.py scripts/setup-data-link.sh
git commit -m "feat(data): add centralized data resolver with env/symlink/fallback resolution

WED_DATA_ROOT env var > symlink at data/ > fallback to data/ directory.
Includes setup script for creating symlinks and 6 unit tests."
```

---

### Task 2: Migrate Hardcoded Data Paths to Resolver

**Files:**
- Modify: ~25-30 files with hardcoded `Path("data/...")`

The top files to migrate (from exploration):
- `src/worldenergydata/cli/main.py` (lines 241-249, 7 paths)
- `src/worldenergydata/bsee/data/loaders/production/production_loader.py` (line 26)
- `src/worldenergydata/bsee/analysis/financial/data_loader.py` (line 129)
- `src/worldenergydata/scheduler/jobs/bsee_refresh.py` (line 45)
- `src/worldenergydata/scheduler/jobs/sodir_refresh.py` (line 35)
- `src/worldenergydata/scheduler/jobs/metocean_refresh.py` (line 27)
- `src/worldenergydata/scheduler/jobs/eia_us_refresh.py` (line 30)
- All `bsee/data/loaders/` files

- [ ] **Step 1: Find all hardcoded data paths**

Run: `cd /mnt/local-analysis/workspace-hub/worldenergydata && grep -rn 'Path("data/' src/ --include="*.py" | grep -v __pycache__`

- [ ] **Step 2: Replace each with data_resolver calls**

Pattern: Replace `Path("data/modules/bsee")` with:
```python
from worldenergydata.common.data_resolver import get_module_data
# ...
data_path = get_module_data("bsee")
```

For paths like `Path("data/bsee")` (without modules/):
```python
from worldenergydata.common.data_resolver import get_data_root
# ...
data_path = get_data_root() / "bsee"
```

- [ ] **Step 3: Run tests**

Run: `cd /mnt/local-analysis/workspace-hub/worldenergydata && uv run pytest tests/ -x -q --tb=short 2>&1 | tail -15`

- [ ] **Step 4: Commit**

```bash
git add -u
git commit -m "refactor(data): migrate hardcoded data paths to data_resolver

Replaced 40+ hardcoded Path('data/...') references with
get_data_root() and get_module_data() calls."
```

---

### Task 3: Consolidate Module Duplication

**Analysis results:**
- `bsee/` has 526 files (canonical, production code)
- `modules/bsee/` has 40 files (stubs, skeletal)
- `marine_safety/` has 194 files (canonical)
- `modules/marine_safety/` has 12 files (stubs)
- Import ratio: 268 imports from `worldenergydata.bsee.*` vs 56 from `worldenergydata.modules.bsee.*`
- MODULE_INDEX.md references `worldenergydata.bsee` as canonical

**Strategy:** Delete stub directories, redirect the 56 imports from `modules.bsee` to `bsee`.

- [ ] **Step 1: Map all imports from modules.bsee and modules.marine_safety**

Run: `cd /mnt/local-analysis/workspace-hub/worldenergydata && grep -rn "from worldenergydata.modules.bsee" src/ tests/ --include="*.py" | grep -v __pycache__`

Run: `cd /mnt/local-analysis/workspace-hub/worldenergydata && grep -rn "from worldenergydata.modules.marine_safety" src/ tests/ --include="*.py" | grep -v __pycache__`

- [ ] **Step 2: Update all imports to use canonical paths**

For each import found:
- `from worldenergydata.modules.bsee.X import Y` → `from worldenergydata.bsee.X import Y`
- `from worldenergydata.modules.marine_safety.X import Y` → `from worldenergydata.marine_safety.X import Y`

- [ ] **Step 3: Add backward-compatible re-exports in modules/**

Create `src/worldenergydata/modules/bsee/__init__.py`:
```python
"""Backward-compatible re-exports. Use worldenergydata.bsee directly."""
from worldenergydata.bsee import *  # noqa: F401,F403
```

Create `src/worldenergydata/modules/marine_safety/__init__.py`:
```python
"""Backward-compatible re-exports. Use worldenergydata.marine_safety directly."""
from worldenergydata.marine_safety import *  # noqa: F401,F403
```

- [ ] **Step 4: Delete stub files in modules/ (keep only __init__.py re-exports)**

Remove all files in `modules/bsee/` and `modules/marine_safety/` EXCEPT the `__init__.py` re-export files.

- [ ] **Step 5: Run tests**

Run: `cd /mnt/local-analysis/workspace-hub/worldenergydata && uv run pytest tests/ -x -q --tb=short 2>&1 | tail -15`

- [ ] **Step 6: Commit**

```bash
git add -u && git add src/worldenergydata/modules/bsee/__init__.py src/worldenergydata/modules/marine_safety/__init__.py
git commit -m "refactor(modules): consolidate bsee and marine_safety to canonical locations

bsee/ (526 files) is canonical; modules/bsee/ stubs removed.
marine_safety/ (194 files) is canonical; modules/marine_safety/ stubs removed.
Backward-compatible re-exports preserved in modules/__init__.py."
```

---

### Task 4: Replace Print Statements with Logging

**Files:**
- Modify: 93+ files containing print() statements
- Primary targets (highest count): cli/commands/*.py, marine_safety/cli_import.py, vessel_hull_models/cli.py

**Existing infrastructure:** `src/worldenergydata/common/logging.py` provides `get_logger()` — already production-ready.

- [ ] **Step 1: Create replacement script**

Create `scripts/migrate_print_to_logging.py`:
```python
"""Migrate print() statements to logging calls.

Usage: python scripts/migrate_print_to_logging.py src/worldenergydata/
"""
import re
import sys
from pathlib import Path


def process_file(filepath: Path) -> int:
    """Replace print() with logger calls in a single file. Returns count of replacements."""
    content = filepath.read_text()

    # Skip if no print statements
    if "print(" not in content:
        return 0

    lines = content.split("\n")
    replacements = 0
    has_logger_import = "get_logger" in content or "logger" in content

    new_lines = []
    for line in lines:
        stripped = line.lstrip()
        # Simple print() → logger.info()
        if stripped.startswith("print(") and not stripped.startswith("print(f\"ERROR") and not stripped.startswith("print(f\"Warning"):
            indent = line[:len(line) - len(stripped)]
            # Extract print content
            new_line = line.replace("print(", "logger.info(", 1)
            new_lines.append(new_line)
            replacements += 1
        elif stripped.startswith("print(f\"ERROR") or stripped.startswith("print(f\"Error"):
            new_lines.append(line.replace("print(", "logger.error(", 1))
            replacements += 1
        elif stripped.startswith("print(f\"Warning") or stripped.startswith("print(f\"WARN"):
            new_lines.append(line.replace("print(", "logger.warning(", 1))
            replacements += 1
        else:
            new_lines.append(line)

    if replacements > 0:
        # Add logger import if not present
        if not has_logger_import:
            # Insert after last import
            import_idx = 0
            for i, line in enumerate(new_lines):
                if line.startswith("import ") or line.startswith("from "):
                    import_idx = i + 1
            new_lines.insert(import_idx, "")
            new_lines.insert(import_idx + 1, "from worldenergydata.common.logging import get_logger")
            new_lines.insert(import_idx + 2, "")
            new_lines.insert(import_idx + 3, "logger = get_logger(__name__)")

        filepath.write_text("\n".join(new_lines))

    return replacements


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("src/worldenergydata")
    total = 0
    for py_file in sorted(root.rglob("*.py")):
        if "__pycache__" in str(py_file):
            continue
        count = process_file(py_file)
        if count > 0:
            print(f"  {py_file}: {count} replacements")
            total += count
    print(f"\nTotal: {total} print() → logger replacements")
```

- [ ] **Step 2: Run the migration script**

Run: `cd /mnt/local-analysis/workspace-hub/worldenergydata && uv run python scripts/migrate_print_to_logging.py src/worldenergydata/`

- [ ] **Step 3: Manual review of high-count files**

Check the top 5 files (cli_import.py, landman.py, vessel_hull_models/cli.py) — ensure the logger calls make sense. Some print() calls may be intentional CLI output (typer.echo is preferred for CLI).

- [ ] **Step 4: Run tests**

Run: `cd /mnt/local-analysis/workspace-hub/worldenergydata && uv run pytest tests/ -x -q --tb=short 2>&1 | tail -15`

- [ ] **Step 5: Commit**

```bash
git add -u && git add scripts/migrate_print_to_logging.py
git commit -m "refactor(logging): replace 487 print() statements with structured logging

Uses existing worldenergydata.common.logging infrastructure.
Migration script included at scripts/migrate_print_to_logging.py."
```

---

### Task 5: Fix Packaging

**Files:**
- Modify: `pyproject.toml`
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Replace assetutilities git dependency**

In `pyproject.toml` line 27, replace:
```toml
"assetutilities @ git+https://github.com/vamseeachanta/assetutilities.git",
```
with editable local path (matching digitalmodel pattern):
```toml
"assetutilities>=0.0.7",
```

And in UV sources section (or create if missing):
```toml
[tool.uv.sources]
assetutilities = { path = "../assetutilities", editable = true }
```

- [ ] **Step 2: Add upper bounds to dependencies**

Add `<NEXT_MAJOR` upper bounds to all 28 core dependencies. Pattern: `>=X.Y.Z` → `>=X.Y.Z,<NEXT_MAJOR`.

- [ ] **Step 3: Make mypy block CI**

In `.github/workflows/ci.yml` line 131, remove `|| true`:
```yaml
      - name: Run mypy
        run: |
          uv run mypy src/worldenergydata/common/ \
            --ignore-missing-imports \
            --no-error-summary \
            --show-error-codes
```

Note: Keep scope limited to `common/` for now (already typed). Expand later.

- [ ] **Step 4: Verify dependency resolution**

Run: `cd /mnt/local-analysis/workspace-hub/worldenergydata && uv lock 2>&1 | tail -5`

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml .github/workflows/ci.yml uv.lock
git commit -m "fix(packaging): replace git dep with local path, pin deps, make mypy block CI"
```

---

### Task 6: Improve Test Coverage on Validation Layer

**Files:**
- Create: `tests/unit/validation/test_base.py`
- Create: `tests/unit/validation/test_schemas.py`
- Create: `tests/unit/validators/test_data_validator.py`

The validation layer has 1,697 lines of implemented code but needs test coverage.

- [ ] **Step 1: Write tests for validation/base.py**

Test the core classes: ValidationError, ValidationResult, BaseValidator, FieldValidator.

```python
"""Tests for validation base module."""

import pytest
from worldenergydata.validation.base import (
    ValidationError,
    ValidationResult,
    FieldValidator,
)


def test_validation_error_creation():
    err = ValidationError(field="temperature", message="Out of range", severity="error")
    assert err.field == "temperature"
    assert err.severity == "error"


def test_validation_result_is_valid_when_no_errors():
    result = ValidationResult()
    assert result.is_valid


def test_validation_result_tracks_errors():
    result = ValidationResult()
    result.add_error(ValidationError(field="x", message="bad", severity="error"))
    assert not result.is_valid
    assert len(result.errors) == 1


def test_validation_result_tracks_warnings():
    result = ValidationResult()
    result.add_warning(ValidationError(field="x", message="suspicious", severity="warning"))
    assert result.is_valid  # Warnings don't invalidate
    assert len(result.warnings) == 1
```

- [ ] **Step 2: Write tests for validators/data_validator.py**

Test DataValidator with sample DataFrames:

```python
"""Tests for data validator."""

import pandas as pd
import pytest
from worldenergydata.validators.data_validator import DataValidator


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "well_id": ["W001", "W002", None, "W004"],
        "production": [100.0, 200.0, 150.0, -50.0],
        "date": ["2024-01", "2024-02", "2024-03", "2024-04"],
    })


def test_validator_detects_missing_data(sample_df):
    validator = DataValidator()
    result = validator.validate_dataframe(sample_df)
    # Should detect the None in well_id
    assert any("missing" in str(e).lower() for e in result.get("missing_data", []))


def test_validator_generates_report(sample_df):
    validator = DataValidator()
    report = validator.generate_report(sample_df)
    assert isinstance(report, str)
    assert len(report) > 0
```

- [ ] **Step 3: Run new tests**

Run: `cd /mnt/local-analysis/workspace-hub/worldenergydata && uv run pytest tests/unit/validation/ tests/unit/validators/ -v --tb=short 2>&1`

- [ ] **Step 4: Check coverage improvement**

Run: `cd /mnt/local-analysis/workspace-hub/worldenergydata && uv run pytest tests/ -q --cov=src/worldenergydata --cov-report=term-missing 2>&1 | tail -30`

- [ ] **Step 5: Commit**

```bash
git add tests/unit/validation/ tests/unit/validators/
git commit -m "test(validation): add tests for validation base, schemas, and data validator"
```

---

### Task 7: Final Verification

- [ ] **Step 1: Run full test suite**

```bash
cd /mnt/local-analysis/workspace-hub/worldenergydata
uv run pytest tests/ -q --tb=short 2>&1 | tail -15
```

- [ ] **Step 2: Verify data resolver works with real data**

```bash
cd /mnt/local-analysis/workspace-hub/worldenergydata
WED_DATA_ROOT=/mnt/ace/worldenergydata/data uv run python -c "
from worldenergydata.common.data_resolver import get_data_root, get_module_data
print(f'Data root: {get_data_root()}')
print(f'BSEE data: {get_module_data(\"bsee\")}')
print(f'HSE data: {get_module_data(\"hse\")}')
print('All OK')
"
```
Expected: All OK with correct paths

- [ ] **Step 3: Verify zero print statements remain**

```bash
cd /mnt/local-analysis/workspace-hub/worldenergydata
grep -rn "^[[:space:]]*print(" src/worldenergydata/ --include="*.py" | grep -v __pycache__ | wc -l
```
Expected: 0 (or near-zero if some are intentional CLI output)

- [ ] **Step 4: Check module consolidation**

```bash
cd /mnt/local-analysis/workspace-hub/worldenergydata
uv run python -c "
from worldenergydata.bsee import BSEEData
from worldenergydata.modules.bsee import BSEEData as BSEEData2
print(f'Direct: {BSEEData}')
print(f'Via modules: {BSEEData2}')
print(f'Same object: {BSEEData is BSEEData2}')
"
```
Expected: Same object: True
