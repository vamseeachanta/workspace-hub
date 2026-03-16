---
name: instrument-data-allotrope-calculated-data-handling
description: 'Sub-skill of instrument-data-allotrope: Calculated Data Handling.'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# Calculated Data Handling

## Calculated Data Handling


**IMPORTANT:** Separate raw measurements from calculated/derived values.

- **Raw data** -> `measurement-document` (direct instrument readings)
- **Calculated data** -> `calculated-data-aggregate-document` (derived values)

Calculated values MUST include traceability via `data-source-aggregate-document`:

```json
"calculated-data-aggregate-document": {
  "calculated-data-document": [{
    "calculated-data-identifier": "SAMPLE_B1_DIN_001",
    "calculated-data-name": "DNA integrity number",
    "calculated-result": {"value": 9.5, "unit": "(unitless)"},
    "data-source-aggregate-document": {
      "data-source-document": [{
        "data-source-identifier": "SAMPLE_B1_MEASUREMENT",
        "data-source-feature": "electrophoresis trace"
      }]
    }
  }]
}
```

**Common calculated fields by instrument type:**
| Instrument | Calculated Fields |
|------------|-------------------|
| Cell counter | Viability %, cell density dilution-adjusted values |
| Spectrophotometer | Concentration (from absorbance), 260/280 ratio |
| Plate reader | Concentrations from standard curve, %CV |
| Electrophoresis | DIN/RIN, region concentrations, average sizes |
| qPCR | Relative quantities, fold change |

See `references/field_classification_guide.md` for detailed guidance on raw vs. calculated classification.
