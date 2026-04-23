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

## Marine Terminal Engineering Interface

LNG carrier mooring should be treated as part of the broader marine terminal engineering problem, not as an isolated rope-and-hook system. Alongside line layout and berth hardware, terminal engineering must account for:
- berth orientation and dolphin arrangement
- fender reaction and vessel offset limits
- loading-arm or hose motion envelope constraints
- harbour agitation and long-period response
- pilotage, tug, and approach/departure limitations
- emergency release and shutdown logic during cargo transfer

This wider system framing is reinforced by the LNG2026 technical programme, which explicitly groups shipping, marine, port operations, bunkering, ship-to-ship transfer, and LNG terminal infrastructure as linked technical topics rather than separate silos.

## Cross-References

- **Related concept**: [[long-period-swell-resonance]]
- **Related concept**: [[mooring-line-failure]]
- **Related concept**: [[lng-marine-terminal-engineering]]
- **Related entity**: [[separator]] (LNG terminals include processing)
- **Related source**: [LNG2026 TP04: Shipping, Marine and Port Operations](../sources/lng2026-tp04-shipping-marine-port-operations.md)
- **Cross-wiki (engineering)**: [OrcaFlex Solver](../../../engineering/wiki/entities/orcaflex-solver.md) — OrcaFlex used for dynamic mooring analysis of LNG carriers at terminals
- **Cross-wiki (engineering)**: [Wave Theory for Offshore Engineering](../../../engineering/wiki/concepts/wave-theory-offshore.md) — wave spectra and swell environment as primary design driver for LNG terminal moorings
