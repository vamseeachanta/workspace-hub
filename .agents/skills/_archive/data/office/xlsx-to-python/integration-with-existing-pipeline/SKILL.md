---
name: xlsx-to-python-integration-with-existing-pipeline
description: 'Sub-skill of xlsx-to-python: Integration with Existing Pipeline.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Integration with Existing Pipeline

## Integration with Existing Pipeline


| Component | How This Skill Integrates |
|-----------|--------------------------|
| `parsers/xlsx.py` | Existing parser handles values; this skill adds formula layer |
| `parsers/formula_xlsx.py` | New parser created by WRK-1247 using patterns from this skill |
| `deep_extract.py` | Extended with formula extraction path for XLSX files |
| `dark-intelligence-workflow` | Step 2 (Extract) uses this skill's extraction pipeline |
| `calculation-report` | Step 7 output follows calc-report YAML schema |
| `legal-sanity-scan` | HARD GATE: must pass before archival |
