# Plan: WRK-617 — digitalmodel.ansys domain

## Context

ANSYS FEA assets exist in /mnt/ace but are inaccessible programmatically. WRK-617 creates
`src/digitalmodel/ansys/` — a new domain that can (a) parse APDL `.inp` files for material
and section data, (b) read IronPython `.wbjn` journal metadata, and (c) read parametric design
point logs (`DesignPointLog.csv`). This enables WRK-615 (thin-wall FEA automation) and future
AI-agent-driven FEA workflows.

## Critical Files

### Existing patterns to follow
- `digitalmodel/src/digitalmodel/well/__init__.py` — module export pattern
- `digitalmodel/src/digitalmodel/well/drilling/rop_models.py` — dataclass + class pattern
- `digitalmodel/tests/well/drilling/test_rop_models.py` — TDD test structure
- `digitalmodel/specs/data-sources/digitalmodel.yaml` — add `ansys_assets:` section here

### Files to create (digitalmodel repo)

**Source:**
```
src/digitalmodel/ansys/__init__.py
src/digitalmodel/ansys/models.py           # dataclasses
src/digitalmodel/ansys/apdl_reader.py     # parse .inp → materials, sections
src/digitalmodel/ansys/design_points.py   # parse DesignPointLog.csv → DesignPoint list
src/digitalmodel/ansys/wbjn_reader.py     # parse .wbjn → journal metadata
```

**Tests:**
```
tests/ansys/__init__.py
tests/ansys/test_apdl_reader.py
tests/ansys/test_design_points.py
tests/ansys/test_wbjn_reader.py
tests/ansys/fixtures/sewol_excerpt.inp       # 30 lines from sewol_global.inp
tests/ansys/fixtures/design_point_log.csv   # 5 rows from DesignPointLog.csv
tests/ansys/fixtures/journal_simple.wbjn    # minimal journal header
```

**Spec addition (workspace-hub repo):**
```
specs/data-sources/digitalmodel.yaml  — add ansys_assets: section
```

## Implementation Steps

### Step 1 — models.py (dataclasses)

```python
@dataclass
class APDLMaterial:
    mat_id: int
    elastic_modulus_mpa: float | None = None
    poissons_ratio: float | None = None
    density_kg_mm3: float | None = None

@dataclass
class APDLSection:
    section_id: int
    section_type: str        # e.g., "BEAM", "ROD"
    section_subtype: str     # e.g., "ASEC"
    area_mm2: float | None = None
    iz_mm4: float | None = None    # 2nd moment about Z
    iy_mm4: float | None = None    # 2nd moment about Y
    j_mm4: float | None = None     # polar moment

@dataclass
class DesignPoint:
    name: str               # e.g., "DP 0"
    index: int
    parameters: dict[str, float]   # P1→value, P2→value, …

@dataclass
class ParametricStudy:
    project_name: str
    creation_date: str
    parameter_labels: dict[str, str]   # "P1" → "Force Z Component [N]"
    design_points: list[DesignPoint]

@dataclass
class WBJNJournal:
    release_version: str
    filepath: str
    design_point_operations: list[str]    # e.g., ["Delete DP 3", "Delete DP 4"]
    system_names: list[str]               # GetSystem Name values
    parameter_expressions: list[tuple[str, str]]  # (param_name, expression)
```

### Step 2 — apdl_reader.py

```python
class APDLReader:
    def parse_materials(self, filepath: str | Path) -> list[APDLMaterial]:
        """Parse MP commands from .inp file.

        Recognises:
          MP,EX,<id>,<val>    → elastic_modulus_mpa
          MP,NUXY,<id>,<val>  → poissons_ratio
          MP,DENS,<id>,<val>  → density_kg_mm3
        """

    def parse_sections(self, filepath: str | Path) -> list[APDLSection]:
        """Parse SECTYPE/SECDATA blocks from .inp file."""
```

Pattern: line-by-line, skip `!` comments, split by comma, match command keywords.
No regex required — APDL commands are always comma-separated positional.

### Step 3 — design_points.py

```python
class DesignPointReader:
    def read(self, filepath: str | Path) -> ParametricStudy:
        """Parse DesignPointLog.csv.

        Handles:
          # comment lines (metadata, parameter definitions)
          Header row: Name, P1, P2, ...
          Data rows: DP <n>, <float>, <float>, ...
          Audit comment lines embedded mid-file (skip gracefully)
        """
```

Implementation: iterate lines, parse `# Parameters:` block for labels,
skip non-data `#` lines, use `csv.reader` for data rows.

### Step 4 — wbjn_reader.py

