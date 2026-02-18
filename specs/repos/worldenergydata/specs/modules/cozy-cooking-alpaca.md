---
title: "WorldEnergyData File Structure Organization"
description: "Standardize module structure, consolidate tests, organize scripts"
version: "1.1"
module: "worldenergydata"
session:
  id: "cozy-cooking-alpaca"
  agent: "claude-opus-4-5"
  started: "2026-01-24"
status: "approved"
priority: "high"
complexity: "medium"
tags: ["refactor", "organization", "modules", "structure"]
review:
  required_iterations: 3
  current_iteration: 3
  status: "approved"
  reviewers:
    openai_codex:
      status: "approved"
      iteration: 3
      feedback: "All blocking issues resolved, shim strategy validated, implementation-ready"
    google_gemini:
      status: "approved"
      iteration: 3
      feedback: "Architecture production-ready, patterns consistent, phases properly sequenced"
---

# WorldEnergyData File Structure Organization Plan

## Executive Summary

Standardize the worldenergydata repository's 7 modules to follow a consistent structure pattern, consolidate fragmented test directories, and organize 50+ scattered scripts into their owning modules.

## Current State

| Component | Current | Issue |
|-----------|---------|-------|
| Modules | 7 modules with inconsistent structure | No standard template |
| Tests | 8+ directories (372 files) | Fragmented, unclear ownership |
| Scripts | 50+ files in scripts/ | Scattered, no module ownership |
| Specs | Mixed active/archived | Disorganized |

---

## Cross-Review Summary (Iteration 1)

### Codex Review: CHANGES_REQUESTED

**Critical Issues:**
1. **TC-1 (HIGH)**: No backward compatibility plan for imports - need shim modules
2. **TC-2 (HIGH)**: BSEE `_by_*`/`_from_*` rename breaks `engine.py` and cross-module imports
3. **TC-3 (MEDIUM)**: Rigid 4-directory template doesn't fit all modules
4. **TC-6 (HIGH)**: No `pyproject.toml` update plan

**Suggested:** Compatibility shims, deprecation warnings, phased rollout

### Gemini Review: CHANGES_REQUESTED

**Architectural Concerns:**
1. Missing cross-cutting concerns layer (`src/common/`)
2. Multiple CLI entry points violate orchestrator pattern
3. Inter-module dependency management undefined
4. No shared utilities layer

**Suggested:** Single CLI orchestrator, flexible layer requirements, `src/common/` for shared code

---

## Addressed Concerns

### A1: Flexible Module Template (TC-3)

**REQUIRED directories:**
- `__init__.py` - Module exports
- `data/` - Data access layer

**OPTIONAL directories (as needed):**
- `core/` - Core business logic
- `analysis/` - Analysis functions
- `reports/` - Report generation
- `utils/` - Module-specific utilities

### A2: Backward Compatibility (TC-1, TC-2)

**Deprecation Strategy:**
```python
# Old path shim: data/_by_api/__init__.py
import warnings
warnings.warn(
    "worldenergydata.bsee.data._by_api is deprecated. "
    "Use worldenergydata.bsee.data.loaders.api instead.",
    DeprecationWarning, stacklevel=2
)
from worldenergydata.bsee.data.loaders.api import *
```

**Timeline:** 2 minor versions before removal

### A3: Cross-Cutting Concerns Layer

**Add `src/worldenergydata/common/`:**
```
common/
├── __init__.py
├── logging.py          # Structured logging
├── config.py           # Environment-based config
├── exceptions.py       # Common exception hierarchy
└── validation/         # Shared validation schemas
```

### A4: Single CLI Orchestrator

**Replace per-module CLI with unified entry:**
```bash
uv run python -m worldenergydata bsee analyze --field "MC252"
uv run python -m worldenergydata marine-safety report --region "GOM"
```

**Structure:**
```
src/worldenergydata/
├── __main__.py         # CLI entry point
├── cli/
│   ├── __init__.py
│   ├── main.py         # Orchestrator
│   └── commands/       # Module subcommands
```

---

## Revised Phase Plan

### Phase 0: Pre-Migration (NEW)

**Tasks:**
- [ ] 0.1 Generate import dependency graph (`pydeps src/worldenergydata`)
- [ ] 0.2 Audit all `__all__` declarations
- [ ] 0.3 Create old-path → new-path mapping file
- [ ] 0.4 Update `pyproject.toml` package includes
- [ ] 0.5 Create migration branch

**Verification Gate:**
```bash
python -c "from worldenergydata import *"  # All imports resolve
```

### Phase 1: Foundation

**Tasks:**
- [ ] 1.1 Create `src/worldenergydata/common/` with logging, config, exceptions
- [ ] 1.2 Document flexible module template in `MODULE_TEMPLATE.md`
- [ ] 1.3 Create compliance checker script
- [ ] 1.4 Establish baseline metrics (test count, coverage)

### Phase 2: Test Consolidation

**Target Structure (hybrid approach):**
```
tests/
├── unit/
│   ├── bsee/           # Module grouping preserved
│   ├── fdas/
│   └── marine_safety/
├── integration/
│   └── modules/
├── e2e/
├── fixtures/
└── _archived/
    ├── legacy/
    └── validation_runs/  # Date-prefixed directories
```

