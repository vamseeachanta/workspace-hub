# Test Error Triage Report — 2026-04-02

## Summary

| Scope | Collected | Errors | Skipped |
|-------|-----------|--------|---------|
| digitalmodel/tests/ | 12,062 | 1 (INTERNALERROR) | 15 |
| workspace-hub/tests/ | 2,120 | 25 | 0 |
| **Total** | **14,182** | **26** | **15** |

> **Context:** The original #1647/#1665 estimate of 149 collection errors has been
> resolved down to 26 by prior dependency additions (pint, plotly, deepdiff,
> factory-boy, loguru were added to `digitalmodel/pyproject.toml` main deps in an
> earlier session). This report triages the remaining 26 errors.

---

## digitalmodel/tests/ — 1 Error

### INTERNALERROR: pytest-asyncio / hypothesis incompatibility

- **Root cause:** `pytest-asyncio==0.21.1` is incompatible with `hypothesis>=6.151`.
  The `pytest_collection_modifyitems` hook in pytest-asyncio calls
  `function.hypothesis.inner_test` on functions that don't have a `hypothesis`
  attribute, raising `AttributeError`.
- **Fix:** Upgrade `pytest-asyncio` to `>=0.23.0` (fixes the hypothesis interaction).
  Currently pinned as `pytest-asyncio==0.21.1` in `digitalmodel/pyproject.toml`
  main dependencies.
- **Impact:** Intermittent — some runs show 1 error, some show 3, depending on
  random seed and test ordering.
- **Priority:** MEDIUM — does not prevent test execution, but causes noisy
  INTERNALERROR traceback after collection completes.

---

## workspace-hub/tests/ — 25 Errors by Category

| Category | Count | Files | Root Cause | Fix Needed |
|----------|-------|-------|------------|------------|
| Missing dep: `pdfplumber` | 6 | tests/data/doc_intelligence/test_*.py | Module not installed | `uv add pdfplumber` or add to `[project.optional-dependencies]` |
| Broken import: `data.pipeline` | 7 | tests/data/pipeline/test_*.py | Import path `data.pipeline` doesn't resolve — no `data/` package on sys.path | Add conftest.py with sys.path fix, or restructure imports |
| Missing dep: `ee` (earthengine-api) | 1 | tests/gis/test_google_earth_engine.py | Google Earth Engine SDK not installed | Add `earthengine-api` to optional deps (requires auth) |
| Missing dep: `geopandas` | 1 | tests/gis/test_python_gis_ecosystem.py | Module not installed | `uv add geopandas` or add to optional deps |
| SyntaxError: unterminated string | 3 | tests/promoted/naval-architecture/test_*.py | Multi-line strings not properly closed (line 12-13) | Fix string literals in test files |
| Missing module: `workspace_hub` | 1 | tests/unit/test_circle.py | No `workspace_hub` package installed/importable | Check if package exists, fix import, or skip |
| Missing file: `infer-category.py` | 1 | tests/unit/test_infer_category.py | `scripts/work-queue/infer-category.py` doesn't exist | Create the script or remove/skip the test |
| Missing work-queue modules | 5 | tests/work-queue/test_*.py | `run_log`, `gate_check`, `generate_transition_table`, `urgency_score` not on path | These are local scripts — add conftest.py that puts `scripts/work-queue/` on sys.path |

---

## Top 5 Worst Packages by Error Count

| # | Package/Directory | Error Count | Error Type |
|---|-------------------|-------------|------------|
| 1 | tests/data/pipeline/ | 7 | Broken import path |
| 2 | tests/data/doc_intelligence/ | 6 | Missing `pdfplumber` |
| 3 | tests/work-queue/ | 5 | Missing local modules on sys.path |
| 4 | tests/promoted/naval-architecture/ | 3 | SyntaxError in test files |
| 5 | tests/gis/ | 2 | Missing `ee` and `geopandas` |

---

## Recommended Fix Order

1. **SyntaxErrors in promoted/naval-architecture** (3 errors) — Quick fix, just close
   the string literals. These are broken test files that can never work.

2. **work-queue sys.path** (5 errors) — Add a `conftest.py` in `tests/work-queue/`
   that adds `scripts/work-queue/` to `sys.path`, or verify the scripts exist at the
   expected paths.

3. **data.pipeline imports** (7 errors) — The `data/pipeline/` package import scheme
   needs a conftest.py or restructured imports. Check if `scripts/data/pipeline/` is
   the intended source.

4. **Missing pip deps** (8 errors: pdfplumber×6, ee×1, geopandas×1) — Add to
   `pyproject.toml` under optional dependency groups:
   - `[project.optional-dependencies] docling` → pdfplumber
   - `[project.optional-dependencies] gis` → earthengine-api, geopandas

5. **pytest-asyncio upgrade** (1 INTERNALERROR) — Upgrade from 0.21.1 to >=0.23.0
   in digitalmodel/pyproject.toml.

6. **workspace_hub module + infer-category.py** (2 errors) — Investigate whether
   these are stale tests referencing removed code.

---

## Detailed Error List

### 1. Missing `pdfplumber` (6 files)
```
tests/data/doc_intelligence/test_docx_parser.py
tests/data/doc_intelligence/test_html_parser.py
tests/data/doc_intelligence/test_integration.py
tests/data/doc_intelligence/test_orchestrator.py
tests/data/doc_intelligence/test_pdf_parser.py
tests/data/doc_intelligence/test_xlsx_parser.py
```

### 2. Broken `data.pipeline` import (7 files)
```
tests/data/pipeline/test_base.py
tests/data/pipeline/test_bsee_wells.py
tests/data/pipeline/test_eia_production.py
tests/data/pipeline/test_manifest.py
tests/data/pipeline/test_pipeline.py
tests/data/pipeline/test_state.py
tests/data/pipeline/test_yfinance_prices.py
```

### 3. Missing `ee` (earthengine-api) (1 file)
```
tests/gis/test_google_earth_engine.py
```

### 4. Missing `geopandas` (1 file)
```
tests/gis/test_python_gis_ecosystem.py
```

### 5. SyntaxError — unterminated strings (3 files)
```
tests/promoted/naval-architecture/test_fluiddynamicdraghoerner1965_examples.py  (line 12)
tests/promoted/naval-architecture/test_introductiontonavalarchitecturecomstock1942_examples.py  (line 13)
tests/promoted/naval-architecture/test_theoreticalnavalarchitectureattwood1899_examples.py  (line 12)
```

### 6. Missing `workspace_hub` module (1 file)
```
tests/unit/test_circle.py
```

### 7. Missing file `scripts/work-queue/infer-category.py` (1 file)
```
tests/unit/test_infer_category.py
```

### 8. Missing work-queue modules (5 files)
```
tests/work-queue/test_engine_integration.py  — needs: run_log
tests/work-queue/test_run_log.py             — needs: run_log
tests/work-queue/test_stage_lifecycle.py     — needs: gate_check
tests/work-queue/test_transition_table.py    — needs: generate_transition_table
tests/work-queue/test_urgency_score.py       — needs: urgency_score
```
