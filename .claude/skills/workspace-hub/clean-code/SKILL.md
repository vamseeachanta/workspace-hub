---
name: clean-code
version: "1.0.0"
category: workspace
description: "Clean code enforcement for workspace-hub Python repos: file/function size limits, God Object detection, naming rules, dead code removal, and refactor decision guidance. Consult before writing new modules or accepting large files."
invocation: /clean-code
applies-to: [claude, codex, gemini]
capabilities: []
requires: []
see_also: [repo-structure, file-taxonomy, infrastructure-layout]
---

# Clean Code — Enforcement Rules for Python Repos

Consult this skill before writing new modules or when reviewing existing code for refactor
candidacy. For file placement rules see `/repo-structure`. For output file paths see `/file-taxonomy`.

---

## Hard Limits (Zero-Tolerance)

| Metric | Hard Limit | Target | Action When Exceeded |
|--------|-----------|--------|----------------------|
| File length | **400 lines** | 200 lines | Split by responsibility |
| Function length | **50 lines** | 20–30 lines | Extract helpers |
| Class public methods | **10 methods** | 5–7 methods | Extract sub-classes or use composition |
| Nesting depth | **4 levels** | 2 levels | Extract guard clauses or sub-functions |
| Import count per file | **20 imports** | 10–12 imports | Sign of a God Object — split the file |

**Exception**: Legacy solver files (e.g., `wellpath3D.py`, `cathodic_protection.py`) that are
low-churn and have full test coverage may remain until a dedicated refactor WRK is approved.
Document the exception with a `# noqa: clean-code` comment at the top of the file.

---

## Quick Scan Commands

Run these before reviewing or merging code:

```bash
# Find files exceeding 400-line hard limit
find src/ -name "*.py" -exec wc -l {} + | awk '$1 > 400 {print $1, $2}' | sort -rn | head -20

# Find functions exceeding 50 lines (approximate — counts def blocks)
grep -n "^    def \|^def " src/**/*.py | awk -F: '{print $1, $2}' | head -30

# Oversized files by severity
echo "=== CRITICAL (>1000 lines) ===" && find src/ -name "*.py" -exec wc -l {} + | awk '$1>1000{print}' | sort -rn
echo "=== HIGH (400-1000 lines) ===" && find src/ -name "*.py" -exec wc -l {} + | awk '$1>400 && $1<=1000{print}' | sort -rn

# Dead code: files named *_unused.py or *_old.py
find src/ \( -name "*_unused.py" -o -name "*_old.py" -o -name "*_bak.py" \) | head -20

# Duplicate class names (possible God Object fragmentation)
grep -r "^class " src/ | sed 's/.*class //' | sed 's/[:(].*//' | sort | uniq -d
```

---

## File Size Decision Tree

When a file exceeds 400 lines:

```
Is it a God Object (does many unrelated things)?
  YES → Split by responsibility (see Decomposition Patterns below)
  NO  → Is it a report generator / long output formatter?
         YES → Extract: data-gathering logic → separate module
                        formatting/rendering → reporter.py / formatter.py
         NO  → Is it a data model / schema file?
                YES → Acceptable if types are coherent; add __all__
                NO  → Is it a legacy solver (low churn, full tests)?
                       YES → Add # noqa: clean-code; open WRK for future split
                       NO  → Split now
```

---

## Decomposition Patterns

### Pattern 1: Responsibility Split (most common)

```
# BEFORE: one 1200-line file
src/digital_model/bsee/analysis.py  ← does: fetch + parse + validate + report

# AFTER: four focused files
src/digital_model/bsee/
  fetcher.py        ← HTTP, pagination, rate-limiting (≤150L)
  parser.py         ← raw→structured data transform (≤200L)
  validator.py      ← business rules, schema checks (≤150L)
  reporter.py       ← HTML/CSV/JSON report generation (≤200L)
  __init__.py       ← re-exports public API (≤30L)
```

### Pattern 2: Extract Report Generator

Report generation always violates SRP when mixed with domain logic.

