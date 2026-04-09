---
title: "DNV-RP-C203: Fatigue Design"
tags: [standard, dnv, fatigue, sn-curve, welded-joints, offshore]
sources: [dnv-rp-c203]
added: 2026-04-08
last_updated: 2026-04-08
---

# DNV-RP-C203: Fatigue Design of Offshore Steel Structures

**Full title:** DNV-RP-C203 "Fatigue Design of Offshore Steel Structures"

## Scope

Provides S-N curves and fatigue design methodology for welded steel connections in offshore structures. Covers tubular joints, plated connections, and other structural details subjected to cyclic loading from waves, wind, and operational forces.

## S-N Curve Approach

Fatigue life is determined from S-N curves that relate the applied stress range (S) to the number of cycles to failure (N):

```
log N = log a - m * log S
```

where:
- **N** = number of cycles to failure
- **S** = stress range
- **a** = intercept (depends on detail category)
- **m** = negative inverse slope (typically 3 for N < 10^7, 5 for N > 10^7)

## S-N Curve Categories

Curves are classified by weld type, geometry, and quality:

| Category | Typical Application |
|----------|-------------------|
| **B1** | Base material, machined surfaces |
| **B2** | Butt welds ground flush, full penetration |
| **C** | Butt welds with cap intact |
| **C1** | Butt welds in tubulars |
| **C2** | Partial penetration butt welds |
| **D** | Fillet welds, cruciform joints |
| **E** | Weld toe at plate edge |
| **F** | Weld toe at plate surface |
| **F1** | Fillet welds on plate edge |
| **F3** | Non-load-carrying fillet welds |
| **G** | Gusset welds, complex details |
| **W1/W2/W3** | Weld root failures |
| **T** | Tubular joints (specific T-curve) |

Higher categories (B1, B2) have better fatigue performance; lower categories (G, W) have the worst.

## Hot-Spot Stress Method

For complex geometries where nominal stress classification is ambiguous, the hot-spot stress approach is used:

1. **Build FE model** with sufficiently fine mesh at the weld toe
2. **Extract stresses** at prescribed distances from the weld toe (surface stress extrapolation)
3. **Apply to the D-curve** (or appropriate hot-spot S-N curve)

Two extrapolation methods:
- **Type a:** stress perpendicular to weld toe on plate surface (read at 0.5t and 1.5t)
- **Type b:** stress perpendicular to weld toe along plate edge (read at 5mm and 15mm from weld toe, or proportional to plate thickness)

## Design Fatigue Factor (DFF)

The DFF accounts for consequence of failure and inspection access:

| Condition | DFF |
|-----------|-----|
| Inspectable, above splash zone | 1 |
| Inspectable, below water | 2 |
| Not inspectable, accessible for repair | 3 |
| Inaccessible, no inspection possible | 10 |

The calculated fatigue life must exceed the design life multiplied by the DFF:

```
N_calculated >= DFF x Design Life (in cycles)
```

## Miner's Rule for Cumulative Damage

When the structure sees variable-amplitude loading (as is typical in offshore), Miner's cumulative damage rule applies:

```
D = sum(n_i / N_i) <= 1.0 / DFF
```

where:
- **n_i** = number of cycles at stress range S_i (from rainflow counting or spectral analysis)
- **N_i** = number of cycles to failure at S_i (from S-N curve)
- **D** = cumulative fatigue damage ratio

## Fatigue Analysis Methods

| Method | Input | Best For |
|--------|-------|----------|
| **Deterministic** | Regular wave stepping | Screening, simple structures |
| **Spectral** | Wave scatter diagram + transfer functions | Production platforms, detailed design |
| **Time-domain** | Irregular wave time series | Nonlinear systems, transient events |

## Key Considerations

- **Thickness correction:** fatigue strength decreases with plate thickness above 25mm; apply thickness correction factor
- **Corrosion allowance:** S-N curves in seawater (with or without cathodic protection) are lower than in-air curves
- **Post-weld treatment:** grinding, TIG dressing, or hammer peening can improve fatigue category by 1-2 classes
- **Fabrication quality:** inspection and repair requirements are tied to the assumed S-N category

## Related Pages

- [S-N Curve and Fatigue Definitions](../concepts/sn-curve-fatigue-definitions.md) -- foundational fatigue terminology
- [FEA Structural Analysis](../concepts/fea-structural-analysis.md) -- finite element methods for hot-spot stress extraction
- [VIV Riser Fatigue](../concepts/viv-riser-fatigue.md) -- fatigue from vortex-induced vibrations in risers
- [DNV-RP-C205: Environmental Conditions and Loads](dnv-rp-c205.md) -- wave and current loading that drives fatigue
- **Cross-wiki (naval-architecture)**: [Ship Structural Design](../../../naval-architecture/wiki/concepts/ship-structures.md) — S-N curve fatigue methodology applies to ship hull structural details under classification rules
