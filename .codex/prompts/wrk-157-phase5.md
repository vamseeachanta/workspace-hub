# WRK-157 Phase 5 — Design-Code Report Templates

## Task
Implement per-standard design-code report templates for the fatigue analysis module in
`digitalmodel/src/digitalmodel/structural/fatigue/`.

## Context

### What exists
- `sn_curves.py` — S-N curve library (DNV, API, BS, AWS, IIW standards)
- `damage_accumulation.py` — Palmgren-Miner + modified + nonlinear + critical plane
- `rainflow.py` — ASTM E1049-85 rainflow counting
- `sn_comparison_report.py` — multi-curve overlay HTML report
- `parametric_sweep.py` — SCF/curve/thickness/DFF parameter sweep with tornado chart HTML
- `worked_examples.py` — three canonical examples (pipeline, SCR, mooring) with Plotly HTML
- `analysis.py` — FatigueAnalysisEngine integration orchestrator
- `__init__.py` — exports all public symbols

### Phase 5 target: `design_code_report.py`
Create a new file with a **per-standard report generator** that produces a standalone HTML
report matching the quality of `sn_comparison_report.py` and `worked_examples.py`.

## Acceptance Criteria

1. **`DesignCodeReport` class** — accepts:
   - `standard: str` — "DNV-RP-C203", "BS 7608", "API RP 2A", "IIW"
   - `result: ExampleResult` (from `worked_examples.py`) or raw damage dict
   - Optional: `title`, `company`, `project_ref`, `revision`

2. **Report sections** (HTML, self-contained with Plotly CDN):
   - Header: standard name, methodology summary, applicable scope
   - S-N curve parameters table: class, m-slope, log(A), CAFL, environment
   - Damage calculation methodology (Palmgren-Miner explanation block)
   - Interactive S-N chart with operating point cloud (from histogram)
   - Damage breakdown table: stress range bins, ni, Ni, ni/Ni contribution
   - Summary box: total damage, life years, DFF check (PASS/FAIL with colour)
   - Recommendations section: pulled from existing `create_fatigue_report()` logic
   - References section: standard-specific bibliography

3. **`generate_design_code_report(result, standard, output_path=None, **kwargs) -> str`**
   — convenience function, returns HTML string or writes to file

4. **`__init__.py` exports** — add `DesignCodeReport`, `generate_design_code_report`

5. **Tests** in `tests/structural/fatigue/test_design_code_report.py`:
   - Smoke tests for each of the 4 standards
   - HTML contains standard name, Plotly, damage value
   - File write test
   - PASS/FAIL colour coding present
   - References section present for each standard
   - At minimum 30 tests

## Constraints
- Python 3.12, no new external deps (Plotly already available)
- File length ≤ 400 lines (split into helper if needed)
- Function length ≤ 50 lines
- Follow patterns from `worked_examples.py` for HTML generation
- Test file ≤ 400 lines
- Run tests with:
  `PYTHONPATH=src python3 -m pytest tests/structural/fatigue/test_design_code_report.py -v --noconftest`
  from `digitalmodel/` directory

## Standard-specific notes

### DNV-RP-C203
- Reference: DNV-RP-C203 (2016 + 2019 amendments)
- Curves: Table 2-1 (air), Table 2-2 (seawater+CP), Table 2-3 (seawater free-corrosion)
- Thickness correction: (t/tref)^k where tref=25mm
- Weld improvement: grinding, hammer peening references

### BS 7608
- Reference: BS 7608:2014+A1:2015
- Classes: B, C, D, E, F, F2, G, W
- Environment: air (default), marine (apply factor)

### API RP 2A
- Reference: API RP 2A-WSD 22nd Edition
- Curves: X, X′ (tubular joints)
- Note: SCF via Efthymiou equations

### IIW
- Reference: IIW Recommendations Doc. XIII-2460-13
- FAT classes (FAT 36 – FAT 160)
- Mean stress effect: R-ratio correction

## Working directory
All work in: `/mnt/local-analysis/workspace-hub/digitalmodel/`
Commit to `digitalmodel` repo then note final test count.
WRK item: WRK-157 Phase 5
