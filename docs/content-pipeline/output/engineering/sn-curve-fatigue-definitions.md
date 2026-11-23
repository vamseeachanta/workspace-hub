---
title: "S-N Curve Fatigue Definitions"
description: "S-N curves (Stress-Number curves, also called Woehler curves) define the relationship between cyclic stress range and the number of cycles to failure for a..."
keywords: "fatigue, sn-curve, riser, dnv-rp-c203, stress-range, miner"
author: "ACE Engineer"
url: "/knowledge/engineering/sn-curve-fatigue-definitions"
canonical: "https://aceengineer.com/knowledge/engineering/sn-curve-fatigue-definitions"
domain: "engineering"
---

# S-N Curve Fatigue Definitions

*By [ACE Engineer](https://aceengineer.com) -- Expert Offshore and Marine Engineering Consulting*

S-N curves (Stress-Number curves, also called Woehler curves) define the relationship between cyclic stress range and the number of cycles to failure for a given material and weld detail. They are foundational to fatigue design of risers, pipelines, and marine structures.

## Fundamental Relationship

The S-N curve is expressed as:

```
N = a / (S^m)
```

Or equivalently in log-log space:

```
log(N) = log(a) - m * log(S)
```

Where:

| Parameter | Description | Units |
|-----------|-------------|-------|
| N | Cycles to failure | - |
| S | Stress range (peak-to-peak) | N/m^2 (or MPa) |
| m | Negative inverse slope of S-N curve | - |
| log(a) | Intercept of log(N) axis | - |

## DNV-RP-C203 Standard Curves

DNV-RP-C203 defines S-N curves for different weld categories in seawater and in-air environments:

| Curve | m (N < 10^7) | log(a) (N < 10^7) | m (N > 10^7) | Typical Application |
|-------|--------------|-------------------|--------------|---------------------|
| B1 | 4.0 | 15.117 | 5.0 | Rolled sections, base metal |
| D | 3.0 | 12.164 | 5.0 | Butt welds, flush ground |
| E | 3.0 | 12.010 | 5.0 | Butt welds, as-welded |
| F | 3.0 | 11.855 | 5.0 | Cruciform joints |
| F1 | 3.0 | 11.699 | 5.0 | Fillet welds |
| W3 | 3.0 | 10.970 | 5.0 | Worst-case welds |

Note: Curves have a slope change at 10^7 cycles. The shallower slope beyond this transition reflects the endurance limit behavior.

## Cut-Off Stress Range

Below the cut-off stress range, fatigue damage is considered negligible:

- Stress ranges below the constant-amplitude fatigue limit (CAFL) at ~10^7 cycles contribute no damage under constant amplitude loading
- Under variable amplitude loading (realistic sea states), stress ranges below the cut-off at ~10^9 cycles are excluded
- This prevents accumulation of negligible damage from very small stress cycles

## Miner's Rule — Cumulative Damage

Palmgren-Miner's linear damage accumulation rule:

```
D = sum(ni / Ni) < 1 / DFF
```

Where:

| Symbol | Description | Typical Value |
|--------|-------------|---------------|
| D | Cumulative fatigue damage ratio | Must be < 1/DFF |
| ni | Number of cycles at stress range Si | From rainflow counting |
| Ni | Cycles to failure at stress range Si | From S-N curve |
| DFF | Design Fatigue Factor | 3.0 - 10.0 depending on criticality |

### DFF Guidelines (DNV)

| Consequence of Failure | Access for Inspection | DFF |
|------------------------|----------------------|-----|
| Low | Yes | 3.0 |
| Low | No | 6.0 |
| High | Yes | 6.0 |
| High | No | 10.0 |

## Application to Riser Fatigue

For riser fatigue analysis:

1. **Wave fatigue**: Compute stress ranges from vessel motions and wave loading across all sea states
2. **VIV fatigue**: Compute stress ranges from vortex-induced vibration response
3. **Combined fatigue**: Sum wave and VIV damage contributions using Miner's rule
4. **Fatigue life**: Life = 1 / (D_total * DFF), expressed in years

## Cross-References

- **Related concept**: VIV Riser Fatigue
- **Related entity**: OrcaFlex Solver
- **Cross-wiki (marine-engineering)**: Mooring Line Failure — wire rope mooring fatigue assessed using S-N curve methodology
- **Cross-wiki (naval-architecture)**: Ship Structural Design — ship hull fatigue under cyclic wave loading uses S-N curves per classification rules
- **Source**: Dark Intelligence Extractions
- **Source**: Career Learnings Seed

---

## Work With Us

ACE Engineer provides expert engineering consulting across offshore, marine, and subsea disciplines. Our team combines deep domain expertise with modern computational tools to deliver reliable, auditable results.

[Contact us](https://aceengineer.com/contact) to discuss how we can support your project.

*Visit [aceengineer.com](https://aceengineer.com) for our full range of services.*

