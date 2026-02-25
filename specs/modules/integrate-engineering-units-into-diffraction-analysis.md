---
title: "Add semantic score column to validation summary and refresh data from benchmark JSONs"
description: "Enhance the master validation_summary.html to show semantic equivalence scores per case, and read DOF correlations from actual benchmark_report.json files instead of stale config notes"
version: "0.1.0"
module: hydrodynamics/diffraction
session:
  id: 2026-02-16-semantic-summary
  agent: claude-opus-4.6
review:
  status: draft
  reviewers: []
---

# Add Semantic Score to Validation Summary

## Context

The master `validation_summary.html` table currently shows per-DOF correlation coefficients and a PASS/FAIL status per case. Two problems:

1. **No semantic equivalence data** — The individual benchmark reports already compute semantic equivalence (match/cosmetic/convention/significant diffs between OWD and spec YAML configs), but the master summary table doesn't surface this. Knowing whether configurations are semantically equivalent is critical for interpreting correlation results.

2. **Stale data** — `--summary-only` mode reads DOF correlations from manually-maintained `validation_config.yaml` notes (e.g. `r=1.000000`). But actual `benchmark_report.json` files exist for all 12 cases with precise correlation values. Cases 2.8 and 2.9 were just re-run with fixes and the config is stale.

## Approach

### Single file change: `scripts/benchmark/validate_owd_vs_spec.py`

**A. Enhance `_build_results_from_config()`** — Read actual data from benchmark artifacts:
- For each case, read `benchmark_report.json` → extract per-DOF correlation from `consensus_by_dof[DOF].mean_pairwise_correlation`
- For each case, find the YAML pair (`*_input.yml` + `spec_orcawave/*.yml` excluding `spec_input.yml`) → run `_compare_orcawave_ymls()` → extract significant/cosmetic/convention/match counts
- Fall back to config notes parsing when artifacts don't exist

**B. Add semantic column to `_generate_master_html()`**:
- New table header: `<th>Semantic</th>` between "Status" and "Surge"
- Cell rendering:
  - `0 significant` → green badge "EQUIV"
  - `N significant` → amber/red badge "N diff(s)"
  - No data → gray "-"
- Legend entry explaining semantic equivalence

**C. Update `validation_config.yaml`** — Refresh case 2.9 notes (heave was 0.999871, now 1.000000 after fix)

**D. Run `--summary-only`** to regenerate `validation_summary.html`

## Detailed Changes

### `scripts/benchmark/validate_owd_vs_spec.py`

#### 1. `_build_results_from_config()` (~lines 925-997)

Replace the notes-parsing approach with benchmark JSON reading:

```python
def _build_results_from_config() -> dict:
    """Build results dict from benchmark artifacts + validation_config.yaml fallback."""
    # For each case:
    #   1. Try reading benchmark_report.json → DOF correlations
    #   2. Try finding YAML pair → semantic equivalence
    #   3. Fall back to config notes
```

**DOF correlation from JSON:**
```python
json_path = L00_DIR / cid / "benchmark" / "benchmark_report.json"
if json_path.exists():
    with open(json_path) as f:
        report = json.load(f)
    consensus = report.get("consensus_by_dof", {})
    for dof in dof_names:
        dof_upper = dof.upper()
        if dof_upper in consensus:
            corr = consensus[dof_upper].get("mean_pairwise_correlation", "N/A")
            # Determine max_abs_diff from rao_comparisons if available
            dof_summary[dof] = {"correlation": corr, "max_abs_diff": ..., "n_points": ...}
```

**Semantic equivalence from YAML pair:**
```python
benchmark_dir = L00_DIR / cid / "benchmark"
owd_ymls = list(benchmark_dir.glob("*_input.yml"))
spec_dir = benchmark_dir / "spec_orcawave"
spec_ymls = [f for f in spec_dir.glob("*.yml") if f.name != "spec_input.yml"]
if owd_ymls and spec_ymls:
    sem = _compare_orcawave_ymls(owd_ymls[0], spec_ymls[0])
    result["semantic"] = sem
```

#### 2. `run_case()` (~line 909)

After computing DOF summary, also store semantic data:
```python
result["dof_summary"] = summary
# Extract semantic data if it was computed (it's attached to metadata)
# Actually: compute it here from the YAML paths we already have
```

Wait — for live runs (`--all`), semantic data is computed in `run_comparison()` but not returned. Rather than refactoring the return value, compute it in `_build_results_from_config()` for `--summary-only` and in `run_case()` for `--all`.

