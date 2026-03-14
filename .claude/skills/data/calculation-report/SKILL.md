---
name: calculation-report
description: Generate professional engineering calculation reports from YAML — renders LaTeX formulas, interactive charts, and pass/fail outputs as HTML using the warm-parchment design system
version: "1.0.0"
triggers:
  - calculation report
  - calc report
  - engineering report
  - fatigue report
  - generate report from YAML
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

## Examples

- `examples/reporting/fatigue-pipeline-girth-weld.yaml` — pipeline girth weld fatigue
- `examples/reporting/fatigue-scr-touchdown.yaml` — SCR touchdown zone fatigue

## Schema

Full schema at `config/reporting/calculation-report-schema.yaml`.

## Tests

```bash
uv run --no-project --with PyYAML --with pytest python -m pytest tests/reporting/test_generate_calc_report.py -v
```
