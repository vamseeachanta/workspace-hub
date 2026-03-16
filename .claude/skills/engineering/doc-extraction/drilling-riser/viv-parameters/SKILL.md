---
name: doc-extraction-drilling-riser-viv-parameters
description: 'Sub-skill of doc-extraction-drilling-riser: VIV Parameters (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# VIV Parameters (+3)

## VIV Parameters


Vortex-induced vibration parameters for riser fatigue assessment.

**Detection heuristics**:
- Keywords: "vortex-induced vibration", "VIV", "Strouhal number", "reduced velocity",
  "lock-in", "mode shape", "vortex shedding"
- Symbols: `St`, `V_r`, `f_s`, `f_n`, `A/D`
- Units: Hz, m/s, dimensionless
- Often in sections titled "VIV Assessment" or "Fatigue from VIV"

**Key extraction fields**:
```yaml
- content_type: constants
  domain: drilling_riser
  sub_type: viv_parameter
  data:
    name: "Strouhal number — smooth cylinder"
    symbol: "St"
    value: 0.2
    units: dimensionless
    applicability:
      surface: "smooth"
      reynolds_range: "subcritical"
    source: "DNV-RP-C205 Section 9.3"
```

**VIV parameter reference values**:
| Parameter | Typical value | Source |
|-----------|--------------|--------|
| Strouhal number (smooth) | 0.2 | DNV-RP-C205 |
| Strouhal number (rough) | 0.21 | DNV-RP-C205 |
| Cross-flow VIV onset V_r | 4–8 | DNV-RP-C205 |
| In-line VIV onset V_r | 1–3.5 | DNV-RP-C205 |
| Lock-in V_r range | 5–7 | DNV-RP-C205 |
| Max cross-flow A/D (screening heuristic) | 1.0–1.5 | Empirical, non-normative |

**Mode shape extraction**:
- Detect mode number, natural frequency, wavelength
- Boundary conditions: tension-controlled, pinned-pinned, fixed-fixed
- Added mass coefficient (C_a) by proximity to seabed


## Kill and Choke Line Specifications


Auxiliary line properties for well control.

**Detection heuristics**:
- Keywords: "kill line", "choke line", "auxiliary line", "bore"
- Pattern: table with ID, OD, pressure rating, material grade columns
- Units: inches (ID/OD), psi or MPa (pressure), ksi (yield)
- Often in riser stack-up tables or well control equipment specs
- Note: values are edition- and vendor-dependent; always capture source edition

**Key extraction fields**:
```yaml
- content_type: tables
  domain: drilling_riser
  sub_type: kill_choke_line
  data:
    title: "Kill/choke line specifications"
    columns:
      - {name: line_type, units: null}
      - {name: ID, units: inches}
      - {name: OD, units: inches}
      - {name: working_pressure, units: psi}
      - {name: burst_pressure, units: psi}
      - {name: collapse_pressure, units: psi}
      - {name: material_grade, units: null}
    source: "API RP 16Q Table 4"
```

**Typical kill/choke line parameters**:
| Parameter | Kill line | Choke line |
|-----------|-----------|------------|
| Nominal bore | 3" – 4.5" | 3" – 4.5" |
| Working pressure | 10,000 – 15,000 psi | 10,000 – 15,000 psi |
| Material | AISI 4130, 4140 | AISI 4130, 4140 |
| Connection | Integral flanged | Integral flanged |


## BOP Stack Configurations


Blowout preventer stack layout and component specifications.

**Detection heuristics**:
- Keywords: "BOP", "blowout preventer", "annular preventer", "pipe ram",
  "blind ram", "shear ram", "stack height", "wellhead connector"
- Pattern: vertical stack-up diagram or table listing components top-to-bottom
- Units: inches (bore), feet or meters (height), tons (weight)
- Often accompanied by schematic drawings

**Key extraction fields**:
```yaml
- content_type: tables
  domain: drilling_riser
  sub_type: bop_configuration
  data:
    title: "BOP stack configuration — 18-3/4 inch, 15K"
    components:
      - {position: 1, type: "annular preventer", bore: "18.75 in", rating: "10,000 psi"}
      - {position: 2, type: "annular preventer", bore: "18.75 in", rating: "10,000 psi"}
      - {position: 3, type: "pipe ram", bore: "18.75 in", rating: "15,000 psi"}
      - {position: 4, type: "blind/shear ram", bore: "18.75 in", rating: "15,000 psi"}
      - {position: 5, type: "pipe ram", bore: "18.75 in", rating: "15,000 psi"}
      - {position: 6, type: "casing shear ram", bore: "18.75 in", rating: "15,000 psi"}
    stack_height: {value: 35, units: feet}
    dry_weight: {value: 400, units: tons}
    source: "API STD 53 Section 5"  # BOP config authority is API STD 53, not API RP 16Q
```

**BOP component types**:
| Component | Function |
|-----------|----------|
| Annular preventer | Seals around any tubular or open hole |
| Pipe ram | Seals around specific pipe OD |
| Blind ram | Seals open hole (no pipe) |
| Shear ram | Cuts pipe and seals |
| Casing shear ram | Cuts casing strings |
| Wellhead connector | Connects BOP to wellhead |


## Riser Stack-Up Data


Joint-by-joint riser assembly data.

**Detection heuristics**:
- Keywords: "stack-up", "riser joint", "pup joint", "flex joint", "telescopic joint"
- Pattern: table with component name, length, weight, buoyancy columns
- Units: feet or meters (length), kips or tonnes (weight)
- Sequential ordering from mudline to surface

**Key extraction fields**:
```yaml
- content_type: tables
  domain: drilling_riser
  sub_type: riser_stack_up
  data:
    title: "Drilling riser stack-up"
    columns:
      - {name: component, units: null}
      - {name: length, units: ft}
      - {name: dry_weight, units: kips}
      - {name: buoyant_weight, units: kips}
      - {name: OD, units: inches}
      - {name: ID, units: inches}
    source: "Riser analysis report Section 3"
```