For `run_case()`: add semantic computation after the comparison step:
```python
# After line 909: result["dof_summary"] = summary
# Compute semantic equivalence
owd_yml = benchmark_dir / f"{vessel_name}_input.yml"  # need to find this
spec_yml = spec_orcawave_dir / f"{vessel_name}.yml"
if owd_yml.exists() and spec_yml.exists():
    result["semantic"] = _compare_orcawave_ymls(owd_yml, spec_yml)
```

Actually, this is complex because run_case() doesn't track the YAML paths outside run_comparison(). **Simpler: just enhance `_build_results_from_config()` and let `--all` mode use the same JSON-reading approach for the summary.**

For `--all` mode, modify the flow at line 1319:
```python
if args.all and not args.owd_only:
    # Rebuild results from JSON files to get semantic data
    enriched = _build_results_from_config()
    # Merge live results (which have status) with enriched data (which has semantic)
    for cid in results:
        if cid in enriched and "semantic" in enriched[cid]:
            results[cid]["semantic"] = enriched[cid]["semantic"]
    html_path = _generate_master_html(results, OUTPUT_DIR)
```

Actually even simpler: just always enrich results with semantic data from YAML files before generating HTML, regardless of mode.

#### 3. `_generate_master_html()` (~lines 1009-1232)

**Table header** — Add "Semantic" column:
```python
<th>Case</th><th>Description</th><th>Phase</th><th>Panels</th>
<th>WAMIT</th><th>Status</th><th>Semantic</th>
<th>Surge</th><th>Sway</th>...
```

**Cell rendering** in the per-case row loop:
```python
sem = r.get("semantic", None)
if sem:
    sig = sem["significant_count"]
    total = sem["match_count"] + sem["cosmetic_count"] + sem.get("convention_count", 0) + sig
    if sig == 0:
        sem_cell = f'<td style="text-align:center"><span style="color:#16a34a;font-weight:bold">EQUIV</span></td>'
    else:
        color = "#dc2626" if sig > 2 else "#d97706"
        sem_cell = f'<td style="text-align:center"><span style="color:{color};font-weight:bold">{sig} diff(s)</span></td>'
else:
    sem_cell = '<td style="text-align:center;color:#9ca3af">-</td>'
```

**Legend** — Add semantic entry:
```html
<span style="color:#16a34a">EQUIV = 0 significant solver parameter differences</span>
```

**Footer** — Update to mention semantic score.

#### 4. Blocked case rows

For blocked cases (not in results), semantic cell = "-".

### `validation_config.yaml`

Update case 2.9 notes: `heave r=0.999871` → `r=1.000000` (all DOFs now match after the preferred_load_rao_method fix).

## Implementation Sequence

| Step | Action | Verify |
|------|--------|--------|
| 1 | Modify `_build_results_from_config()` to read JSON + compute semantic | Unit check: print results dict |
| 2 | Modify `_generate_master_html()` to add Semantic column | Visual: check HTML output |
| 3 | Enrich `--all` mode results with semantic data | Already covered by step 1 |
| 4 | Update `validation_config.yaml` notes for case 2.9 | Manual check |
| 5 | Run `--summary-only` to regenerate | Open HTML, verify all values + semantic column |

## Verification

1. `cd /d/workspace-hub/digitalmodel && uv run python scripts/benchmark/validate_owd_vs_spec.py --summary-only`
2. Open `docs/modules/orcawave/L00_validation_wamit/validation_summary.html` in browser
3. Verify:
   - All 12 case rows present with correct DOF correlation values (from JSON, not notes)
   - New "Semantic" column shows EQUIV or N diff(s) for each case
   - Case 2.9 heave shows updated correlation (~1.000000, not 0.999871)
   - Report hyperlinks work
   - Legend includes semantic explanation

## Critical Files

| File | Role |
|------|------|
| `scripts/benchmark/validate_owd_vs_spec.py` | Main changes: `_build_results_from_config()`, `_generate_master_html()` |
| `docs/.../L00_validation_wamit/validation_config.yaml` | Update stale notes |
| `docs/.../L00_validation_wamit/validation_summary.html` | Output — regenerated |
| `docs/.../L00_validation_wamit/*/benchmark/benchmark_report.json` | Read-only: DOF correlation source |
| `docs/.../L00_validation_wamit/*/benchmark/*_input.yml` | Read-only: OWD YAML for semantic comparison |
| `docs/.../L00_validation_wamit/*/benchmark/spec_orcawave/*.yml` | Read-only: spec YAML for semantic comparison |
