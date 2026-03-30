---

name: calculation-report
description: Generate professional engineering calculation reports from YAML — renders LaTeX formulas, interactive charts, and pass/fail outputs as HTML using the warm-parchment design system
type: reference
version: "1.0.0"
triggers:
  - calculation report
  - calc report
  - engineering report
  - fatigue report
  - generate report from YAML
category: data
---

# Calculation Report Skill

## Pipeline

```
calculation.yaml → generate-calc-report.py → report.html (default) / report.md
```

## Usage

```bash
# Generate HTML (default)
uv run --no-project python scripts/reporting/generate-calc-report.py <input.yaml>

# Generate Markdown with LaTeX math
uv run --no-project python scripts/reporting/generate-calc-report.py <input.yaml> --format md

# Specify output path
uv run --no-project python scripts/reporting/generate-calc-report.py <input.yaml> --output path/to/report.html
```

## YAML Structure (Required Sections)

- **metadata**: title, doc_id, revision, date, author, status (draft/reviewed/approved)
- **inputs**: list of {name, symbol, value, unit} with optional source/notes
- **methodology**: description, standard, equations [{id, name, latex, description}]
- **outputs**: list of {name, symbol, value, unit} with optional pass_fail/limit
- **assumptions**: list of strings
- **references**: list of strings

## Optional Sections

- **charts**: interactive Chart.js charts (line, bar, scatter, log_log)
- **data_tables**: tabular data with column headers and units
- **change_log**: revision history in metadata

## Examples (13 calc reports)

- `examples/reporting/fatigue-pipeline-girth-weld.yaml` — pipeline girth weld fatigue (DNV-RP-C203)
- `examples/reporting/fatigue-scr-touchdown.yaml` — SCR touchdown zone fatigue
- `examples/reporting/spectral-fatigue-dnv-rp-c203.yaml` — spectral fatigue (DNV-RP-C203)
- `examples/reporting/geotechnical-pile-axial-capacity.yaml` — pile capacity (API RP 2GEO)
- `examples/reporting/geotechnical-anchor-capacity.yaml` — anchor capacity (DNV-RP-E302/E303)
- `examples/reporting/geotechnical-scour-assessment.yaml` — scour depth (DNV-RP-F107)
- `examples/reporting/on-bottom-stability-pipeline.yaml` — pipeline stability (DNV-RP-F109)
- `examples/reporting/on-bottom-stability-dnv-rp-f109.yaml` — detailed stability check
- `examples/reporting/sepd-decline-unconventional.yaml` — SEPD decline curve
- `examples/reporting/type-curve-matching-fetkovich.yaml` — Fetkovich type curves
- `examples/reporting/resource-estimation-monte-carlo.yaml` — P10/P50/P90 resources (SPE PRMS)
- `examples/reporting/portfolio-beta-energy-benchmark.yaml` — portfolio beta (CAPM)
- `examples/reporting/dividend-yield-forecast.yaml` — Gordon growth model

## Schema Validation Gate (mandatory before report generation)

Full schema at `config/reporting/calculation-report-schema.yaml`.

Validate EVERY YAML before generating the report:
```bash
uv run --no-project python -c "
import yaml
with open('config/reporting/calculation-report-schema.yaml') as f:
    schema = yaml.safe_load(f)
with open('<your-calc>.yaml') as f:
    report = yaml.safe_load(f)
# Required sections
for s in ['metadata', 'inputs', 'methodology', 'outputs', 'assumptions', 'references']:
    assert s in report, f'Missing: {s}'
# Metadata fields
for f in ['title', 'doc_id', 'revision', 'date', 'author', 'status']:
    assert f in report['metadata'], f'Missing metadata.{f}'
# Standard traceability
assert 'standard' in report['methodology'], 'Missing methodology.standard'
assert 'equations' in report['methodology'], 'Missing methodology.equations'
for eq in report['methodology']['equations']:
    assert 'name' in eq and 'latex' in eq, f'Equation missing name or latex'
print('PASS')
"
```

## Compliance Audit

Run periodically to catch missing reports across all implementations:
```bash
# List all calc report YAMLs and validate each
for f in examples/reporting/*.yaml; do
  echo -n "$f: "
  uv run --no-project python -c "import yaml; d=yaml.safe_load(open('$f')); [d[s] for s in ['metadata','inputs','methodology','outputs','assumptions','references']]; print('PASS')" 2>&1 || echo "FAIL"
done
```

## Tests

```bash
uv run --no-project --with PyYAML --with pytest python -m pytest tests/reporting/test_generate_calc_report.py -v
```

## See also

- [data/dark-intel](https://github.com/vamseeachanta/data/tree/main/dark-intel) — dark intelligence archive with worked examples and reference data used in calculation reports
