# WRK-315 + WRK-316 Implementation Plans

## Context

A codebase scan triggered by WRK-314 Phase 4 completion found legacy OrcFxAPI
scripts in `digitalmodel/docs/domains/orcaflex/`. Two follow-up work items were
created:
- **WRK-315**: Migrate the 24in pipeline installation HTML report scripts to Phase 4
- **WRK-316**: Inventory and triage all legacy OrcFxAPI scripts (~42 files)

Exploration reveals a critical architectural insight: Phase 4 is a **single-case,
single-structure** report framework. The legacy pipeline scripts are **multi-case
sensitivity analysis** scripts (tension × environment × heading sweeps). A
wholesale rewrite is out of scope; the approach is a **hybrid migration** using
Phase 4 extractors for data extraction while retaining domain-specific sensitivity
rendering logic.

---

## Plan A — WRK-315: Migrate 24in Pipeline Scripts

### Current State

| File | Lines | Pattern |
|------|-------|---------|
| `generate_html_report.py` | 795 | Direct OrcFxAPI → Plotly → ad-hoc HTML |
| `generate_env_case_report.py` | 687 | Direct OrcFxAPI → Plotly → ad-hoc HTML |
| `test_postproc.py` | ~30 | Unit tests for above |

Both scripts share the same data extraction pattern:
```python
import OrcFxAPI
model = OrcFxAPI.Model(sim_file)
pipeline = model['pipeline']
rg = pipeline.RangeGraph('Effective Tension', period)
te_end_a = pipeline.TimeHistory('Effective Tension', period, objectExtra=oeEndA)
```

### Gap Analysis (exploration findings)

| Legacy Feature | Phase 4 Status | Action |
|---|---|---|
| OrcFxAPI extraction (RangeGraph, TimeHistory) | ✅ `aggregator.py:build_report_from_model()` | Reuse directly |
| RangeGraph CSV export | ❌ Missing | **Add** `export_rangegraph_csvs()` to `aggregator.py` |
| Multi-case sensitivity (tension × env × heading) | ❌ Not in scope | Keep in domain script |
| Dual-view charts (full + critical zone zoom) | ❌ Missing | Keep in domain script |
| Bar charts for case comparison | ❌ Missing | Keep in domain script |
| Design-based coloring (UC > 0.90 = FAIL) | ✅ `DesignCheckData.checks` supports it | Map X65 utilization to `UtilizationData` |

### Step 1: Add `export_rangegraph_csvs()` to aggregator.py

Location: `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/extractors/aggregator.py`

```python
def export_rangegraph_csvs(
    lines: list,
    variables: list[str],
    period,
    output_dir: Path,
) -> list[Path]:
    """Export arc-length distributed RangeGraph results as CSV per line per case."""
```

- Calls `line.RangeGraph(var, period)` for each `var` in `variables`
- Writes one CSV per line: columns = `ArcLength_m | {var}_Min | {var}_Max | {var}_Mean`
- Returns list of written paths
- Add test to `test_extractors.py` (mock RangeGraph return)

### Step 2: Rewrite extraction layer in both scripts

Replace the direct `import OrcFxAPI` extraction block in each script with:

```python
from digitalmodel.solvers.orcaflex.reporting.extractors.aggregator import (
    build_report_from_model, export_rangegraph_csvs,
)
import OrcFxAPI

model = OrcFxAPI.Model(sim_path)
report = build_report_from_model(
    model,
    project_name="24in Pipeline Installation",
    structure_type="installation",
)
# CSV side-effect
export_rangegraph_csvs(
    lines=[model['pipeline']],
    variables=['Effective Tension', 'Max Bending Stress', 'Direct Tensile Strain'],
    period=OrcFxAPI.pnDynamic,
    output_dir=rangegraph_dir,
)
```

Preserve all Plotly chart functions and HTML page generation logic unchanged.

### Step 3: Map X65 utilization to DesignCheckData

In `generate_html_report.py`, the utilization is:
```python
util = (bend_stress + tens_stress) / X65_YIELD_MPa
```

Map to Phase 4 models:
```python
from digitalmodel.solvers.orcaflex.reporting.models.design_checks import (
    DesignCheckData, UtilizationData,
)

report.design_checks = DesignCheckData(
    code="DNV-OS-F101 (combined loading)",
    checks=[
        UtilizationData(
            name=f"Combined loading — {case_name}",
            uc=util,
            allowable=UTIL_LIMIT,  # 0.90
            load_case=case_name,
            location_arc_m=worst_arc,
        )
        for case_name, util, worst_arc in worst_utils
    ],
)
generate_orcaflex_report(report, summary_output_path)
```

This produces a Phase 4 HTML summary page alongside the existing sensitivity pages.

### Step 4: Archive originals

Move `generate_html_report.py` and `generate_env_case_report.py` to
`postproc/_archive/` with a `MIGRATED.md` note. Keep `test_postproc.py` and
update it to test the new extraction layer.

### Step 5: Test + legal scan

```bash
cd /d/workspace-hub/digitalmodel
uv run python -m pytest tests/solvers/orcaflex/reporting/ -v --cov-fail-under=80
bash /d/workspace-hub/scripts/legal/legal-sanity-scan.sh
# Verify CSV output
uv run python docs/domains/orcaflex/pipeline/installation/floating/24in_pipeline/monolithic/postproc/generate_html_report.py --dry-run
```

### Critical Files

