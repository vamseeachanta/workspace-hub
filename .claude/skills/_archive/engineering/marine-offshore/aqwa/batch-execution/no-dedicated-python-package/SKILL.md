---
name: aqwa-batch-execution-no-dedicated-python-package
description: 'Sub-skill of aqwa-batch-execution: No Dedicated Python Package.'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# No Dedicated Python Package

## No Dedicated Python Package


The PyAnsys metapackage (33+ packages) does **not** include a dedicated AQWA client
as of 2025 R1. Automate AQWA via:
- `subprocess` + direct `.DAT` / `Aqwa` executable (recommended for standalone)
- `subprocess` + `runwb2` (for Workbench projects)
- `.LIS` / `.AH1` text parsing for results extraction
