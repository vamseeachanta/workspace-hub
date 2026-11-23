# Plan 2A: digitalmodel Refactor

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean digitalmodel's packaging (deduplicate deps, fix version targeting), type solver entry points, triage TODOs, and clean stale files. Note: curves.py is 29K lines of data/comment placeholders (not code) — decomposition is not applicable.

**Architecture:** Targeted edits to pyproject.toml for dependency cleanup, type annotations on small solver files, and file cleanup.

**Tech Stack:** Python 3.11+, setuptools, pytest, mypy

**Repo:** `/mnt/local-analysis/workspace-hub/digitalmodel`

---

### Task 1: Deduplicate Dependencies in pyproject.toml

**Files:**
- Modify: `pyproject.toml` (lines 25-180 dependencies section)

**17 packages with duplicate/conflicting entries to resolve:**

| Package | Keep | Remove |
|---------|------|--------|
| assetutilities | `>=0.0.7` (line 33) | bare entry (line 32) |
| bumpver | `>=2023.1129` (line 46) | bare entry (line 45) |
| dash | `>=3.1.0,<4.0.0` (line 53) | bare entry (line 52) |
| deepdiff | `>=8.0.0,<9.0.0` (line 55) | bare entry (line 54) |
| OrcFxAPI | one copy (line 87) | duplicate (line 88) |
| pandas | `>=2.0.0,<3.0.0` (line 90) | bare entry (line 89) |
| PyPDF2/pypdf2 | `pypdf2>=3.0.0,<4.0.0` (line 106) | case variant (line 105) |
| pytest | `>=7.4.3,<9.0.0` (line 109) | bare entry (line 108) |
| pytest-mock | `>=3.12.0,<4.0.0` (line 113) | pinned `==3.12.0` (line 112) |
| pyyaml | `>=6.0.0,<7.0.0` (line 131) | bare (line 130) AND `==6.0.1` (line 132) |
| scrapy | `>=2.11.0,<3.0.0` (line 141) | bare entry (line 140) |
| tabulate | `>=0.9.0,<1.0.0` (line 152) | bare entry (line 151) |
| webcolors | `>=1.13,<2.0` (line 158) | bare entry (line 157) |
| xlrd | `>=2.0.0,<3.0.0` (line 161) | bare entry (line 160) |
| xlsxwriter | `>=3.1.0,<4.0.0` (line 163) | bare (line 162) AND `==3.1.9` (line 164) |
| xmltodict | `>=0.13.0,<1.0.0` (line 166) | bare entry (line 165) |

- [ ] **Step 1: Remove all duplicate/bare entries**

For each package above, remove the "Remove" entries, keeping only the versioned one. This reduces ~25 duplicate lines.

- [ ] **Step 2: Add upper bounds to remaining deps without them**

Scan remaining dependencies for any `>=X.Y.Z` without `<NEXT_MAJOR`. Add upper bounds using the `<NEXT_MAJOR` pattern.

- [ ] **Step 3: Move optional packages to extras groups**

Move these from core dependencies to new optional groups:

```toml
[project.optional-dependencies]
solvers = [
    "OrcFxAPI",
    "gmsh>=4.12.0,<5.0.0",
]
viz = [
    "dash>=3.1.0,<4.0.0",
    "kaleido>=0.2.0,<1.0.0",
    "seaborn>=0.13.0,<1.0.0",
]
web = [
    "fastapi>=0.100.0,<1.0.0",
    "uvicorn>=0.25.0,<1.0.0",
    "sqlalchemy>=2.0.0,<3.0.0",
]
async = [
    "aiofiles>=23.0.0,<25.0.0",
    "asyncpg>=0.29.0,<1.0.0",
]
```

- [ ] **Step 4: Verify dependency resolution**

Run: `cd /mnt/local-analysis/workspace-hub/digitalmodel && uv lock 2>&1 | tail -5`

- [ ] **Step 5: Run tests**