| File | Action |
|------|--------|
| `docs/domains/orcaflex/pipeline/installation/.../postproc/generate_html_report.py` | Rewrite extraction layer, map UCs to Phase 4, archive original |
| `docs/domains/orcaflex/pipeline/installation/.../postproc/generate_env_case_report.py` | Same |
| `docs/domains/orcaflex/pipeline/installation/.../postproc/test_postproc.py` | Update to test new extraction layer |
| `src/digitalmodel/solvers/orcaflex/reporting/extractors/aggregator.py` | Add `export_rangegraph_csvs()` |
| `tests/solvers/orcaflex/reporting/test_extractors.py` | Add test for `export_rangegraph_csvs()` |
| `.claude/work-queue/pending/WRK-315.md` | Update to complete |

### Verification

1. `uv run python generate_html_report.py` — produces same HTML + CSV output as before
2. New Phase 4 summary HTML written alongside existing sensitivity pages
3. `test_postproc.py` passes
4. Coverage ≥ 80%

---

## Plan B — WRK-316: Legacy Script Inventory

### Current State (from exploration)

Actual count: **~42 Python files** in `docs/domains/orcaflex/` (~32 directly
import OrcFxAPI; the 194 count included `.venv`).

Domain breakdown:
| Domain | Count | Pattern | Priority |
|--------|-------|---------|----------|
| Risers/Production/charts | 10 | matplotlib charts | archive |
| Risers/Production/csv | 10 | CSV extraction loops | archive |
| Risers/Drilling | 3 | Excel preprocessing | archive |
| Mooring/semi/rao-check | 2 | TimeHistory RAO | review |
| Pipeline/installation | 3 | HTML reports (WRK-315) | ✅ WRK-315 |
| Examples/raw (K01/K02) | 3 | Vendor Orcina tutorials | out-of-scope |
| Examples/GOM SCR design study | 4 | Parametric model gen | review |
| Utilities | 2 | Patterns | reference |

### Approach: Automated inventory script + manual triage

#### Step 1: Write `scripts/inventory/orcaflex_legacy_inventory.py`

Script (no OrcFxAPI needed — reads metadata only):
```python
"""Enumerate all legacy OrcFxAPI scripts and output a triage table."""
import subprocess, pathlib, ast, re

def classify(filepath):
    src = filepath.read_text(errors='replace')
    lines = src.splitlines()
    report_type = (
        'html_report' if 'html' in src.lower() else
        'chart' if 'matplotlib' in src or 'plotly' in src else
        'csv' if 'csv' in src.lower() or 'excel' in src.lower() else
        'preproc' if 'Model(' in src and 'CreateObject' in src else
        'postproc'
    )
    return {
        'path': str(filepath),
        'lines': len(lines),
        'report_type': report_type,
        'imports_orcfxapi': 'import OrcFxAPI' in src or 'from OrcFxAPI' in src,
    }
```

Output: `docs/domains/orcaflex/LEGACY_SCRIPT_INVENTORY.md` — markdown table with:

```
| File | Lines | Type | Domain | Migration | Phase4 Gap |
```

#### Step 2: Manual triage decisions

Apply the following rules in the script:

| Rule | Migration value |
|------|----------------|
| K01/K02 raw examples | `out-of-scope` — vendor code |
| Risers/production/charts (matplotlib only) | `archive` — superseded by Phase 4 renderers |
| Risers/production/csv | `archive` — data extraction now via Phase 4 extractors |
| Risers/drilling preprocessing | `archive` — one-time setup scripts |
| GOM SCR design study | `review` — active parametric workflow, may benefit from migration |
| Mooring RAO study scripts | `review` — RAO comparison not in Phase 4 |
| Pipeline (WRK-315) | `migrating` — tracked separately |

#### Step 3: Identify systemic Phase 4 gaps

From the classification table, identify features present in ≥3 scripts that
Phase 4 doesn't cover. Based on exploration findings, expect:
- **matplotlib-based charts**: 10 riser scripts → note: no matplotlib renderer in Phase 4
- **Excel export**: 10 riser CSV scripts → note: no Excel output in Phase 4
- **Parametric model generation**: GOM SCR scripts → note: out of Phase 4 scope

Create a "Systemic Gaps" subsection in the inventory markdown and add WRK items
for gaps worth addressing.

#### Step 4: Commit inventory + any new WRK items

```bash
cd /d/workspace-hub/digitalmodel
uv run python scripts/inventory/orcaflex_legacy_inventory.py
git add docs/domains/orcaflex/LEGACY_SCRIPT_INVENTORY.md scripts/inventory/
git commit -m "feat(inventory): add legacy OrcFxAPI script triage table (WRK-316)"
```

Update `.claude/work-queue/pending/WRK-316.md` → `percent_complete: 100`.

### Critical Files

| File | Action |
|------|--------|
| `scripts/inventory/orcaflex_legacy_inventory.py` | Create — automated inventory script |
| `docs/domains/orcaflex/LEGACY_SCRIPT_INVENTORY.md` | Create — triage table output |
| `.claude/work-queue/pending/WRK-316.md` | Update to complete |

### Verification

1. `uv run python scripts/inventory/orcaflex_legacy_inventory.py` — runs without error
2. `LEGACY_SCRIPT_INVENTORY.md` contains ≥ 30 rows
3. Each row has migration decision populated
4. Systemic gaps section lists ≥ 2 Phase 4 gaps
5. Legal scan passes

---

## Sequencing

```
WRK-315 → WRK-316 (inventory informs any additional migration gaps)
          |
          └─ Any new WRK items from systemic gap analysis
```

WRK-315 **Step 1** (add `export_rangegraph_csvs`) can be done without reading
the legacy scripts; run it first as a clean Phase 4 extension, then address the
legacy scripts in Steps 2–4.
