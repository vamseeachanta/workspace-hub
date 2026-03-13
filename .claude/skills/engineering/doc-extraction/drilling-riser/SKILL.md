---
name: doc-extraction-drilling-riser
description: >
  Layer 3 domain sub-skill for extracting drilling riser data from API RP 16Q,
  DNV-RP-C205, and riser analysis reports. Provides detection heuristics for
  VIV parameters, kill/choke line specs, and BOP stack configurations.
version: 1.0.0
updated: 2026-03-12
category: engineering
parent_skill: engineering/doc-extraction
triggers:
  - riser extraction
  - drilling riser data
  - BOP extraction
  - riser stack-up extraction
  - VIV parameter extraction
related_skills:
  - engineering/doc-extraction
  - engineering/marine-offshore/viv-analysis
  - engineering/marine-offshore/catenary-riser
capabilities:
  - viv-parameter-extraction
  - bop-configuration-extraction
  - kill-choke-line-extraction
  - riser-stack-up-extraction
requires: []
tags: []
---

# Drilling Riser Document Extraction Sub-Skill

Domain-specific extraction heuristics for drilling riser documents, aligned
with `typical_riser_stack_up_calculations.py` and the VIV analysis skill.

## When to Use

- Extracting data from API RP 16Q (Marine Drilling Riser Systems)
- Processing riser analysis reports or stack-up calculations
- Ingesting VIV assessment data from riser studies
- Extracting BOP configuration data from well control documents
- Building riser component databases from manufacturer specs

## Source Code Alignment

Extracted data should align with existing module structures:

| Module | Relevant data |
|--------|---------------|
| `typical_riser_stack_up_calculations.py` | Joint dimensions, weights, stack-up sequence |
| VIV analysis skill | Strouhal number, reduced velocity, mode shapes |

## Drilling Riser Content Types

### VIV Parameters

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
| Max cross-flow A/D | 1.0–1.5 | Empirical |

**Mode shape extraction**:
- Detect mode number, natural frequency, wavelength
- Boundary conditions: tension-controlled, pinned-pinned, fixed-fixed
- Added mass coefficient (C_a) by proximity to seabed

### Kill and Choke Line Specifications

Auxiliary line properties for well control.

**Detection heuristics**:
- Keywords: "kill line", "choke line", "auxiliary line", "bore"
- Pattern: table with ID, OD, pressure rating, material grade columns
- Units: inches (ID/OD), psi or MPa (pressure), ksi (yield)
- Often in riser stack-up tables or well control equipment specs

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

### BOP Stack Configurations

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
    source: "API RP 16Q Section 5"
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

### Riser Stack-Up Data

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

## Validation Rules

When extracting drilling riser data, validate against known ranges:

| Parameter | Valid range | Flag if outside |
|-----------|------------|----------------|
| Strouhal number | 0.1 – 0.3 | Warning |
| Riser joint length | 40 – 90 ft | Warning |
| Kill/choke working pressure | 5,000 – 25,000 psi | Warning |
| BOP stack height | 15 – 60 ft | Warning |
| Riser OD | 18 – 24 inches | Warning |
| Water depth for riser | 100 – 12,000 ft | Warning |

## Standards Reference

| Standard | Scope |
|----------|-------|
| API RP 16Q | Marine drilling riser systems — design, selection, operation |
| DNV-RP-C205 | Environmental conditions and environmental loads |
| API STD 53 | BOP equipment systems for drilling wells |
| API Spec 16R | Marine drilling riser couplings |
| DNV-RP-F204 | Riser fatigue |
| DNV-OS-E101 | Drilling plant |

## Related Skills

- [viv-analysis](../../marine-offshore/viv-analysis/SKILL.md) — VIV assessment
- [catenary-riser](../../marine-offshore/catenary-riser/SKILL.md) — Riser configuration
- [structural-analysis](../../marine-offshore/structural-analysis/SKILL.md) — Stress checks
