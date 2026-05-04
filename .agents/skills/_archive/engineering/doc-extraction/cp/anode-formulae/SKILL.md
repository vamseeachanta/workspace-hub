---
name: doc-extraction-cp-anode-formulae
description: 'Sub-skill of doc-extraction-cp: Anode Formulae (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Anode Formulae (+3)

## Anode Formulae


Equations for anode mass, current output, resistance, and utilisation.

**Detection heuristics**:
- Keywords: "anode mass", "current capacity", "utilisation factor", "anode resistance"
- Symbols: `M_a`, `C_a`, `u`, `R_a`, `I_a`
- Units: kg, Ah/kg, ohm, ampere
- Geometric terms: "length", "radius", "cross-section"

**Key extraction fields**:
```yaml
- content_type: equations
  domain: cathodic_protection
  sub_type: anode_formula
  data:
    name: "Anode current output"
    expression: "I_a = (E_c - E_a) / R_a"
    variables:
      - {symbol: I_a, name: "anode current output", units: A}
      - {symbol: E_c, name: "structure protection potential", units: V}
      - {symbol: E_a, name: "anode closed-circuit potential", units: V}
      - {symbol: R_a, name: "anode resistance", units: ohm}
    source: "DNV-RP-B401 Section 4.3"
```

**Anode resistance formulae** (by geometry):
- Flush-mounted: McCoy's formula — `R = ρ / (2π × S)` where S = shape factor
- Stand-off: Dwight's formula — depends on length/radius ratio
- Bracelet: Peterson's formula — for cylindrical anodes on pipelines


## Coating Breakdown Factors


Linear degradation model: `f_c(t) = f_ci + k × t`, clamped at 1.0.

**Detection heuristics**:
- Keywords: "coating breakdown", "breakdown factor", "coating category"
- Symbols: `f_c`, `f_ci`, `k`, `t`
- Pattern: table with Category I/II/III rows, f_ci and k columns
- Section reference: typically Section 3.4 in B401

**Key extraction fields**:
```yaml
- content_type: constants
  domain: cathodic_protection
  sub_type: coating_breakdown
  data:
    name: "Coating Category I breakdown parameters"
    values:
      f_ci: {value: 0.05, units: dimensionless, description: "Initial breakdown factor"}
      k: {value: 0.020, units: "1/year", description: "Degradation rate"}
    applicability:
      category: "I"
      description: "High quality >= 300 um epoxy"
    source: "DNV-RP-B401 Section 3.4.6"
```

**Category definitions** (B401-2021):
| Category | f_ci | k | Description |
|----------|------|---|-------------|
| I | 0.05 | 0.020 | High quality ≥300 μm epoxy |
| II | 0.10 | 0.030 | Anti-friction thin film / PTFE |
| III | 0.25 | 0.050 | Standard quality paint system |
| bare | 1.00 | 0.000 | No coating — bare steel |


## Design Life Tables


Design life parameters for CP system sizing.

**Detection heuristics**:
- Keywords: "design life", "service life", "lifetime", "years"
- Pattern: table with years in one column, other parameters varying
- Often cross-referenced with temperature and environmental severity
- Section reference: typically early sections of B401/F103

**Key extraction fields**:
```yaml
- content_type: tables
  domain: cathodic_protection
  sub_type: design_life
  data:
    title: "CP design life parameters"
    columns: [design_life_years, mean_current_density, final_current_density]
    applicability:
      temperature_band: ">12-17°C"
      environment: "seawater"
    source: "DNV-RP-B401 Table 3-2"
```


## Current Density Values


Design current densities by zone and environmental condition.

**Detection heuristics**:
- Keywords: "current density", "mean current density", "initial current density", "final current density"
- Units: mA/m², A/m²
- Pattern: table indexed by zone (submerged/splash/atmospheric) and temperature
- Distinction between coated and bare steel values

**Key extraction fields**:
```yaml
- content_type: constants
  domain: cathodic_protection
  sub_type: current_density
  data:
    name: "Mean design current density — submerged, coated"
    current_density_type: mean   # mean | initial | final
    value: 0.060
    units: "A/m²"
    applicability:
      zone: submerged
      temperature_range: ">12-17°C"
      surface_condition: coated
    source: "DNV-RP-B401 Table 3-1"
```

**Structured discriminator**: Always include `current_density_type` (one of
`mean`, `initial`, `final`) — do not encode the type only in the `name` field.

**Zone classification**:
| Zone | Description | Temperature dependency |
|------|-------------|----------------------|
| Submerged | Below splash zone, permanently immersed | Yes — 4 temperature bands |
| Splash | Tidal and wave action zone | No — fixed values |
| Atmospheric | Above splash, exposed to marine atmosphere | No — fixed values |
