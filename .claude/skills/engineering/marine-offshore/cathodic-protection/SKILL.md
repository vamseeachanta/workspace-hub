---
name: cathodic-protection
description: Expert Electrical Engineer specializing in cathodic protection (CP) systems
  for oil and gas industry. Use for CP system design, corrosion prevention, sacrificial
  anode calculations, impressed current systems, pipeline integrity, coating defects,
  and NACE/ISO standards compliance.
version: 1.2.0
updated: 2026-02-20
category: offshore-engineering
triggers:
- cathodic protection
- corrosion prevention
- sacrificial anode
- impressed current
- ICCP system
- SACP system
- pipeline CP
- anode design
- NACE standards
- ISO 15589
- DNV-RP-B401
- DNV-RP-F103
- ABS GN Ships
- ABS GN Offshore
- coating breakdown
- stray current
- fitness for service
- FFS assessment
- API 579
- corrosion damage assessment
- remaining life
see_also:
  - engineering/asset-integrity/fitness-for-service  # WRK-206: CP prevents corrosion; FFS assesses damage once it occurs
  - engineering/marine-offshore/risk-assessment
capabilities:
  - ABS_gn_ships_2018: Ship hull SACP design — bracelet/flush anodes, aluminium alloy, ABS GN Ships 2017
  - DNV_RP_F103_2010: Submarine pipeline SACP design — bracelet anodes, buried conditions, DNV-RP-F103 2010
  - DNV_RP_B401_offshore: Offshore fixed platform SACP — jacket/GBS structures, zonal design, DNV-RP-B401 2021
requires: []
---
# Cathodic Protection Skill

Expert guidance on cathodic protection (CP) systems for offshore platforms, subsea pipelines, storage tanks, and onshore oil and gas facilities.

## Version Metadata

```yaml
version: 1.2.0
python_min_version: '3.10'
compatibility:
  tested_python:
  - '3.10'
  - '3.11'
  - '3.12'
  - '3.13'
  os:
  - Windows
  - Linux
  - macOS
```

## Changelog

### [1.2.0] - 2026-02-20

**Added:**
- `DNV_RP_B401_offshore` route: Offshore fixed platform SACP per DNV-RP-B401 (2021 edition)
- Covers jacket structures, gravity-based structures, and topsides steel
- Zones: submerged (temp-dependent), splash, atmospheric
- Coating categories I–III and bare per B401-2021 Sec.3.4.6
- Anode types: flush-mounted, stand-off, bracelet (Dwight formula, Sec.4.9)

### [1.1.0] - 2026-02-20

**Fixed:**
- Corrected Python examples to use real `CathodicProtection().router(cfg)` API
- Added working ABS GN Ships and DNV-RP-F103 cfg examples with verified key names
- Added DNV-RP-F103 to standards table and triggers

**Removed:**
- Non-existent class imports (AnodeDesign, PipelineCP, CoatingAnalysis, ICCPDesign, etc.)
- MCP tool integration section (not applicable to engineering calculations)

### [1.0.0] - 2026-01-07

**Added:**
- Initial version metadata and dependency management


## When to Use

- CP system design (SACP and ICCP)
- Anode calculation and spacing
- Transformer rectifier unit sizing
- Pipeline CP design
- Coating breakdown assessment
- AC/DC interference analysis
- CP monitoring system design
- NACE/ISO/DNV compliance

## Domain Expertise

### Cathodic Protection Systems

| System Type | Applications |
|-------------|--------------|
| **SACP** (Sacrificial Anode) | Offshore structures, pipelines, short-term protection |
| **ICCP** (Impressed Current) | Long pipelines, complex structures, retrofit |
| **Hybrid** | Combined systems for optimal protection |

### Anode Materials

| Material | Application | Environment |
|----------|-------------|-------------|
| Al-Zn-In | Marine, seawater | Offshore, subsea |
| Magnesium | Soil, freshwater | Onshore pipelines |
| MMO (Mixed Metal Oxide) | ICCP anodes | All environments |
| Graphite | Deep well anodes | Soil, groundbeds |
| High-silicon iron | Groundbeds | Soil |

### Industry Standards

| Standard | Scope |
|----------|-------|
| **DNV-RP-F103** | Cathodic protection of submarine pipelines (galvanic anodes) |
| **DNV-RP-B401** | Cathodic protection design (offshore structures) |
| **ABS GN Ships** | Cathodic protection of ships |
| **ABS GN Offshore** | Cathodic protection of offshore structures |
| **NACE SP0169** | External corrosion control of pipelines |
| **NACE SP0176** | Corrosion control of steel fixed offshore platforms |
| **ISO 15589-2** | Cathodic protection of offshore pipelines |
| **API RP 651** | Cathodic protection of aboveground tanks |
| **SNAME T&R R-21** | Cathodic protection of marine service |

