---
name: repo-architecture-analysis
description: Scan a Python repo's package structure, count classes/functions, classify module maturity (PRODUCTION/DEVELOPMENT/SKELETON/GAP), and generate architecture reports with Mermaid diagrams. Use when asked to analyze codebase structure, find untested packages, or assess module maturity.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [architecture, package-analysis, maturity-matrix, code-structure, TDD]
    related_skills: [codebase-inspection, github-issues]
---

# Repo Architecture Analysis & Module Maturity Classification

Scan Python repositories to discover packages, count classes/functions, classify maturity levels, and generate markdown/JSON reports.

## When to Use

- User asks "what packages does this repo have?"
- User wants to know which modules lack tests
- User asks for a module maturity or readiness matrix
- User wants an architecture overview with diagrams
- Before prioritizing test coverage work

## Three Scripts (workspace-hub)

1. `scripts/analysis/repo_architecture_scanner.py` — Basic package discovery, counting, Mermaid structure diagrams
2. `scripts/analysis/architecture-scanner.py` — **Enhanced** scanner with LOC, public API surface, import dependency graph, YAML output (#1604)
3. `scripts/analysis/module_status_matrix.py` — Maturity classification (PRODUCTION/DEVELOPMENT/SKELETON/GAP) (#1567)

## Running

```bash
# Enhanced architecture scan with API surface + dependency graph (preferred)
uv run python scripts/analysis/architecture-scanner.py [REPO_PATH] [-o OUTPUT_DIR]
# Outputs: docs/architecture/api-surface-map.md + .yaml

# With collision detection (added #1627)
uv run python scripts/analysis/architecture-scanner.py --detect-collisions
# Appends collision report to api-surface-map.md, prints top-20 to stdout

# Basic architecture scan
uv run scripts/analysis/repo_architecture_scanner.py [REPO_PATH] [-o OUTPUT_DIR]

# Module status matrix (with LOC-weighted scoring + trend tracking, #1629)
uv run scripts/analysis/module_status_matrix.py [REPO_PATH] [-o OUTPUT_DIR]
# Defaults to docs/reports/ — use `-o docs/architecture` for canonical location
# Outputs: module-status-matrix.md + .json (JSON includes quality_score for trend tracking)

# All default to digitalmodel/ if no path given
```

## Enhanced Scanner Features (architecture-scanner.py)

The enhanced scanner adds capabilities beyond the basic one:
- **LOC counts** per package (non-blank lines)
- **Public API surface** detection: classes/functions not prefixed with `_`
- **Import dependency graph**: scans for inter-package imports (absolute via namespace + relative)
- **YAML report** output alongside markdown
- **Mermaid dependency graph** (edges between packages, not just tree structure)
- **Cross-package API name collision detection** (`--detect-collisions` flag, #1627): builds reverse index of symbol→packages, flags symbols exported by 2+ packages (179 collisions found across 31 packages)
- Functions: `discover_packages()`, `build_dependency_graph()`, `build_reverse_index()`, `detect_collisions()`, `generate_collision_report()`, `generate_yaml_report()`, `generate_markdown()`, `scan_repo()`

## Module Status Matrix Scoring (module_status_matrix.py)

Added in #1629 — LOC-weighted quality scoring and trend tracking:
- **Quality score**: `test_count × file_count / LOC × 100` — higher = better tested per LOC
- **Test-to-source ratio**: `test_count / file_count`
- **Trend tracking**: compares current quality_score to previous JSON snapshot (↑↓→/NEW/—)
- Previous snapshot auto-loaded from existing `module-status-matrix.json` before overwrite
- Functions: `compute_quality_score()`, `compute_test_source_ratio()`, `compute_trend()`
- JSON output now includes `loc`, `quality_score`, `test_source_ratio` per package for future trend comparisons

## Maturity Classification Rules

| Status | Criteria |
|--------|----------|
| PRODUCTION | >5 test files AND >3 source files AND >50% files have docstrings |
| DEVELOPMENT | has source files AND ≥1 test files AND not all files tiny (<20 lines) |
| SKELETON | source files but 0 test files, OR all files <20 non-blank lines (even with tests) |
| GAP | directory exists but only `__init__.py` |

**Priority order:** GAP (only __init__.py) → PRODUCTION (>5 tests, >3 files, >50% docstrings) → DEVELOPMENT (≥1 test, not all files tiny) → SKELETON (everything else — 0 tests, or all files tiny).

## Key Pitfalls (Discovered Through Iteration)

### 1. `.egg-info` directories break namespace detection
The src-layout scanner looks for a single child directory under `src/` to detect namespace packages. `.egg-info` dirs count as children and break this heuristic.

**Fix:** Always filter out `.egg-info` and `.dist-info`:
```python
subdirs = [d for d in src_dir.iterdir()
           if d.is_dir()
           and not d.name.startswith((".", "_"))
           and not d.name.endswith((".egg-info", ".dist-info"))]
```

### 2. `.venv` pollutes entry point discovery
`rglob("__main__.py")` will find hundreds of `__main__.py` files inside `.venv/lib/python3.x/site-packages/`. Same for `scripts/` rglob hitting deep legacy trees.

**Fix:** Skip known directories:
```python
skip_dirs = {".venv", "venv", "node_modules", ".git", "__pycache__", ".tox", ".nox"}
def _skip_venv(path):
    return any(part in skip_dirs for part in path.parts)
```

### 3. src-layout namespace detection
For repos using `src/mypackage/` layout with a single namespace package, the scanner must detect this pattern and drill one level deeper to find the real sub-packages.

**Pattern:** If `src/` has exactly 1 non-hidden, non-egg-info child with `__init__.py`, treat it as the namespace root and scan its children.

### 4. Entry point scripts/ scanning depth
Use `glob("*.py")` (top-level only) instead of `rglob("*.py")` for scripts/ to avoid listing hundreds of legacy/deep scripts.

### 5. Use relative paths in reports
Call `path.relative_to(repo_path)` for cleaner output instead of absolute paths.

## TDD Structure

Tests for all scripts live in `tests/analysis/`:
- `test_architecture_scanner.py` — 19 tests (discovery, metrics, public API, dependency graph, YAML, markdown, e2e)
- `test_collision_detection.py` — 14 tests (reverse index, collision detection, dedup, report formatting, top-N, case sensitivity)
- `test_repo_architecture_scanner.py` — 17 tests (package discovery, counting, markdown, entry points)
- `test_module_status_matrix.py` — 18 tests (scanning, classification, docstring%, key classes, markdown, JSON)
- `test_weighted_scoring.py` — 13 tests (quality score, test/source ratio, trend comparison, edge cases)

All use `tmp_path` fixtures with mock repo structures to test each classification branch.

### Hyphenated filenames need importlib (not sys.path.insert)

`architecture-scanner.py` has a hyphen, making it non-importable via normal Python import. Tests must use:

```python
import importlib.util
_script_path = Path(__file__).resolve().parents[2] / "scripts" / "analysis" / "architecture-scanner.py"
_spec = importlib.util.spec_from_file_location("architecture_scanner", _script_path)
architecture_scanner = importlib.util.module_from_spec(_spec)
sys.modules["architecture_scanner"] = architecture_scanner
_spec.loader.exec_module(architecture_scanner)
```

Then test functions can `from architecture_scanner import discover_packages` normally.

### 6. Concurrent agent file conflicts
When running alongside other agents (Codex, Gemini), your files may get overwritten mid-session. **Commit immediately** after tests pass — don't leave uncommitted work sitting. If you hit `index.lock`, run `rm -f .git/index.lock` and retry.

### 7. scan_packages takes two arguments: src_dir and tests_dir
The actual working signature is `scan_packages(src_dir: Path, tests_dir: Path)` — this is more flexible than a single repo_path since it decouples source and test locations. The CLI flags `--src-dir` and `--tests-dir` map to these. The prior single-arg approach was less testable.

### 8. Test fixture for SKELETON vs GAP distinction
GAP = only `__init__.py` (no real source files). SKELETON = has source files but 0 tests. You do NOT need files >20 lines for DEVELOPMENT — the "all tiny" check only applies when combined with 0 tests. Keep fixture files small; the classification handles it correctly.

### 9. Packages without `__init__.py` are invisible — fix by adding __init__.py
If a directory lacks `__init__.py`, the scanner skips it. Fixed in #1626: `data_models/` got `__init__.py` → scanner now reports 31 packages. When a package is missing, create an `__init__.py` with a module docstring. Commit goes to the **digitalmodel repo** (not workspace-hub — see pitfall #12).

### 10. Module status matrix summary format
The enhanced output includes a bold summary line at the top: `**X/N PRODUCTION, Y/N DEVELOPMENT, Z/N SKELETON, W/N GAP**`. This format was added to meet issue #1567 acceptance criteria.

### 12. digitalmodel/ is a separate git repo inside workspace-hub
`digitalmodel/` is in workspace-hub's `.gitignore` — it's a separate repo (`github.com/vamseeachanta/digitalmodel.git`) cloned inside. Files under `digitalmodel/src/` must be committed in the digitalmodel repo (`cd digitalmodel && git add ... && git commit`), while `scripts/analysis/`, `tests/analysis/`, `docs/architecture/` are committed in workspace-hub. Before pushing either, stash unstaged changes from other terminals: `git stash && git pull origin main --rebase && git stash pop && git push`.

### 13. Module status matrix output path discrepancy
The script defaults to `docs/reports/` but the canonical location used by other tools is `docs/architecture/`. Run with `-o docs/architecture` to update the canonical copy. Both locations exist and should be kept in sync.

### 11. Dependency graph only includes inter-package edges
The `build_dependency_graph()` function detects the namespace package name (e.g. `digitalmodel`) and only tracks imports between known sibling packages. Stdlib and third-party imports are excluded. It matches both absolute (`from digitalmodel.pkg`) and relative (`from .pkg`) import patterns.

## Test Fixture Pattern for src-layout

```python
@pytest.fixture
def sample_repo(tmp_path):
    src = tmp_path / "src" / "mypackage"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text("")  # CRITICAL: must exist for namespace detection
    
    alpha = src / "alpha"
    alpha.mkdir()
    (alpha / "__init__.py").write_text('__all__ = ["Thing"]')
    (alpha / "engine.py").write_text('class Thing:\n    pass\n')
    
    tests_dir = tmp_path / "tests" / "alpha"
    tests_dir.mkdir(parents=True)
    (tests_dir / "test_engine.py").write_text("def test_thing(): pass\n")
    
    return tmp_path
```

**Critical:** The namespace package directory (`src/mypackage/`) MUST have `__init__.py` or it won't be detected as a namespace package.
