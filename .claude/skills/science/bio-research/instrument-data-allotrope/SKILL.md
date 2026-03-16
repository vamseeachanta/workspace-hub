---
name: instrument-data-allotrope
description: Convert laboratory instrument output files (PDF, CSV, Excel, TXT) to
  Allotrope Simple Model (ASM) JSON format or flattened 2D CSV for LIMS systems and
  data lakes.
version: 1.0.0
category: science
last_updated: 2026-02-03
source: https://github.com/anthropics/knowledge-work-plugins
related_skills:
- single-cell-rna-qc
- scvi-tools
- nextflow-pipelines
- clinical-trial-protocol
- scientific-problem-selection
capabilities: []
requires: []
see_also:
- instrument-data-allotrope-workflow-overview
- instrument-data-allotrope-output-format-selection
- instrument-data-allotrope-calculated-data-handling
- instrument-data-allotrope-validation
- instrument-data-allotrope-supported-instruments
- instrument-data-allotrope-tier-1-native-allotropy-parsing-preferred
- instrument-data-allotrope-pre-parsing-checklist
- instrument-data-allotrope-common-mistakes-to-avoid
- instrument-data-allotrope-code-export-for-data-engineers
- instrument-data-allotrope-file-structure
- instrument-data-allotrope-example-1-vi-cell-blu-file
- instrument-data-allotrope-installing-allotropy
tags: []
scripts_exempt: true
---

# Instrument Data Allotrope

## Quick Start

```python
# Install requirements first
pip install allotropy pandas openpyxl pdfplumber --break-system-packages

# Core conversion
from allotropy.parser_factory import Vendor
from allotropy.to_allotrope import allotrope_from_file

# Convert with allotropy
asm = allotrope_from_file("instrument_data.csv", Vendor.BECKMAN_VI_CELL_BLU)
```

## Sub-Skills

- [Workflow Overview](workflow-overview/SKILL.md)
- [Output Format Selection](output-format-selection/SKILL.md)
- [Calculated Data Handling](calculated-data-handling/SKILL.md)
- [Validation](validation/SKILL.md)
- [Supported Instruments](supported-instruments/SKILL.md)
- [Tier 1: Native allotropy parsing (PREFERRED) (+2)](tier-1-native-allotropy-parsing-preferred/SKILL.md)
- [Pre-Parsing Checklist](pre-parsing-checklist/SKILL.md)
- [Common Mistakes to Avoid](common-mistakes-to-avoid/SKILL.md)
- [Code Export for Data Engineers](code-export-for-data-engineers/SKILL.md)
- [File Structure](file-structure/SKILL.md)
- [Example 1: Vi-CELL BLU file (+2)](example-1-vi-cell-blu-file/SKILL.md)
- [Installing allotropy (+2)](installing-allotropy/SKILL.md)
