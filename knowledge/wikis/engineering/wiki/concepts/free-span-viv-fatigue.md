---
title: "Free-Span VIV Fatigue Assessment"
tags: [free-span, pipeline, viv, fatigue, dnv-rp-f105, weibull, miner]
sources:
  - closed-issues
added: 2026-04-09
last_updated: 2026-04-09
---

# Free-Span VIV Fatigue Assessment

Pipeline free-span VIV fatigue methodology per DNV-RP-F105, implemented clean-room in digitalmodel (#1773, closed 2026-04-04). Extended with probability-weighted multi-current damage summation (#1791).

## Methodology

1. **Current profile fitting**: Weibull distribution fitted to measured current data (Sec 3.3)
2. **Wave-induced velocity**: JONSWAP spectrum integrated for near-seabed velocities (Sec 3.4)
3. **VIV screening**: Cross-flow and in-line onset checked against reduced velocity criteria (Sec 4.3)
4. **Modal analysis**: Natural frequencies and mode shapes for the free span (Sec 6)
5. **Fatigue damage**: Miner's rule with bilinear S-N curves for each current bin (Sec 4.4)
6. **Probability weighting**: `D_total = sum(D_i * prob_i)` across current speed bins

## Probability-Weighted Summation

Real pipeline assessments use multiple current speed bins with occurrence probabilities:

```
Speed [m/s]   Probability
0.04          0.80
0.20          0.10
0.40          0.05
0.60          0.04
1.00          0.01
```

The `assess_multi_current(current_bins)` method sweeps all bins and accumulates weighted damage, matching the methodology from operational practice.

## Clean-Room Implementation

The Python implementation was built entirely from DNV-RP-F105 standard text due to copyright constraints on legacy MATLAB scripts (copyrighted by original engineering firm, c.2005-2014). Independent variable names, function structure, algorithms, and test vectors were used. Deny-list patterns in `.legal-deny-list.yaml` block any reference to original tool/firm/author names.

## Cross-References

- **Related concept**: [VIV Riser Fatigue](../concepts/viv-riser-fatigue.md)
- **Related concept**: [S-N Curve Fatigue Definitions](../concepts/sn-curve-fatigue-definitions.md)
- **Related concept**: [Pipeline Integrity Assessment](../concepts/pipeline-integrity-assessment.md)
- **Related standard**: [DNV-RP-F105](../standards/dnv-rp-f105.md)
- **Related standard**: [DNV-RP-C203](../standards/dnv-rp-c203.md)
