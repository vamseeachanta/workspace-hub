---
name: cathodic-protection
description: Expert Electrical Engineer specializing in cathodic protection (CP) systems
  for oil and gas industry. Use for CP system design, corrosion prevention, sacrificial
  anode calculations, impressed current systems, pipeline integrity, coating defects,
  and NACE/ISO standards compliance.
type: reference
version: 1.2.0
updated: 2026-02-20
category: engineering
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
capabilities:
- ABS_gn_ships_2018: "Ship hull SACP design \u2014 bracelet/flush anodes, aluminium\
    \ alloy, ABS GN Ships 2017"
- DNV_RP_F103_2010: "Submarine pipeline SACP design \u2014 bracelet anodes, buried\
    \ conditions, DNV-RP-F103 2010"
- DNV_RP_B401_offshore: "Offshore fixed platform SACP \u2014 jacket/GBS structures,\
    \ zonal design, DNV-RP-B401 2021"
requires: []
tags: []
scripts_exempt: true
---

# Cathodic Protection

## When to Use

- CP system design (SACP and ICCP)
- Anode calculation and spacing
- Transformer rectifier unit sizing
- Pipeline CP design
- Coating breakdown assessment
- AC/DC interference analysis
- CP monitoring system design
- NACE/ISO/DNV compliance

## Related Skills

- [structural-analysis](../structural-analysis/SKILL.md) - Structural integrity
- [mooring-design](../mooring-design/SKILL.md) - Mooring system protection
- [fatigue-analysis](../fatigue-analysis/SKILL.md) - Corrosion-fatigue interaction

## Package Structure

The CP package lives at `digitalmodel/src/digitalmodel/cathodic_protection/`:

| Module | Purpose |
|--------|---------|
| `__init__.py` | Unified exports from all sub-modules |
| `api_rp_1632.py` | API RP 16Q32 calculations |
| `iso_15589_2.py` | ISO 15589-2 pipeline CP |
| `dnv_rp_b401.py` | DNV-RP-B401 offshore structures |
| `marine_cp.py` | Multi-zone marine CP — temp/depth current density, calcareous deposits |
| `marine_structure_cp.py` | Zone-based CP — ClimateRegion enum, anode distribution, retrofit (**overlaps marine_cp.py, consolidation tracked in #1702**) |
| `pipeline_cp.py` | Pipeline-specific CP design |
| `iccp_design.py` | Impressed current CP design |
| `fuel_system_cp.py` | Fuel system ICCP (FuelPipeSegment, RectifierOutput) |
| `anode_sizing.py` | Anode mass/geometry calculations |
| `anode_depletion.py` | Anode consumption tracking |
| `coating.py` | Coating breakdown factors |
| `corrosion_rate.py` | Corrosion rate models |
| `cp_monitoring.py` | CP monitoring systems |
| `cp_reporting.py` | Report generation |
| `cp_survey.py` | Survey data processing |
| `stray_current.py` | AC/DC stray current analysis |

Legacy router: `digitalmodel/src/digitalmodel/infrastructure/common/cathodic_protection.py`
Tests: `digitalmodel/tests/specialized/cathodic_protection/`

## References

- NACE International Standards
- ISO 15589-2: Cathodic Protection of Offshore Pipelines
- DNV-RP-F103 (2003, 2010): Cathodic Protection of Submarine Pipelines
- DNV-RP-B401 (2005, 2011, 2021): Cathodic Protection Design
- ABS GN Ships 2017 (289): Cathodic Protection of Ships
- ABS GN Offshore Structures 2018 (306): Cathodic Protection of Offshore Structures
- SNAME T&R R-21: Cathodic Protection of Marine Service

---

## Version History

- **1.2.0** (2026-02-20): Added DNV_RP_B401_offshore route; B401-2021 coating categories I–III; zonal current demand; Dwight anode resistance
- **1.1.0** (2026-02-20): Fixed examples to use real CathodicProtection().router(cfg) API; added DNV-RP-F103 to standards table
- **1.0.0** (2025-01-02): Initial release from agents/cathodic-protection-engineer.md

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.2.0] - 2026-02-20 (+2)](120-2026-02-20/SKILL.md)
- [Cathodic Protection Systems (+2)](cathodic-protection-systems/SKILL.md)
- [Example: Ship Hull (ABS GN Ships 2018) (+3)](example-ship-hull-abs-gn-ships-2018/SKILL.md)
- [CP System Design Process](cp-system-design-process/SKILL.md)
