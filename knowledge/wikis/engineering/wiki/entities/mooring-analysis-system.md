---
title: "Mooring Analysis System"
tags: [mooring, catenary, taut-mooring, fpso, station-keeping, api-rp-2sk, dnv]
sources:
  - skills-metadata
  - mooring-failures-seed
added: 2026-04-09
last_updated: 2026-04-09
---

# Mooring Analysis System

The mooring analysis system in digitalmodel covers station-keeping design for floating platforms (FPSOs, semi-subs, SPARs), catenary and taut-leg mooring configurations, tension calculations, fatigue assessment, and anchor design. Two complementary skills exist: `mooring-analysis` (analysis workflows) and `mooring-design` (system design including CALM/SALM buoys).

## Capabilities

- **Station-keeping design**: FPSO, semi-sub, SPAR mooring configurations
- **Catenary analysis**: Static and dynamic catenary behavior
- **CALM/SALM buoys**: Catenary Anchor Leg Mooring and Single Anchor Leg Mooring design
- **Spread mooring**: Multi-line spread mooring configuration optimization
- **Tension calculations**: Pretension, extreme loads, dynamic amplification
- **Fatigue assessment**: Mooring line fatigue life using T-N curves
- **Anchor design**: Holding capacity verification for drag, suction, and pile anchors

## Applicable Standards

| Standard | Scope |
|----------|-------|
| API RP 2SK (4th Ed, 2024) | Stationkeeping systems for floating structures |
| DNV-OS-E301 (2021) | Position mooring — dynamic amplification, nearshore gap |
| ISO 19901-7 | Stationkeeping systems |
| OCIMF MEG4 (2018) | Mooring equipment guidelines |

## Key Design Insight

API RP 2SK 4th Edition highlights that the N-year return period wave condition may **not** yield the most onerous mooring response — shorter-period waves can generate larger drift forces. Mooring line damping from drag can dominate total system damping for catenary systems, making realistic low-frequency damping estimates crucial.

## OrcaFlex Integration

Mooring analysis setup in OrcaFlex is a primary workflow. The `mooring-iteration` sub-skill provides design iteration workflows, while `mooring-design` covers YAML configuration patterns for OrcaFlex mooring models.

## Cross-References

- **Related entity**: [OrcaFlex Solver](../entities/orcaflex-solver.md)
- **Related entity**: [Solver Queue](../entities/solver-queue.md)
- **Related concept**: [VIV Riser Fatigue](../concepts/viv-riser-fatigue.md)
- **Related concept**: [S-N Curve Fatigue Definitions](../concepts/sn-curve-fatigue-definitions.md)
- **Related standard**: [DNV-RP-C205](../standards/dnv-rp-c205.md)
- **Cross-wiki (marine-engineering)**: [Mooring Line Failure](../../../marine-engineering/wiki/concepts/mooring-line-failure.md)