Run: `cd /mnt/local-analysis/workspace-hub/digitalmodel && uv run pytest tests/ -x -q --tb=short --ignore=tests/visualization 2>&1 | tail -15`
Expected: Tests pass (some may skip due to missing optional deps — that's expected)

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "fix(packaging): deduplicate 17 conflicting deps, add upper bounds, move optional to extras"
```

---

### Task 2: Fix Version Targeting

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Align classifiers with requires-python**

`requires-python = ">=3.11"` (line 10) but classifiers list 3.9/3.10. Remove stale classifiers:

```toml
classifiers = [
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
```

- [ ] **Step 2: Align mypy python_version**

Change `[tool.mypy]` `python_version` from `"3.9"` to `"3.11"` (line 256).

- [ ] **Step 3: Align black target-version**

Change `[tool.black]` `target-version` from `['py39', 'py310', 'py311']` to `['py311', 'py312']` (line 248).

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "fix(packaging): align classifiers and tool targets with requires-python >=3.11"
```

---

### Task 3: Type Solver Entry Points

**Files:**
- Modify: `src/digitalmodel/solvers/orcaflex/orcaflex.py` (33 lines)
- Modify: `src/digitalmodel/hydrodynamics/aqwa/aqwa_router.py` (124 lines)

- [ ] **Step 1: Add type hints to orcaflex.py**

The file is only 33 lines with 2 methods. Add full type annotations:

```python
from __future__ import annotations

from typing import Any


class OrcaFlex:
    """OrcaFlex solver router."""

    def __init__(self) -> None:
        pass

    def router(self, cfg: dict[str, Any]) -> dict[str, Any]:
        """Route OrcaFlex configuration to appropriate handlers."""
        # ... existing body
```

- [ ] **Step 2: Add type hints to aqwa_router.py**

The file is 124 lines with 4 methods. Add annotations to all:

```python
from __future__ import annotations

from typing import Any, Optional


class Aqwa:
    """AQWA solver router."""

    def __init__(self) -> None: ...

    @staticmethod
    def _resolve_attr(name: str, fallback: Any = None) -> Any: ...

    def router(self, cfg: dict[str, Any]) -> dict[str, Any]: ...

    def get_cfg_with_master_data(self, cfg: dict[str, Any]) -> dict[str, Any]: ...
```

- [ ] **Step 3: Run mypy on both files**

Run: `cd /mnt/local-analysis/workspace-hub/digitalmodel && uv run mypy src/digitalmodel/solvers/orcaflex/orcaflex.py src/digitalmodel/hydrodynamics/aqwa/aqwa_router.py --ignore-missing-imports 2>&1`
Expected: Success (0 errors)

- [ ] **Step 4: Commit**

```bash
git add src/digitalmodel/solvers/orcaflex/orcaflex.py src/digitalmodel/hydrodynamics/aqwa/aqwa_router.py
git commit -m "feat(types): add type hints to OrcaFlex and AQWA solver entry points"
```

---

### Task 4: Clean Stale Root Files and curves.py Assessment

**Files:**
- Delete: `--version.cvg`, `--version.dat`, `--version.sta`
- Document: `naval_architecture/curves.py` (29,666 lines of data placeholders)

- [ ] **Step 1: Remove stale version artifacts**

```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel
git rm -- "--version.cvg" "--version.dat" "--version.sta"
```

- [ ] **Step 2: Add TODO comment to curves.py header**

The file is 29,666 lines of comment placeholders referencing DNV-RP-C205 and Warship standards — no classes, no functions. Add a header documenting this:

```python
"""Curve interpolation scaffolds — naval-architecture.

NOTE: This file contains 29K+ lines of placeholder entries referencing
standard curves (DNV-RP-C205, Warship-Naval-Submarines). Each entry
links to a source PDF figure and CSV data path. No executable code.

Future: Convert to a structured data format (YAML/JSON catalog) and
load curves programmatically. See GitHub issue for tracking.
"""
```

- [ ] **Step 3: Commit**

```bash
git add -- "--version.cvg" "--version.dat" "--version.sta" src/digitalmodel/naval_architecture/curves.py
git commit -m "chore: remove stale version artifacts, document curves.py as data placeholders"
```

---

### Task 5: Triage collect_ignore and TODOs

**Files:**
- Modify: `tests/conftest.py` (lines 9-43, collect_ignore list)

- [ ] **Step 1: Categorize collect_ignore entries**

Read the 26 entries in `tests/conftest.py` collect_ignore. For each:
- If the test file no longer exists → remove from ignore list
- If the test references a deleted module → remove both test and ignore entry
- If platform-specific (orcawave COM) → keep, add comment explaining why
- If fixable (missing import) → fix the import if simple

- [ ] **Step 2: Remove entries for deleted files**

10 entries reference "Deleted orcaflex-dashboard service files" — verify these test files still exist. If not, remove from collect_ignore.

- [ ] **Step 3: Run tests**

Run: `cd /mnt/local-analysis/workspace-hub/digitalmodel && uv run pytest tests/ -x -q --tb=short 2>&1 | tail -15`

- [ ] **Step 4: Commit**

```bash
git add tests/conftest.py
git commit -m "chore(tests): clean collect_ignore list, remove entries for deleted files"
```

---

### Task 6: Final Verification

- [ ] **Step 1: Run full test suite**

```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel
uv run pytest tests/ -q --tb=short 2>&1 | tail -15
```
Expected: 80%+ coverage maintained, no new failures

- [ ] **Step 2: Verify package builds**

```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel
uv run python -m build --sdist 2>&1 | tail -5
```
Expected: Successfully built sdist