**Tasks:**
- [ ] 2.1 Consolidate all archive folders → `_archived/`
- [ ] 2.2 Move `tests/modules/<mod>/` → `tests/unit/<mod>/`
- [ ] 2.3 Update `conftest.py` hierarchy
- [ ] 2.4 Fix test imports
- [ ] 2.5 Update pytest markers and CI config

### Phase 3: Scripts Consolidation

**Target Structure:**
```
scripts/
├── bsee/
├── fdas/
├── marine_safety/      # Already organized
├── hse/
├── tools/
└── _deprecated/
```

**Tasks:**
- [ ] 3.1 Create module script directories
- [ ] 3.2 Move scripts to owning modules
- [ ] 3.3 Update script imports to use module CLI
- [ ] 3.4 Archive deprecated scripts

### Phase 4: Module Restructure

**Order (low-risk first):**
1. HSE, Reporting (minimal modules)
2. FDAS, Marine Safety (medium complexity)
3. Well Production Dashboard
4. BSEE (highest complexity, most dependencies)

#### 4.1 BSEE Module (Final)

**Restructure with shims:**
```
modules/bsee/
├── data/
│   ├── loaders/
│   │   ├── api.py          # NEW
│   │   ├── block.py        # NEW
│   │   └── lease.py        # NEW
│   ├── sources/
│   │   ├── bin.py          # NEW
│   │   └── zip.py          # NEW
│   ├── _by_api/            # SHIM → loaders.api
│   ├── _by_block/          # SHIM → loaders.block
│   ├── _from_bin/          # SHIM → sources.bin
│   └── _from_zip/          # SHIM → sources.zip
├── core/                   # Extract from bsee.py
├── analysis/               # KEEP
├── reports/                # KEEP
└── _legacy/                # Consolidate
```

**Tasks:**
- [ ] 4.4.1 Create new structure with proper code
- [ ] 4.4.2 Create backward-compatible shim modules
- [ ] 4.4.3 Update `engine.py` imports (non-breaking)
- [ ] 4.4.4 Add deprecation warnings to old paths

### Phase 5: CLI Unification

**Tasks:**
- [ ] 5.1 Create `src/worldenergydata/cli/` orchestrator
- [ ] 5.2 Convert module CLIs to subcommands
- [ ] 5.3 Update `__main__.py` entry point
- [ ] 5.4 Update scripts to use unified CLI

### Phase 6: Validation

**Verification Gates:**
```bash
# Gate 1: All imports resolve
python -c "from worldenergydata import *"

# Gate 2: All tests pass
uv run pytest tests/ --tb=short

# Gate 3: No deprecation warnings in core
python -W error::DeprecationWarning -c "from worldenergydata.modules import bsee"

# Gate 4: Coverage maintained
uv run pytest --cov=src/worldenergydata --cov-fail-under=80
```

**Tasks:**
- [ ] 6.1 Run all verification gates
- [ ] 6.2 Compare metrics to baseline
- [ ] 6.3 Update documentation
- [ ] 6.4 Create migration guide for users

---

## Risk Mitigation (Updated)

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking imports | High | High | Shim modules with deprecation warnings |
| Circular imports | Medium | High | Dependency graph analysis in Phase 0 |
| Lost test coverage | Medium | Medium | Track metrics before/after |
| Git history loss | Low | Medium | Use `git mv` exclusively |
| CI/CD failures | Medium | High | Update GitHub Actions in Phase 2 |
| Developer confusion | Low | Medium | Migration guide + deprecation period |

---

## Success Criteria

- [ ] All 7 modules follow flexible template
- [ ] Tests consolidated to 3 categories (unit/integration/e2e)
- [ ] Scripts owned by modules
- [ ] Single CLI orchestrator
- [ ] `src/common/` for cross-cutting concerns
- [ ] No broken imports (shims in place)
- [ ] Test coverage maintained ≥80%
- [ ] 2-version deprecation period for old paths

---

## Review Iteration Log

| Iteration | Reviewer | Status | Key Feedback |
|-----------|----------|--------|--------------|
| 1 | OpenAI Codex | Changes Requested | Backward compat, flexible template, phased migration |
| 1 | Google Gemini | Changes Requested | Cross-cutting layer, single CLI, inter-module deps |
| 2 | OpenAI Codex | Approved | Shim strategy sound, deprecation timeline appropriate |
| 2 | Google Gemini | Approved | Common layer adequate, CLI aligned, hybrid tests scalable |
| 3 | OpenAI Codex | Approved | All blockers resolved, implementation-ready |
| 3 | Google Gemini | Approved | Architecture production-ready, phases properly sequenced |

## Final Recommendations (from reviews)

### Must Address Before Implementation:
- [ ] Add `src/worldenergydata/common/constants.py` for unit conversions
- [ ] Add data flow diagram to documentation

### Should Address During Phase 1:
- [ ] Define exception hierarchy in `common/exceptions.py`
- [ ] Add `common/types.py` for shared type definitions
- [ ] Add `migration_manifest.json` for automated tooling
- [ ] Add CI deprecation warning count metric