```python
# BEFORE: domain class with 300-line report method
class WellDataAnalyzer:
    def generate_report(self, ...):  # 300 lines of HTML templating
        ...

# AFTER: separate reporter
class WellDataAnalyzer:
    def analyze(self, ...) -> AnalysisResult:  # pure domain logic
        ...

class WellDataReporter:               # src/<pkg>/<domain>/reporter.py
    def generate(self, result: AnalysisResult) -> str:
        ...
```

### Pattern 3: Extract Constants and Config

Inlined magic numbers bloat files and hide domain knowledge.

```python
# BEFORE
def check_wall_thickness(t, D, SMYS):
    if t / D < 0.01:    # magic ratio
        ...
    safety_factor = 1.25  # magic number

# AFTER — constants.py (≤50 lines)
WALL_RATIO_MIN = 0.01        # API 5L minimum D/t ratio
DESIGN_SAFETY_FACTOR = 1.25  # ASME B31.4 Table 403.2.1

# domain file uses named constants
from .constants import WALL_RATIO_MIN, DESIGN_SAFETY_FACTOR
```

### Pattern 4: Extract Sub-Package for Large Domains

When a domain grows beyond 3–4 files, promote to sub-package:

```
# BEFORE
src/digitalmodel/structural/
  pipe_capacity.py   (1476 lines)  ← God Object

# AFTER
src/digitalmodel/structural/pipe_capacity/
  __init__.py          ← public API (re-exports)
  models.py            ← dataclasses, enums
  burst.py             ← burst pressure checks
  collapse.py          ← external pressure / collapse
  bending.py           ← combined bending checks
  api_5l.py            ← API 5L specific rules
  dnv_st_f101.py       ← DNV-ST-F101 specific rules
```

---

## Naming Rules (Enforcement)

| Item | Rule | Wrong | Correct |
|------|------|-------|---------|
| Python files | `snake_case.py` | `PipeCapacity.py` | `pipe_capacity.py` |
| Python dirs | `snake_case/` | `orcaflex-dashboard/` | `orcaflex_dashboard/` |
| Classes | `PascalCase` | `pipe_capacity` | `PipeCapacity` |
| Functions | `snake_case` | `calcWallThick` | `calc_wall_thickness` |
| Constants | `SCREAMING_SNAKE` | `safetyFactor` | `SAFETY_FACTOR` |
| Private helpers | `_snake_case` | `__helper` | `_helper` |
| Test files | `test_<module>.py` | `PipeCapacityTest.py` | `test_pipe_capacity.py` |

**Quick check for PascalCase file names** (violation):
```bash
find src/ -name "*.py" | grep -E '/[A-Z][a-zA-Z]+\.py$'
```

---

## Dead Code Identification and Removal

Dead code is any code that is never called, imported, or referenced.

```bash
# Find files that nothing imports (potential dead modules)
# Run from repo root:
python3 -c "
import ast, os, sys
from pathlib import Path

src = Path('src')
all_files = list(src.rglob('*.py'))
imported = set()

for f in all_files:
    try:
        tree = ast.parse(f.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if hasattr(node, 'module') and node.module:
                    imported.add(node.module.split('.')[-1])
    except:
        pass

for f in all_files:
    stem = f.stem
    if stem not in imported and stem != '__init__':
        print(f)
"
```

Common dead code patterns to delete:
- `*_unused.py` — explicitly named dead code
- `*_old.py`, `*_bak.py`, `*.py.bak` — backup files (use git, not backup files)
- Files with only `pass` in every function
- Commented-out code blocks >5 lines (use git history instead)
- `__all__ = []` with no exports (likely orphaned)

---

## God Object Detection

A "God Object" knows or does too much. Signs:

1. File >600 lines with >8 classes or >15 functions
2. Class that imports from 5+ different domain modules
3. Function >50 lines with >3 different concerns
4. File name that ends in `_utils.py`, `_helpers.py`, `_common.py` with >200 lines

