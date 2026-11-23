---
title: "DNV-RP-F105 — Free Spanning Pipelines"
description: "DNV Recommended Practice for free spanning pipeline assessment, covering VIV screening, fatigue damage, and structural response. Implemented as a clean-room..."
keywords: "standard, dnv, pipeline, free-span, viv, fatigue, screening"
author: "ACE Engineer"
url: "/knowledge/standards/dnv-rp-f105"
canonical: "https://aceengineer.com/knowledge/standards/dnv-rp-f105"
domain: "engineering"
---

# DNV-RP-F105 — Free Spanning Pipelines

*By [ACE Engineer](https://aceengineer.com) -- Expert Offshore and Marine Engineering Consulting*

DNV Recommended Practice for free spanning pipeline assessment, covering VIV screening, fatigue damage, and structural response. Implemented as a clean-room Python module in digitalmodel

## Scope

| Section | Topic |
|---------|-------|
| Sec 3.3 | Current profile Weibull fitting |
| Sec 3.4 | Wave-induced velocity from JONSWAP spectrum |
| Sec 4.3 | Cross-flow and in-line VIV onset screening criteria |
| Sec 4.4 | Fatigue damage calculation (Miner's rule) |
| Sec 6 | Mode shape and effective mass computation |
| Table 4-1 | Safety class factors (Low/Normal/High) |

## Clean-Room Implementation

The digitalmodel implementation  was built entirely from the DNV-RP-F105 standard text due to copyright constraints on legacy MATLAB scripts. Independent variable names, function structure, and test vectors were used.

### Module Structure

| Module | DNV-RP-F105 Section |
|--------|-------------------|
| `viv_screening` | Sec 4.3 |
| `viv_fatigue` | Sec 4.4 |
| `weibull_current` | Sec 3.3 |
| `wave_velocity` | Sec 3.4 |
| `safety_factors` | Table 4-1 |
| `mode_shapes` | Sec 6 |

### Probability-Weighted Damage

Extended with multi-current bin damage summation: `D_total = sum(D_i * prob_i)` for current speed bins with occurrence probabilities. This matches the methodology from real pipeline assessment practice.

## Cross-References

- **Related concept**: VIV Riser Fatigue
- **Related concept**: S-N Curve Fatigue Definitions
- **Related concept**: Pipeline Integrity Assessment
- **Related standard**: DNV-RP-C203

---

## Work With Us

ACE Engineer provides expert engineering consulting across offshore, marine, and subsea disciplines. Our team combines deep domain expertise with modern computational tools to deliver reliable, auditable results.

[Contact us](https://aceengineer.com/contact) to discuss how we can support your project.

*Visit [aceengineer.com](https://aceengineer.com) for our full range of services.*

