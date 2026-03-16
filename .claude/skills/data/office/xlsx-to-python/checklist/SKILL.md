---
name: xlsx-to-python-checklist
description: 'Sub-skill of xlsx-to-python: Checklist.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Checklist

## Checklist


- [ ] Dual-pass load (values + formulas) — verify cached values exist
- [ ] All formula cells extracted with both formula text and computed value
- [ ] Named ranges mapped to variable names
- [ ] Dependency graph built and classified (inputs/intermediates/outputs)
- [ ] Calculation blocks identified (vs data/lookup tables)
- [ ] **Row patterns detected** — normalize formulas via `Translator`, group by pattern
- [ ] **Loop collapse** — repeated patterns (≥3 rows) emit Python loops, not per-cell code
- [ ] **Formula → Python translation** — simple arithmetic auto-translated; complex via `formulas` lib
- [ ] Baseline tests generated using Excel cell values as `pytest.approx()` assertions
- [ ] 10 parametric variations generated per calculation
- [ ] Parametric tests verify at minimum: result is finite, within physical bounds
- [ ] Dark-intelligence archive YAML produced with `legal_scan_passed: false`
- [ ] Legal scan passed — set `legal_scan_passed: true`
- [ ] Calc-report YAML generated from archive