```bash
# Files with many class definitions (God Object candidates)
grep -l "^class " src/**/*.py | xargs -I{} bash -c \
  'count=$(grep -c "^class " {}); [ $count -gt 3 ] && echo "$count classes: {}"' | sort -rn

# Files with many function definitions
grep -l "^def \|^    def " src/**/*.py | xargs -I{} bash -c \
  'count=$(grep -cE "^def |^    def " {}); [ $count -gt 15 ] && echo "$count funcs: {}"' | sort -rn
```

---

## Refactor Prioritization

When 300+ files exceed limits (as in digitalmodel/worldenergydata), use this triage:

| Priority | Criteria | Action |
|----------|---------|--------|
| **P1 — Refactor now** | File has active development (git log shows <60 days) AND >600 lines | Open WRK, split within 2 sprints |
| **P2 — Schedule** | File >400 lines, changes every 1–3 months | Add to backlog, refactor in quarterly sprint |
| **P3 — Low priority** | File >400 lines but <5 commits ever AND full tests exist | Add `# noqa: clean-code — legacy solver` comment; defer |
| **P4 — Delete** | File is unreachable / all functions commented out | `git rm` immediately |

### Top P1 Candidates (2026-02-25 audit)

**digitalmodel** (active development + oversized):

| File | Lines | Domain | Split Strategy |
|------|-------|--------|----------------|
| `hydrodynamics/diffraction/benchmark_plotter.py` | 2700 | Hydro | Extract: data-fetcher, plot-generator, report-writer |
| `hydrodynamics/diffraction/report_generator.py` | 2034 | Hydro | Extract: section renderers (one file per report section) |
| `solvers/orcaflex/orcaflex_model_components.py` | 1905 | Solvers | Extract: line-types, vessel, environment, post-process |
| `marine_ops/marine_analysis/visualization/integration_charts.py` | 1439 | Marine | Extract by chart type |

**worldenergydata** (active development + oversized):

| File | Lines | Domain | Split Strategy |
|------|-------|--------|----------------|
| `cost/data_collection/public_dataset.py` | 1643 | Cost | Extract: fetcher, parser, normalizer, schema |
| `safety_analysis/taxonomy/activity_taxonomy.py` | 1550 | Safety | Extract: taxonomy definitions, lookup, classifier |
| `well_production_dashboard/field_aggregation.py` | 1131 | Dashboard | Extract: query, aggregate, format |
| `well_production_dashboard/well_production.py` | 1090 | Dashboard | Extract: models, fetcher, renderer |

---

## Pre-commit Integration

Add to `.pre-commit-config.yaml` to catch new violations before they land:

```yaml
repos:
  - repo: local
    hooks:
      - id: file-size-check
        name: Python file size check (400 line limit)
        language: system
        entry: bash -c 'find src/ -name "*.py" -exec wc -l {} + | awk "$1 > 400 {print $1, $2; found=1} END {exit found+0}" | sort -rn'
        pass_filenames: false
        types: [python]

      - id: validate-file-placement
        name: Validate file placement
        language: system
        entry: bash scripts/operations/validate-file-placement.sh
        pass_filenames: false
```

---

## Refactor Safety Protocol

Before splitting any file:

1. **Confirm tests exist** — `pytest tests/<domain>/ -q` must pass before and after
2. **Check all callers** — `grep -r "from digitalmodel.<module> import" src/ tests/`
3. **Create backward-compat re-export** in the old location for one release cycle
4. **Update one caller at a time** — don't batch all imports in one commit
5. **Run full test suite after each file move**

```python
# backward-compat shim (old_module.py) — remove after 1 release
"""Deprecated: import from new_module instead."""
import warnings
warnings.warn(
    "old_module is deprecated; use new_module",
    DeprecationWarning, stacklevel=2
)
from .new_location.new_module import *  # noqa: F401,F403
```

---

## See Also

- `/repo-structure` — file locations, tests/ layout, .gitignore
- `/file-taxonomy` — where to put reports, results, data
- `/infrastructure-layout` — canonical 5-domain layout for the infrastructure/ package
- `.claude/rules/coding-style.md` — naming conventions (canonical source)
- `scripts/operations/validate-file-placement.sh` — automated structural checks