## Code Usage

The `CathodicProtection` class is the entry point. All calculations use a config-dict
(`cfg`) passed to `router()`. The router dispatches on `cfg["inputs"]["calculation_type"]`.

**Implemented routes:**
- `ABS_gn_ships_2018` — ship hull SACP
- `DNV_RP_F103_2010` — submarine pipeline SACP
- `DNV_RP_B401_offshore` — offshore fixed platform SACP

### Example: Ship Hull (ABS GN Ships 2018)

```python
from digitalmodel.infrastructure.common.cathodic_protection import CathodicProtection

cfg = {
    "inputs": {
        "calculation_type": "ABS_gn_ships_2018",
        "design_data": {
            "design_life": 5,               # years
            "seawater_max_temperature": 20, # Celsius
        },
        "environment": {
            "seawater": {"resistivity": {"input": 0.2547}}  # ohm·m
        },
        "structure": {
            "steel_total_area": 1000.0,                  # m2
            "area_coverage": 100.0,                      # % coated
            "coating_initial_breakdown_factor": 2.0,     # %/yr initial
            "coating_initial_breakdown_duration": 2.0,   # years
            "coating_yearly_breakdown_factor": 3.0,      # %/yr after initial
            "coating_breakdown_factor_max": 2.0,         # max CBF
        },
        "design_current": {
            "coated_steel_mA_m2": 13.5,
            "uncoated_steel_mA_m2": 200.0,
        },
        "anode": {
            "material": "aluminium",
            "protection_potential": 0.8,            # V
            "closed_circuit_anode_potential": -1.09, # V vs Ag/AgCl
            "anode_Utilisation_factor": 0.825,
            "physical_properties": {"net_weight": 29.0},  # kg
            "geometry": {
                "type": "long_flush",  # long_flush, short_flush, bracelet
                "length_m": 0.65,
                "width_m": 0.125,
            },
        },
    }
}

cp = CathodicProtection()
cp.ABS_gn_ships_2018(cfg)

results = cfg["cathodic_protection"]
print(f"Design life:        {results['design_life']} years")
print(f"Mean current demand: {results['current_demand_A']['totals']['mean']:.2f} A")
print(f"Anode count:        {results['anode_requirements']['anode_count']}")
print(f"Driving voltage:    {results['anode_performance']['driving_voltage_V']:.3f} V")
```

### Example: Submarine Pipeline (DNV-RP-F103 2010)

```python
from digitalmodel.infrastructure.common.cathodic_protection import CathodicProtection

cfg = {
    "inputs": {
        "calculation_type": "DNV_RP_F103_2010",
        "design_data": {
            "design_life": 25.0,  # years
        },
        "pipeline": {
            "outer_diameter_m": 0.6096,              # 24-inch OD
            "length_m": 5000.0,
            "wall_thickness_m": 0.020,
            "coating_type": "FBE",                   # FBE, 3LPE, 3LPP
            "coating_quality": "good",               # good, average, poor
            "burial_condition": "buried",
            "coating_initial_breakdown_pct": 0.5,
            "coating_initial_breakdown_duration": 1.0,  # years
            "coating_yearly_breakdown_pct": 1.5,
        },
        "environment": {
            "seawater_temperature_C": 10.0,
            "soil_resistivity_ohm_m": 50.0,
        },
        "anode": {
            "material": "aluminium",
            "closed_circuit_anode_potential": -1.05,  # V vs Ag/AgCl
            "anode_Utilisation_factor": 0.85,
            "physical_properties": {"net_weight": 120.0},  # kg
        },
    }
}

cp = CathodicProtection()
result = cp.router(cfg)

r = result["results"]
print(f"Anode count:   {r['anode_requirements']['anode_count']}")
print(f"Anode spacing: {r['anode_spacing_m']:.1f} m")
print(f"Mean current:  {r['current_demand_A']['mean']:.2f} A")
```

### Example: Offshore Fixed Platform (DNV-RP-B401 2021)

