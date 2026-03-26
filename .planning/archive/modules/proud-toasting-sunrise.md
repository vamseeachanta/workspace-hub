---
title: "Fix diff.headings empty-after-Calculate() bug and regenerate affected reports"
description: "Pass owr_path through the validation pipeline so reports use LoadResults() for correct headings"
version: 1.0.0
module: digitalmodel/L00_validation_wamit
session:
  id: proud-toasting-sunrise
  agent: claude-sonnet-4-6
review: pending
---

# Context

**Problem**: 7 of 13 WAMIT validation cases show `Headings: 0 (°)` in their individual
`benchmark_report.html` files even though wave headings are defined in `spec.yml`.
This makes DOF plots appear empty and violates the report consistency requirement
(individual reports must support the master summary's PASS verdict).

**Root cause**: `OrcFxAPI.Diffraction.headings` returns an empty array after
`Calculate()` is called in memory for certain analysis types (`full_qtf`,
bi-symmetric configurations, fixed-DOF bodies). The property is only reliably
populated via `LoadResults()` from a saved `.owr` file.

**Why some cases are OK**: Cases 2.7, 2.8, 2.9 were recently regenerated and work
correctly — on investigation, the same code path is used for all cases. The difference
is OrcFxAPI behaviour per analysis type, not code version.

**Intended outcome**: All 7 affected individual reports show correct heading counts,
full DOF plots with data, and complete physics sections (hydrostatics, load RAOs,
roll damping) — matching what the master summary already shows.

---

# Affected Cases

| Case | Analysis type | Headings | Shown | Fix needed |
|------|--------------|----------|-------|------------|
| 2.2  | diffraction  | [0°, 27°] | 0   | Yes |
| 2.3  | diffraction  | [0°, 27°] | 0   | Yes |
| 2.5c | diffraction  | [35°]     | 0   | Yes |
| 2.5f | diffraction  | [35°]     | 0   | Yes |
| 3.1  | full_qtf     | [0°]      | 0   | Yes |
| 3.2  | diffraction  | [0°]      | 0   | Yes |
| 3.3  | diffraction  | [0°]      | 0   | Yes (2 bodies → 3 HTML files) |

---

# Implementation Plan

## Step 1 — Fix `validate_owd_vs_spec.py` (~12 lines, 3 change sites)

**File**: `scripts/benchmark/validate_owd_vs_spec.py`

### 1a. `solve_owd()` — return `owr_path` as 5th element

```python
# Current return signature (line 356):
def solve_owd(case_id: str) -> tuple[dict[int, Optional["DiffractionResults"]], dict, Optional[Path], list[dict]]:

# New:
def solve_owd(case_id: str) -> tuple[dict[int, Optional["DiffractionResults"]], dict, Optional[Path], list[dict], Optional[Path]]:
```

```python
# Current return (line 438):
return results_by_body, coupling, owd_yml_path, panel_geometry_data

# New (owr_path already declared at line 391, set to None on failure):
return results_by_body, coupling, owd_yml_path, panel_geometry_data, owr_path
```

Note: `owr_path` is already declared at line 391 — `owr_path = out_dir / f"{owd_path.stem}_ground_truth.owr"`.
On SaveResults() failure, it should be set to `None` in the except block.

### 1b. `run_comparison()` — accept `owr_path` and attach to metadata

```python
# Current signature (line 644):
def run_comparison(
    owd_results_by_body, spec_results_by_body,
    coupling_owd, coupling_spec,
    case_id, owd_yml_path=None, spec_yml_path=None,
    panel_geometry_data=None,
) -> dict:

# Add parameter:
    owr_path: Optional[Path] = None,
```

After building metadata (around line 764, after semantic data attachment):
```python
# Attach .owr path so report generator uses LoadResults() for correct headings
if owr_path and owr_path.exists() and "OrcaWave (.owd)" in metadata:
    metadata["OrcaWave (.owd)"]["owr_path"] = str(owr_path)
```

### 1c. `run_case()` — unpack 5th element and pass to `run_comparison()`

```python
# Current (line 1415):
owd_by_body, coupling_owd, owd_yml_path, panel_geometry_data = solve_owd(case_id)

# New:
owd_by_body, coupling_owd, owd_yml_path, panel_geometry_data, owr_path = solve_owd(case_id)
```

```python
# Current run_comparison call (line 1448):
comp_result = run_comparison(
    owd_by_body, spec_by_body,
    coupling_owd, coupling_spec,
    case_id,
    owd_yml_path=owd_yml_path,
    spec_yml_path=spec_yml_path,
    panel_geometry_data=panel_geometry_data,
)

# New — add owr_path:
    owr_path=owr_path,
```

---

## Step 2 — Regenerate affected cases

Run each affected case sequentially (OrcaWave Calculate() + report generation):

```bash
cd /d/workspace-hub/digitalmodel
uv run python scripts/benchmark/validate_owd_vs_spec.py --case 2.2
uv run python scripts/benchmark/validate_owd_vs_spec.py --case 2.3
uv run python scripts/benchmark/validate_owd_vs_spec.py --case 2.5c
uv run python scripts/benchmark/validate_owd_vs_spec.py --case 2.5f
uv run python scripts/benchmark/validate_owd_vs_spec.py --case 3.1
uv run python scripts/benchmark/validate_owd_vs_spec.py --case 3.2
uv run python scripts/benchmark/validate_owd_vs_spec.py --case 3.3
```

Expected output per case: `Extracted: N freq x M headings` where M > 0.

---

## Step 3 — Regenerate master summary

```bash
uv run python scripts/benchmark/validate_owd_vs_spec.py --summary-only
```

---

## Step 4 — Update WRK-162 progress log

Add Phase 6 entry to `.claude/work-queue/pending/WRK-162.md` documenting:
- Bug fixed: `diff.headings` empty-after-Calculate()
- Code change: `solve_owd()` return + `run_comparison()` metadata + `run_case()` unpack
- Cases regenerated: 2.2, 2.3, 2.5c, 2.5f, 3.1, 3.2, 3.3

---

## Step 5 — Commit

Two commits:
1. `digitalmodel`: code fix + regenerated HTML reports
2. `workspace-hub`: submodule pointer + WRK-162 update

---

# Critical Files

| File | Change |
|------|--------|
| `digitalmodel/scripts/benchmark/validate_owd_vs_spec.py` | 3 change sites, ~12 lines |
| `digitalmodel/docs/modules/orcawave/L00_validation_wamit/*/benchmark/benchmark_report.html` | Regenerated (7 cases) |
| `digitalmodel/docs/modules/orcawave/L00_validation_wamit/validation_summary.html` | Regenerated |
| `.claude/work-queue/pending/WRK-162.md` | Phase 6 note added |

---

# Verification

After regeneration, for each affected case the individual report should show:
- `Headings: N (X.X°)` with N > 0 in the report header
- DOF plots with actual response curves (not empty/flat lines)
- Hydrostatics section populated (Centre of buoyancy, waterplane area, etc.)
- Load RAO section populated

Quick check command:
```bash
python -c "
import re, pathlib
base = pathlib.Path(r'D:\workspace-hub\digitalmodel\docs\modules\orcawave\L00_validation_wamit')
for p in sorted(base.rglob('benchmark_report.html')):
    html = p.read_text(encoding='utf-8')
    m = re.search(r'Headings: (\d+)', html)
    h = m.group(1) if m else '?'
    print(f'{str(p.relative_to(base)):<60} headings={h}')
"
```

Expected: all cases show `headings=N` where N ≥ 1.

---

# Notes on `owr_path` for multi-body cases (2.6, 3.3)

For 2.6 and 3.3 (already showing correct headings), the single `.owr` file contains
both bodies' data. When `extract_report_data_from_owr()` is called with `d.hydrostaticResults[0]`,
it returns body 0's hydrostatics. This is acceptable for the per-body reports
(heading data is shared, hydrostatics per-body are body 0 in both sub-reports).
No change needed for 2.6/3.3 since they already show correct heading counts.