```python
class WBJNReader:
    def read_metadata(self, filepath: str | Path) -> WBJNJournal:
        """Extract key metadata from IronPython .wbjn journal.

        Extracts:
          Release version from: # Release 16.0
          SetScriptVersion(Version="...")
          GetSystem(Name="...") calls → system_names
          GetDesignPoint(Name="...").Delete() → design_point_operations
          SetParameterExpression(Parameter=..., Expression="...") → parameter_expressions
        """
```

Implementation: line-by-line text parsing. No AST parsing — use simple
string matching (`"GetSystem"`, `"GetDesignPoint"`, `"SetParameterExpression"`).

### Step 5 — __init__.py

Export all public classes:
```python
from digitalmodel.ansys.apdl_reader import APDLReader
from digitalmodel.ansys.design_points import DesignPointReader
from digitalmodel.ansys.wbjn_reader import WBJNReader
from digitalmodel.ansys.models import (
    APDLMaterial, APDLSection, DesignPoint, ParametricStudy, WBJNJournal
)
__all__ = [...]
```

### Step 6 — TDD tests (write before impl)

**test_apdl_reader.py** (10+ tests):
- `test_parse_materials_sewol_returns_steel_properties` — E=206000, nu=0.3, rho=7.85e-9
- `test_parse_materials_skips_comment_lines`
- `test_parse_materials_returns_empty_for_no_mp_commands`
- `test_parse_sections_extracts_sectype_and_secdata`

**test_design_points.py** (8+ tests):
- `test_read_parses_header_parameter_labels`
- `test_read_returns_correct_dp_count`
- `test_read_dp0_has_correct_parameter_values`
- `test_read_skips_audit_comment_lines`

**test_wbjn_reader.py** (6+ tests):
- `test_read_metadata_extracts_release_version`
- `test_read_metadata_extracts_system_names`
- `test_read_metadata_extracts_design_point_deletions`

### Step 7 — Fixtures

**sewol_excerpt.inp** (30 lines from sewol_global.inp):
- Material section: MP,EX,1,206000 / MP,NUXY,1,0.3 / MP,DENS,1,7.85e-09
- Rod section: R,101,...
- Beam section: SECTYPE,1,BEAM,ASEC / SECDATA,...

**design_point_log.csv** (hand-crafted 5-row sample):
```
# This file is written by the ANSYS DesignXplorer
# Project name: SplitBody_Mesh_rev3
# Parameters:
# P1 - Force Z Component [N]
# P2 - Force 2 Z Component [N]
Name, P1, P2
DP 0, 1700000.0, -1700000.0
DP 1, 1000000.0, -1000000.0
```

**journal_simple.wbjn** (minimal header):
```python
# encoding: utf-8
# Release 16.0
SetScriptVersion(Version="16.0.361")
system1 = GetSystem(Name="SYS")
designPoint1 = Parameters.GetDesignPoint(Name="3")
designPoint1.Delete()
```

### Step 8 — specs/data-sources/digitalmodel.yaml update (hub repo)

Add `ansys_assets:` section after `orcaflex_models:`:
- 7 project entries (pipeline FEA, drilling, riser, tutorial)
- Each entry: project_id, domain, description, path, file_types, analysis_type, computer

## TDD Order

1. Write ALL fixture files first
2. Write ALL test files (failing)
3. Write models.py
4. Write apdl_reader.py → run tests/ansys/test_apdl_reader.py → green
5. Write design_points.py → run tests/ansys/test_design_points.py → green
6. Write wbjn_reader.py → run tests/ansys/test_wbjn_reader.py → green
7. Write __init__.py
8. Full test run: `PYTHONPATH=src python3 -m pytest tests/ansys/ -v`
9. Legal scan on new files
10. Git commit (plumbing — large pack files)
11. Update specs/data-sources/digitalmodel.yaml in hub repo + commit

## Verification

```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel
PYTHONPATH=src python3 -m pytest tests/ansys/ -v
# Expect: 24+ tests pass, 0 fail

PYTHONPATH=src python3 -c "
from digitalmodel.ansys import APDLReader, DesignPointReader
r = APDLReader()
mats = r.parse_materials('tests/ansys/fixtures/sewol_excerpt.inp')
print(mats[0])  # APDLMaterial(mat_id=1, elastic_modulus_mpa=206000.0, ...)
"
```

## Constraints

- No dependencies on ANSYS software — pure file parsing
- No /mnt/ace paths in test code — fixtures only
- Legal: no client project names in code (generic: `steel_material`, `design_point_zero`)
- Coverage ≥ 80% on new files (enforced by pyproject.toml)
- Cross-review via `scripts/review/cross-review.sh` after implementation
