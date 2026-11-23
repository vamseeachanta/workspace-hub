---
title: "Free-Span VIV Fatigue Assessment"
description: "Pipeline free-span VIV fatigue methodology per DNV-RP-F105, implemented clean-room in digitalmodel  Extended with probability-weighted multi-current damage..."
keywords: "free-span, pipeline, viv, fatigue, dnv-rp-f105, weibull, miner"
author: "ACE Engineer"
url: "/knowledge/engineering/free-span-viv-fatigue"
canonical: "https://aceengineer.com/knowledge/engineering/free-span-viv-fatigue"
domain: "engineering"
---

# Free-Span VIV Fatigue Assessment

*By [ACE Engineer](https://aceengineer.com) -- Expert Offshore and Marine Engineering Consulting*

Pipeline free-span VIV fatigue methodology per DNV-RP-F105, implemented clean-room in digitalmodel  Extended with probability-weighted multi-current damage summation

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

- **Related concept**: VIV Riser Fatigue
- **Related concept**: S-N Curve Fatigue Definitions
- **Related concept**: Pipeline Integrity Assessment
- **Related standard**: DNV-RP-F105
- **Related standard**: DNV-RP-C203

---

## Work With Us

ACE Engineer provides expert engineering consulting across offshore, marine, and subsea disciplines. Our team combines deep domain expertise with modern computational tools to deliver reliable, auditable results.

[Contact us](https://aceengineer.com/contact) to discuss how we can support your project.

*Visit [aceengineer.com](https://aceengineer.com) for our full range of services.*

