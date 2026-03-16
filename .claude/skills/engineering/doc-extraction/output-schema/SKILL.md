---
name: doc-extraction-output-schema
description: 'Sub-skill of doc-extraction: Output Schema.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Output Schema

## Output Schema


Each extracted item follows this structure:

```yaml
- content_type: constants     # one of the 8 types
  source:
    document: "DNV-RP-B401"
    section: "3.4.6"
    page: 42
  data:
    name: "Initial coating breakdown factor"
    symbol: "f_ci"
    value: 0.05
    units: dimensionless
    applicability:
      coating_category: "I"
      description: "High quality >= 300 um epoxy"
  confidence: high            # high / medium / low
  extraction_notes: null
```
