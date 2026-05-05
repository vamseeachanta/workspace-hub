---
title: "DNV-RP-F105 — Free Spanning Pipelines"
tags: [standard, dnv, pipeline, free-span, viv, fatigue, screening]
sources:
  - closed-issues
added: 2026-04-09
last_updated: 2026-04-09
---

# DNV-RP-F105 — Free Spanning Pipelines

DNV Recommended Practice for free spanning pipeline assessment, covering VIV screening, fatigue damage, and structural response. Implemented as a clean-room Python module in digitalmodel (#1773).

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

The digitalmodel implementation (#1773, closed 2026-04-04) was built entirely from the DNV-RP-F105 standard text due to copyright constraints on legacy MATLAB scripts. Independent variable names, function structure, and test vectors were used.

### Module Structure

| Module | DNV-RP-F105 Section |
|--------|-------------------|
| `viv_screening` | Sec 4.3 |
| `viv_fatigue` | Sec 4.4 |
| `weibull_current` | Sec 3.3 |
| `wave_velocity` | Sec 3.4 |
| `safety_factors` | Table 4-1 |
| `mode_shapes` | Sec 6 |

### Probability-Weighted Damage (#1791)

Extended with multi-current bin damage summation: `D_total = sum(D_i * prob_i)` for current speed bins with occurrence probabilities. This matches the methodology from real pipeline assessment practice.

## Cross-References

- **Related concept**: [VIV Riser Fatigue](../concepts/viv-riser-fatigue.md)
- **Related concept**: [S-N Curve Fatigue Definitions](../concepts/sn-curve-fatigue-definitions.md)
- **Related concept**: [Pipeline Integrity Assessment](../concepts/pipeline-integrity-assessment.md)
- **Related standard**: [DNV-RP-C203](../standards/dnv-rp-c203.md)
- **Cross-wiki (engineering-standards)**: [DNV-RP-F105 Free Spanning Pipelines — bounded summary](../../../engineering-standards/wiki/standards/dnv-rp-f105.md) -- similar slugs (100%); similar titles (78%); shared tags: dnv, viv; shared keywords: cross-references, dnv-rp-f105, free, pipelines, scope; shared entities: DNV, DNV-RP-F105, VIV
- **Cross-wiki (engineering-standards)**: [DNV-RP-F101 Corroded Pipelines — bounded summary](../../../engineering-standards/wiki/standards/dnv-rp-f101.md) -- similar slugs (91%); similar titles (54%); shared tags: dnv; shared keywords: cross-references, pipelines, scope; shared entities: DNV
- **Cross-wiki (engineering-standards)**: [DNV-RP-F109 On-bottom Stability of Pipelines — bounded summary](../../../engineering-standards/wiki/standards/dnv-rp-f109.md) -- similar slugs (91%); similar titles (51%); shared tags: dnv; shared keywords: cross-references, pipelines, scope; shared entities: DNV
- **Cross-wiki (asset-management)**: [DNV-RP-G101 — Risk-Based Inspection of Offshore Topsides Static Mechanical Equipment](../../../asset-management/wiki/standards/dnv-rp-g101.md) -- similar slugs (82%); shared tags: dnv, standard; shared entities: DNV
- **Cross-wiki (engineering-standards)**: [DNV-RP-C203 Fatigue Design of Offshore Steel Structures — bounded summary](../../../engineering-standards/wiki/standards/dnv-rp-c203.md) -- similar slugs (73%); shared tags: dnv, fatigue; shared entities: DNV, DNV-RP-C203
- **Cross-wiki (engineering-standards)**: [DNV-ST-F101 Submarine Pipeline Systems — bounded summary](../../../engineering-standards/wiki/standards/dnv-st-f101.md) -- similar slugs (73%); shared tags: dnv; shared entities: DNV
- **Cross-wiki (engineering-standards)**: [DNV-RP-H103 Modelling and Analysis of Marine Operations — bounded summary](../../../engineering-standards/wiki/standards/dnv-rp-h103.md) -- similar slugs (82%); shared tags: dnv; shared entities: DNV
- **Cross-wiki (engineering-standards)**: [DNV-RP-F103 Cathodic Protection of Submarine Pipelines by Galvanic Anodes — bounded summary](../../../engineering-standards/wiki/standards/dnv-rp-f103.md) -- similar slugs (91%); shared tags: dnv; shared entities: DNV, DNV-RP-F101, DNV-ST-F101
