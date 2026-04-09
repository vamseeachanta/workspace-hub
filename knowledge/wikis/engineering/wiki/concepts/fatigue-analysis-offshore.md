---
title: "Fatigue Analysis for Offshore Structures"
tags: [fatigue, s-n-curve, rainflow-counting, miners-rule, mooring-fatigue, structural-fatigue, spectral-fatigue]
sources:
  - skills-metadata
added: 2026-04-09
last_updated: 2026-04-09
---

# Fatigue Analysis for Offshore Structures

Comprehensive fatigue analysis methodology for mooring lines, risers, hull structures, joints, and connections. Covers S-N curve application, rainflow counting, Miner's cumulative damage rule, and spectral fatigue methods.

## Analysis Methods

1. **Deterministic (time-domain)**: Extract stress time series, apply rainflow counting, accumulate damage via Miner's rule
2. **Spectral (frequency-domain)**: Compute stress response spectra from RAOs, derive damage analytically using Dirlik or narrow-band approximation
3. **Probability-weighted**: Sweep multiple sea states from scatter diagram, weight damage by occurrence probability

## Key Concepts

### S-N Curves
Relate stress range (S) to number of cycles to failure (N). Bilinear S-N curves (two slopes) are standard for DNV-RP-C203. Selection depends on weld category, environment (air vs seawater vs seawater+CP), and hot-spot stress method.

### Rainflow Counting
ASTM E1049 standard practice. Extracts closed hysteresis loops from irregular stress history. Each loop defined by stress range and mean stress.

### Miner's Rule
Cumulative damage: `D = sum(n_i / N_i)` where n_i = cycles at stress range S_i, N_i = cycles to failure at S_i from S-N curve. Failure at D >= 1.0. Design fatigue factor (DFF) applied: `D_allowable = 1/DFF`.

### Spectral Fatigue
For stationary Gaussian processes: damage rate from stress response spectrum without explicit time series. Faster than time-domain for long exposure periods.

## Applicable Standards

| Standard | Scope |
|----------|-------|
| DNV-RP-C203 (2024) | Fatigue design of offshore steel structures |
| DNV-OS-E301 | Position mooring fatigue (Section 7) |
| API RP 2SK | Stationkeeping fatigue |
| ASTM E1049 | Cycle counting practices |
| BS 7608 | Steel structure fatigue design |

## Cross-References

- **Related concept**: [S-N Curve Fatigue Definitions](../concepts/sn-curve-fatigue-definitions.md)
- **Related concept**: [VIV Riser Fatigue](../concepts/viv-riser-fatigue.md)
- **Related concept**: [Structural Analysis for Offshore Structures](../concepts/structural-analysis-offshore.md)
- **Related standard**: [DNV-RP-C203](../standards/dnv-rp-c203.md)
- **Related entity**: [OrcaFlex Solver](../entities/orcaflex-solver.md)
- **Cross-wiki (marine-engineering)**: [Mooring Line Failure](../../../marine-engineering/wiki/concepts/mooring-line-failure.md) — fatigue methods (rainflow counting, Miner's rule) directly applicable to wire rope and HMPE mooring line fatigue
- **Cross-wiki (naval-architecture)**: [Ship Structural Design](../../../naval-architecture/wiki/concepts/ship-structures.md) — spectral fatigue methodology for hull girder and structural details under cyclic wave loading
