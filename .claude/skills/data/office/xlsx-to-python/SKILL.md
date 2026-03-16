---
name: xlsx-to-python
description: "Convert Excel calculation spreadsheets to Python code \u2014 extract\
  \ formulas, build dependency graphs, generate pytest tests using cell values as\
  \ assertions, and produce dark-intelligence archive YAMLs.\n"
version: 1.0.0
category: data
type: skill
trigger: manual
auto_execute: false
capabilities:
- formula_extraction
- vba_macro_extraction
- dependency_graph_building
- named_range_mapping
- calculation_chain_analysis
- test_generation_from_cell_values
- dark_intelligence_archive
- calc_report_generation
tools:
- Read
- Write
- Edit
- Bash
- Grep
- Glob
related_skills:
- openpyxl
- dark-intelligence-workflow
- calculation-report
- doc-intelligence-promotion
triggers:
- xlsx to python
- excel to python
- extract formulas from excel
- convert spreadsheet to code
- xlsx formula extraction
tags:
- excel
- xlsx
- formulas
- python
- tdd
- dark-intelligence
scripts_exempt: true
see_also:
- xlsx-to-python-core-principle-excel-values-test-data
- xlsx-to-python-recommended-stack
- xlsx-to-python-openpyxl-limitation
- xlsx-to-python-step-1-dual-pass-loading
- xlsx-to-python-step-6-calculation-block-detection
- xlsx-to-python-test-assertion-patterns-by-data-type
- xlsx-to-python-dark-intelligence-archive-generation
- xlsx-to-python-using-formulas-for-complex-workbooks
- xlsx-to-python-why-parametric-variations-are-required
- xlsx-to-python-research-finding-no-existing-library-does-this
- xlsx-to-python-integration-with-existing-pipeline
- xlsx-to-python-checklist
---

# Xlsx To Python

## When to Use

- Porting engineering calculations from Excel to Python
- Extracting calculation methodology from legacy spreadsheets
- Building dark-intelligence archives from XLSX files
- Any time a spreadsheet contains formulas that should become code

## Sub-Skills

- [Core Principle: Excel Values = Test Data](core-principle-excel-values-test-data/SKILL.md)
- [Recommended Stack (+2)](recommended-stack/SKILL.md)
- [openpyxl Limitation (+3)](openpyxl-limitation/SKILL.md)
- [Step 1 — Dual-Pass Loading (+5)](step-1-dual-pass-loading/SKILL.md)
- [Step 6 — Calculation Block Detection](step-6-calculation-block-detection/SKILL.md)
- [Test Assertion Patterns by Data Type (+1)](test-assertion-patterns-by-data-type/SKILL.md)
- [Dark Intelligence Archive Generation](dark-intelligence-archive-generation/SKILL.md)
- [Using `formulas` for Complex Workbooks](using-formulas-for-complex-workbooks/SKILL.md)
- [Why Parametric Variations Are Required (+4)](why-parametric-variations-are-required/SKILL.md)
- [Research Finding: No Existing Library Does This (+5)](research-finding-no-existing-library-does-this/SKILL.md)
- [Integration with Existing Pipeline](integration-with-existing-pipeline/SKILL.md)
- [Checklist](checklist/SKILL.md)
