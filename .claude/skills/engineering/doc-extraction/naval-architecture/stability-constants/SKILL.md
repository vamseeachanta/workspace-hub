---
name: doc-extraction-naval-architecture-stability-constants
description: 'Sub-skill of doc-extraction-naval-architecture: Stability Constants
  (+4).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Stability Constants (+4)

## Stability Constants


Metacentric height and related parameters for intact and damage stability.

**Detection heuristics**:
- Keywords: "metacentric height", "GM", "GZ", "righting arm", "righting lever",
  "KB", "BM", "KG", "KM", "free surface correction"
- Symbols: GM, GM_t (transverse), GM_l (longitudinal), GZ, KB, BM, KM, KG
- Units: metres or feet
- Context: stability booklets, inclining experiment reports, loading conditions

**Key extraction fields**:
```yaml
- content_type: constants
  domain: naval_architecture
  sub_type: stability_constant
  data:
    name: "Transverse metacentric height"
    symbol: "GM_t"
    value: 1.85
    units: m
    applicability:
      loading_condition: "full load departure"
      free_surface_corrected: true
    source: "Stability booklet Section 3.2"
```

**GZ curve extraction** (from cross-curves or direct calculation):
- Detect heel angle vs righting arm tabulations
- Extract: angle[], GZ[], area_under_curve, maximum_GZ, angle_of_vanishing_stability
- Flag against IMO 2008 IS Code Part A criteria: GZ at 30 deg >= 0.20 m,
  area to 30 deg >= 0.055 m-rad, angle of max GZ >= 25 deg (see table below)


## Resistance Equations


Ship resistance prediction methods and empirical correlations.

**Detection heuristics**:
- Keywords: "resistance", "drag", "Holtrop", "ITTC", "friction line",
  "wave resistance", "form factor", "residuary resistance", "appendage"
- Symbols: R_T, R_F, R_W, R_APP, C_F, C_T, k (form factor), Fn (Froude number)
- Units: kN, N, or non-dimensional coefficients
- Context: resistance prediction reports, towing tank data, CFD validation

**Key extraction fields**:
```yaml
- content_type: equations
  domain: naval_architecture
  sub_type: resistance_equation
  data:
    name: "ITTC 1957 friction line"
    expression: "C_F = 0.075 / (log10(Re) - 2)^2"
    variables:
      - {symbol: C_F, name: "frictional resistance coefficient", units: dimensionless}
      - {symbol: Re, name: "Reynolds number", units: dimensionless}
    source: "ITTC 1957 Model-Ship Correlation Line"
    applicability:
      method: "ITTC-1957"
      flow_regime: "turbulent"
```

**Holtrop-Mennen method** — extract these specific parameters:
- Regression coefficients (c_1 through c_17)
- Form factor (1+k_1) components
- Wave resistance coefficient C_W
- Correlation allowance C_A
- Appendage resistance factors


## Hull Form Coefficients


Dimensionless ratios characterising hull geometry.

**Detection heuristics**:
- Keywords: "block coefficient", "prismatic coefficient", "midship coefficient",
  "waterplane coefficient", "hull form", "form coefficients"
- Symbols: Cb, Cp, Cm, Cwp, L/B, B/T, L/D
- Values: dimensionless, typically 0.3–0.9 for displacement vessels
- Context: hull form databases, general arrangement plans, lines drawings

**Key extraction fields**:
```yaml
- content_type: constants
  domain: naval_architecture
  sub_type: hull_form_coefficient
  data:
    name: "Block coefficient"
    symbol: "Cb"
    value: 0.82
    units: dimensionless
    applicability:
      vessel_type: "tanker"
      design_draft: true
    source: "Lines plan / hull definition"
```

**Hull form coefficient definitions** (screening heuristic ranges):
| Coefficient | Symbol | Definition | Typical range |
|-------------|--------|------------|---------------|
| Block | Cb | Displaced vol / (L × B × T) | 0.35–0.85 |
| Prismatic | Cp | Displaced vol / (A_m × L) | 0.55–0.80 |
| Midship | Cm | A_m / (B × T) | 0.85–0.99 |
| Waterplane | Cwp | A_wp / (L × B) | 0.65–0.90 |

Note: ranges are non-normative screening heuristics for extraction QA only.


## Hydrostatic Curves


Displacement, trim, and stability parameters as functions of draft.

**Detection heuristics**:
- Keywords: "hydrostatic curves", "hydrostatics", "displacement curve",
  "TPC", "MTC", "tonnes per centimetre", "moment to change trim"
- Pattern: table or graph with draft as independent variable
- Columns: draft, displacement, KB, BM, KM, TPC, MTC, LCB, LCF
- Units: metres (draft), tonnes (displacement), t/cm (TPC), t-m/cm (MTC)

**Key extraction fields**:
```yaml
- content_type: curves
  domain: naval_architecture
  sub_type: hydrostatic_curve
  data:
    title: "Hydrostatic curves"
    x_axis: {label: "Draft", units: m}
    columns:
      - {name: displacement, units: tonnes}
      - {name: KB, units: m}
      - {name: BM, units: m}
      - {name: KM, units: m}
      - {name: TPC, units: "t/cm"}
      - {name: MTC, units: "t-m/cm"}
      - {name: LCB, units: "m from AP"}
      - {name: LCF, units: "m from AP"}
    source: "Hydrostatic particulars table"
```


## IMO Stability Criteria


Mandatory and recommended stability criteria from IMO instruments.

**Detection heuristics**:
- Keywords: "IMO", "intact stability", "IS Code", "weather criterion",
  "severe wind and rolling", "SOLAS", "A.749"
- Pattern: criterion statement with threshold value and pass/fail check
- References: IMO Res. A.749(18), 2008 IS Code Part A/B, SOLAS Ch. II-1

**Key extraction fields**:
```yaml
- content_type: requirements
  domain: naval_architecture
  sub_type: imo_stability_criterion
  data:
    id: "IS-A-2.2.1"
    text: "Area under GZ curve up to 30 deg shall not be less than 0.055 m-rad"
    threshold:
      parameter: "GZ_area_0_30"
      operator: ">="
      value: 0.055
      units: "m-rad"
    standard_ref: "2008 IS Code Part A, Section 2.2.1"
    normative_strength: shall
```

**IMO intact stability criteria checklist** (2008 IS Code Part A):
| Criterion | Parameter | Threshold |
|-----------|-----------|-----------|
| 2.2.1 | Area under GZ to 30 deg | >= 0.055 m-rad |
| 2.2.2 | Area under GZ to 40 deg (or flood angle) | >= 0.090 m-rad |
| 2.2.3 | Area under GZ between 30 and 40 deg | >= 0.030 m-rad |
| 2.2.4 | GZ at 30 deg or greater | >= 0.200 m |
| 2.2.5 | Angle of maximum GZ | >= 25 deg |
| 2.2.6 | Initial GM | >= 0.150 m |
| 2.3 | Severe wind and rolling (weather criterion) | ratio >= 1.0 |
