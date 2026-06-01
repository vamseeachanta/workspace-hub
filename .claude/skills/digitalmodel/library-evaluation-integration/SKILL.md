---
name: library-evaluation-integration
description: >
  Create evaluation scripts and integration tests for Python scientific libraries
  in the digitalmodel package. Follows the established pattern from fluids, ht,
  meshio, sectionproperties, and pygmt evaluations.
tags: [digitalmodel, evaluation, integration-test, scientific-python]
triggers:
  - evaluate a library in digitalmodel
  - create integration tests for a library
  - add a new library evaluation script
---

# Library Evaluation + Integration Test Pattern

## Context
The digitalmodel repo (a sibling checkout, e.g. `$WORKROOT/digitalmodel` where `$WORKROOT` holds your repo checkouts) has a standard
pattern for evaluating and testing scientific Python library integrations:

- **Evaluation script**: `scripts/integrations/<lib>_evaluation.py`
- **Integration tests**: `tests/test_<lib>_integration.py`

## Workflow (4 phases)

### Phase 1: API Discovery (CRITICAL — don't skip)
Before writing ANY code, probe the actual installed API:

```bash
uv run python -c "import <lib>; print(<lib>.__version__)"
uv run python -c "import <lib>.<submodule>; print(dir(<lib>.<submodule>))"
uv run python -c "help(<lib>.<submodule>.<function>)"
```

**Why**: Library APIs change between versions. The ht.insulation module completely
changed its API surface in v1.2.0 (no more R_value functions, now k_material/nearest_material).
Always verify what's actually importable before writing imports.

### Phase 2: Compute Reference Values
Run each function with representative inputs and record the actual output:

```bash
uv run python -c "
from <lib>.<mod> import <func>
result = <func>(arg1, arg2)
print(f'result = {result}')
"
```

**Why**: Setting test assertions from textbook expectations can fail. Example: a subsea
pipeline U-value calculated to 0.29 W/m²/K which is realistic but was below the initial
bound of 0.5. Always compute first, then set bounds around the computed value.

### Phase 3: Test Edge Cases Interactively
Different functions handle edge cases differently — test before asserting:

```bash
# Test Re=0, Pr=0, T=T2, empty inputs, etc.
uv run python -c "
try:
    result = func(edge_case_args)
    print(f'Returns: {result}')
except Exception as e:
    print(f'Raises: {type(e).__name__}: {e}')
"
```

**Pitfall discovered**: In ht library, `Nu_conv_internal(Re=0)` raises ValueError
but `Nu_cylinder_Churchill_Bernstein(Re=0)` returns 0.3. Can't assume uniform
edge-case behavior across submodules.

### Phase 4: Write Files

#### Evaluation Script Structure
```python
#!/usr/bin/env python3
"""<Library Name> — Evaluation Script.

Demonstrates <lib> integration for offshore/engineering workflows.
Library: <url> (v<version>, <license>)
"""

import <lib>
from <lib>.<submod> import <func>

def demo_capability_1():
    """Description with engineering context."""
    print("=" * 65)
    print("1. CAPABILITY NAME")
    print("=" * 65)
    # Scenario description, calculations, formatted output
    print()

# ... more demo functions ...

def main():
    print("*" * 65)
    print(f"  <Library> — Evaluation Script")
    print(f"  Version: {<lib>.__version__}")
    print("*" * 65)
    demo_capability_1()
    # ...
    print("  Evaluation complete.")

if __name__ == "__main__":
    main()
```

#### Integration Test Structure
```python
"""<Library> integration tests.

Library: <url> (v<version>, <license>)
Tests: import checks, known-value verification, edge cases, physics sanity.
All values in SI units.
"""
import math
import pytest

<lib> = pytest.importorskip("<lib>")
from <lib>.<submod> import <func>

class TestImportAndVersion:
    def test_import(self): ...
    def test_version(self): ...
    def test_submodules_importable(self): ...

class TestCapability1:
    def test_known_value(self):
        """Compare against pre-computed reference value."""
        result = func(args)
        assert result == pytest.approx(REFERENCE, rel=1e-2)

    def test_monotonicity(self):
        """Physical quantity increases/decreases with parameter."""

    def test_edge_case(self):
        """Re=0, T=0, empty input, etc."""

    def test_physics_sanity(self):
        """Nu > 0, 0 <= eff <= 1, R > 0, etc."""
```

## Test Categories (aim for 15+ tests)
1. **Import/version** (2-3 tests): importorskip, version check, submodules
2. **Known-value verification** (1 per capability): pre-computed reference values
3. **Monotonicity/physics** (1-2 per capability): Nu increases with Re, etc.
4. **Edge cases** (2-3 total): zero inputs, extreme values, domain errors
5. **Unit consistency** (1-2): dimensional analysis checks
6. **Integration/end-to-end** (1-2): combine multiple functions into realistic workflow

## Pitfalls
- **Always use `uv run`** — never bare `python3` (project policy)
- **pytest.approx with rel tolerance** — use rel=1e-2 for engineering correlations,
  rel=1e-6 for analytical formulas, abs for zero-valued results
- **Don't guess assertion bounds** — compute the value first, then verify it makes
  physical sense, THEN set the test bounds around it
- **API drift** — when user says "check what's available", always probe with dir()
  and help() before writing imports
- **Randomized test ordering** — the repo uses pytest-randomly; tests must be independent
