---
title: "LNG Carrier Mooring System"
tags: [lng, mooring, jetty, terminal, operations]
sources:
  - mooring-failures-lng-terminals
  - dnvgl-os-e201
added: 2026-04-07
last_updated: 2026-04-07
---

# LNG Carrier Mooring System

Mooring arrangements for LNG carriers at offshore jetties and onshore terminals. LNG carriers are among the most critical vessels to moor due to the hazardous cargo and the need for extended loading operations.

## Terminal Examples

| Terminal | Location | Operator | Key Issue |
|----------|----------|----------|-----------|
| Karratha Gas Plant (KGP) | Withnell Bay, Australia | Woodside | Long-period swell resonance |
| South Hook LNG | Milford Haven, UK | South Hook LNG Co. | HMPE line failure (2015) |
| Prelude FLNG | Browse Basin, Australia | Shell | Nylon line failure (2018) |
| Ras Laffan | Qatar | QatarEnergy | HMPE failures |
| Gorgon/Wheatstone/NWS | North West Shelf, Australia | Chevron/Woodside | Production interrupted by Cyclone Narelle (2026) |

## Key Design Considerations

- **Wave environment**: Long-period swells, harbour seiching, ship-generated waves
- **Mooring pattern**: Typically 8-12 breast lines, 4-6 spring lines for LNG carriers
- **Line material evolution**: Traditional wire rope → HMPE (Dyneema) → back to non-jacketed SK78 due to jacketed HMPE failures
- **Berth design**: Jetty configuration affects wave exposure and diffraction patterns
- **Operational limits**: Weather downtime, swell forecasts, production ramp-back procedures

## Cross-References

- **Related concept**: [[long-period-swell-resonance]]
- **Related concept**: [[mooring-line-failure]]
- **Related entity**: [[separator]] (LNG terminals include processing)
- **Cross-wiki (engineering)**: [OrcaFlex Solver](../../../engineering/wiki/entities/orcaflex-solver.md) — OrcaFlex used for dynamic mooring analysis of LNG carriers at terminals
- **Cross-wiki (engineering)**: [Wave Theory for Offshore Engineering](../../../engineering/wiki/concepts/wave-theory-offshore.md) — wave spectra and swell environment as primary design driver for LNG terminal moorings
