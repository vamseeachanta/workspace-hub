---
name: instrument-data-allotrope-output-format-selection
description: 'Sub-skill of instrument-data-allotrope: Output Format Selection.'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# Output Format Selection

## Output Format Selection


**ASM JSON (default)** - Full semantic structure with ontology URIs
- Best for: LIMS systems expecting ASM, data lakes, long-term archival
- Validates against Allotrope schemas

**Flattened CSV** - 2D tabular representation
- Best for: Quick analysis, Excel users, systems without JSON support
- Each measurement becomes one row with metadata repeated

**Both** - Generate both formats for maximum flexibility
