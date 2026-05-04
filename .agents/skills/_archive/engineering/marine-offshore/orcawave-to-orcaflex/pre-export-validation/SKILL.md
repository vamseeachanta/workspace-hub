---
name: orcawave-to-orcaflex-pre-export-validation
description: 'Sub-skill of orcawave-to-orcaflex: Pre-Export Validation.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Pre-Export Validation

## Pre-Export Validation


```python
from digitalmodel.diffraction.output_validator import OrcaFlexExportValidator

# Validate export data
validator = OrcaFlexExportValidator()

# Run all checks
validation = validator.validate_for_orcaflex(
    data=unified_data,
    checks=[

*See sub-skills for full details.*
