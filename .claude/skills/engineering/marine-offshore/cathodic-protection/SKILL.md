---
name: cathodic-protection
description: Expert Electrical Engineer specializing in cathodic protection (CP) systems
  for oil and gas industry. Use for CP system design, corrosion prevention, sacrificial
  anode calculations, impressed current systems, pipeline integrity, coating defects,
  and NACE/ISO standards compliance.
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
see_also:
- cathodic-protection-version-metadata
- cathodic-protection-120-2026-02-20
- cathodic-protection-cathodic-protection-systems
- cathodic-protection-example-ship-hull-abs-gn-ships-2018
- cathodic-protection-cp-system-design-process
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

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.2.0] - 2026-02-20 (+2)](120-2026-02-20/SKILL.md)
- [Cathodic Protection Systems (+2)](cathodic-protection-systems/SKILL.md)
- [Example: Ship Hull (ABS GN Ships 2018) (+3)](example-ship-hull-abs-gn-ships-2018/SKILL.md)
- [CP System Design Process](cp-system-design-process/SKILL.md)
