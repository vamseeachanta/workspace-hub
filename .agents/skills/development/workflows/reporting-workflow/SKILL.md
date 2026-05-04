---
name: reporting-workflow
description: End-to-end workflow for generating reports from data, validating outputs,
  running report-focused tests, and iterating on HTML/interactive reporting artifacts.
version: 1.0.0
category: development
type: skill
trigger: manual
auto_execute: false
capabilities:
- report_generation
- report_validation
- html_verification
- regression_testing
- artifact_iteration
tools:
- Read
- Write
- Bash
- Grep
related_skills:
- html-report-verify
- engineering-report-generator
requires: []
tags:
- reporting
- html
- validation
- testing
- workflow
---

# Reporting Workflow

## When to Use

Use this skill when a task follows the common pattern:
1. inspect the input data/model/output expectations
2. run a report generator
3. open or validate the generated artifact
4. run targeted tests
5. refine the report if structure, visuals, or data mappings are wrong

Typical cases:
- benchmark reports
- engineering summary reports
- interactive HTML dashboards
- validation reports with plots/tables

## Core Workflow

### 1. Inspect Inputs and Existing Patterns

Read the generator, input schema, and one known-good output first.

```bash
# inspect generator and fixtures
rg -n "report|dashboard|html" examples/ tests/ scripts/
```

Check for:
- required inputs and file locations
- expected output paths
- linked assets (plots, CSS, JS, images)
- existing tests or snapshots

### 2. Generate the Report

Run the narrowest generator command possible.

```bash
# generic pattern
uv run --no-project python path/to/generator.py

# if shell wrapper exists
bash path/to/generate-report.sh
```

Capture:
- output file path
- warnings/errors
- whether the file was regenerated or unchanged

### 3. Verify the Artifact

For HTML outputs, use structural + visual verification.

Preferred checks:
- file exists and is non-empty
- expected headings/sections are present
- expected charts/tables rendered
- no obvious console/JS failures

If the output is HTML, pair with:
- `html-report-verify`

### 4. Run Report-Focused Tests

Use the smallest test slice that covers the report workflow.

```bash
uv run pytest tests/reporting/ -q
# or a targeted file/case
uv run pytest tests/path/test_report_x.py::test_generates_expected_sections -q
```

If no report test exists yet:
- add a focused regression test for the bug or missing section
- prefer structural assertions over brittle full-file diffs unless snapshots are already standard

### 5. Iterate on Generator / Template / Data Mapping

Common failure buckets:
- wrong data aggregation
- missing section wiring
- broken template variables
- invalid asset paths
- JS/chart rendering failures
- report generated but not linked into navigation/index pages

Fix one layer at a time:
- data extraction
- transformation
- template rendering
- final asset packaging

### 6. Re-run Validation

After each fix:
- regenerate
- re-run targeted tests
- re-verify final artifact

Do not stop at “generator exited 0” — confirm the report is actually correct.

## Recommended Validation Ladder

1. script exits successfully
2. output file exists
3. structural assertions pass
4. targeted tests pass
5. visual/HTML verification passes when relevant

## Test Integration Guidance

Prefer tests that assert:
- key section headings exist
- expected records/counts appear
- chart containers exist
- critical summary metrics match fixture inputs

Avoid overly fragile tests that fail on harmless formatting changes unless snapshot testing is already expected.

## Integration Notes

This skill complements:
- `html-report-verify` for visual/DOM verification
- `interactive-report-generator` for richer dashboard/report generation patterns
- `engineering-report-generator` for engineering-specific outputs

## Common Pitfalls

- regenerating without checking the output path
- trusting console-clean output without opening the report
- testing only generator internals instead of final artifact structure
- mixing data bugs and template bugs in one change
- forgetting to add regression coverage for a discovered report bug