```python
from digitalmodel.infrastructure.common.cathodic_protection import CathodicProtection

cfg = {
    "inputs": {
        "calculation_type": "DNV_RP_B401_offshore",
        "design_data": {
            "design_life": 25.0,           # years
            "structure_type": "jacket",    # jacket | gravity_based | topsides
        },
        "structure": {
            "zones": [
                {"zone": "submerged",    "area_m2": 5000.0, "coating_category": "I"},
                {"zone": "splash",       "area_m2":  300.0, "coating_category": "III"},
                {"zone": "atmospheric",  "area_m2":  200.0, "coating_category": "I"},
            ]
        },
        "environment": {
            "seawater_temperature_C":      10.0,   # °C — drives submerged current density
            "seawater_resistivity_ohm_m":  0.30,   # Ω·m — North Sea typical
        },
        "anode": {
            "material":                  "aluminium",   # aluminium | zinc
            "type":                      "stand_off",   # flush_mounted | stand_off | bracelet
            "individual_anode_mass_kg":   200.0,        # kg per anode
            "utilization_factor":          0.85,        # B401-2021 Sec.3.8 typical
            "length_m":                    1.0,         # for Dwight resistance formula
            "radius_m":                    0.05,        # equivalent anode radius
        }
    }
}

cp = CathodicProtection()
result = cp.router(cfg)

r = result["results"]
print(f"Standard:          {r['standard']}")
print(f"Design life:       {r['design_life_years']} years")
print(f"Total current:     {r['current_demand_A']['total_mean_A']:.2f} A")
print(f"Anode count:       {r['anode_requirements']['anode_count']}")
print(f"Anode mass total:  {r['anode_requirements']['total_mass_kg']:.1f} kg")
print(f"CP adequate:       {r['current_output_verification']['adequate']}")
```

**Key outputs:**
| Key | Description |
|-----|-------------|
| `results.standard` | `"DNV-RP-B401-2021"` |
| `results.current_demand_A.total_mean_A` | Total mean current demand (A) across all zones |
| `results.anode_requirements.anode_count` | Number of anodes required |
| `results.anode_requirements.total_mass_kg` | Total anode mass required (kg) |
| `results.current_output_verification.adequate` | True if N×I_output ≥ I_design |

**Coating categories (B401-2021 Sec.3.4.6):**
| Category | Description | f_ci | k (per yr) |
|----------|-------------|------|-----------|
| I | High quality ≥300 μm epoxy | 0.05 | 0.020 |
| II | Anti-friction thin film (PTFE, new 2021) | 0.10 | 0.030 |
| III | Standard quality paint system | 0.25 | 0.050 |
| bare | No coating | 1.00 | 0.000 |

**References:** DNV-RP-B401-2021 Sections 3.3, 3.4, 4.9

### Using router() vs direct method call

```python
# router() dispatches by calculation_type — recommended
result = cp.router(cfg)

# Direct call — same result
cp.ABS_gn_ships_2018(cfg)      # results in cfg["cathodic_protection"]
cp.DNV_RP_F103_2010(cfg)       # results in cfg["results"]
```

Note: ABS route writes to `cfg["cathodic_protection"]`; DNV route writes to `cfg["results"]`.

## Design Workflow

### CP System Design Process

1. **Environment Assessment**
   - Soil/water resistivity
   - Temperature
   - Oxygen content
   - Biological activity

2. **Current Requirement**
   - Surface area calculation
   - Coating efficiency
   - Current density selection

3. **System Selection**
   - SACP vs ICCP decision
   - Hybrid considerations

4. **Component Design**
   - Anode sizing and distribution
   - Cable sizing
   - TRU specification (ICCP)

5. **Interference Analysis**
   - AC/DC interference
   - Stray current
   - Galvanic interaction

6. **Monitoring Design**
   - Reference electrode placement
   - Test point locations
   - Remote monitoring

## Best Practices

1. **Conservatism**: Apply appropriate safety factors
2. **Standards Compliance**: Follow NACE/ISO requirements
3. **Design Life**: Consider coating degradation over time
4. **Monitoring**: Design for long-term performance tracking
5. **Documentation**: Record all assumptions and calculations

## Related Skills

- [structural-analysis](../structural-analysis/SKILL.md) - Structural integrity
- [mooring-design](../mooring-design/SKILL.md) - Mooring system protection
- [fatigue-analysis](../fatigue-analysis/SKILL.md) - Corrosion-fatigue interaction

## References

- NACE International Standards
- ISO 15589-2: Cathodic Protection of Offshore Pipelines
- DNV-RP-F103 (2003, 2010): Cathodic Protection of Submarine Pipelines
- DNV-RP-B401 (2005, 2011, 2021): Cathodic Protection Design
- ABS GN Ships 2017 (289): Cathodic Protection of Ships
- ABS GN Offshore Structures 2018 (306): Cathodic Protection of Offshore Structures
- SNAME T&R R-21: Cathodic Protection of Marine Service
- Code: `digitalmodel/src/digitalmodel/infrastructure/common/cathodic_protection.py`
- Tests: `digitalmodel/tests/specialized/cathodic_protection/`

---

## Version History

- **1.2.0** (2026-02-20): Added DNV_RP_B401_offshore route; B401-2021 coating categories I–III; zonal current demand; Dwight anode resistance
- **1.1.0** (2026-02-20): Fixed examples to use real CathodicProtection().router(cfg) API; added DNV-RP-F103 to standards table
- **1.0.0** (2025-01-02): Initial release from agents/cathodic-protection-engineer.md
