---
name: doc-extraction-unit-detection-and-normalization
description: 'Sub-skill of doc-extraction: Unit Detection and Normalization (+4).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Unit Detection and Normalization (+4)

## Unit Detection and Normalization


Recognize units in parentheses, brackets, or inline: `(m/s²)`, `[ksi]`,
`N/mm²`. Normalize to a canonical form:

| Input variants | Canonical |
|---------------|-----------|
| `ksi`, `KSI` | `ksi` |
| `N/mm²`, `MPa` | `MPa` |
| `mA/m²`, `mA/m2` | `mA/m²` |
| `°C`, `deg C` | `°C` |
| `lb/ft`, `lbs/ft` | `lb/ft` |

Flag SI vs imperial vs field units. Prefer SI in output; keep original as
`units_original`.


## Standards Reference Parsing


Parse references like `DNV-RP-B401 Section 3.4.6` into structured form:

```yaml
standard_ref:
  body: DNV
  document: RP-B401
  edition: null         # null unless explicitly stated in source text
  edition_inferred: 2021  # set only when edition can be inferred; null otherwise
  section: 3.4.6
  table: null
  figure: null
  raw: "DNV-RP-B401 Section 3.4.6"
```

**Inference rule**: `edition` must be null unless the source text explicitly
states the year. Use `edition_inferred` only when surrounding context (title
page, header, or adjacent reference) provides strong evidence; never guess.

Common patterns:
- `DNV-RP-XXXX Sec N.N.N` / `Section N.N` / `Table N-N` / `Figure N-N`
- `API RP NNX Section N` / `API 579-1 Part N`
- `ASME BPVC Section VIII Div 2`
- `ISO NNNNN-N:YYYY Clause N.N`


## Safety and Design Factor Identification


Flag values tagged as safety factors, design factors, or usage factors:
- Keywords: "safety factor", "design factor", "utilisation factor", "usage factor"
- Often dimensionless ratios between 0 and 10
- Extract: {name, value, standard_ref, applicability}


## Material Property Recognition


Detect material properties in text or tables:
- Yield strength (SMYS), tensile strength (SMTS), Young's modulus
- Density, thermal expansion coefficient, Poisson's ratio
- Fatigue S-N curve parameters
- Extract: {property, value, units, material_grade, temperature, standard_ref}


## Condition and Applicability Tagging


Many values have applicability constraints. Tag extracted items with:
- Temperature range
- Depth/pressure range
- Material grade or category
- Environmental condition (seawater, air, buried)
- Service life assumptions
