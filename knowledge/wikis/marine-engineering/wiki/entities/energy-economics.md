---
title: "Energy Economics"
tags: [economics, npv, field-development, oil-gas, production-decline, monte-carlo]
sources:
  - career-learnings
added: 2026-04-09
last_updated: 2026-04-09
---

# Energy Economics

Oil and gas field development economics covering net present value (NPV) analysis, production
decline modelling, fiscal regime assessment, and uncertainty quantification.

## NPV Analysis

NPV = sum(cashflow_t / (1+r)^t) where:

- **NPV10** is the industry standard discount rate (10%) for oil field economics
- Key sensitivities: oil price, production profile, capex, opex, abandonment cost
- Breakeven price = opex + capex_recovery / (production x royalty_net)

## Reserve Estimates

| Percentile | Meaning | Usage |
|------------|---------|-------|
| P10 | 10th percentile (optimistic) | Upside scenario |
| P50 | Median estimate | Base case |
| P90 | 90th percentile (conservative) | Lender/sanction case |

## Production Decline (Arps Equations)

- **Exponential**: q = qi * exp(-Di*t) — constant decline rate
- **Hyperbolic**: q = qi / (1 + b*Di*t)^(1/b) — b=1 typical for tight oil
- **Harmonic**: Special case of hyperbolic with b=1

## Fiscal Regimes

- Government take varies by fiscal regime: Production Sharing Contract (PSC) vs royalty/tax
- Monte Carlo simulation for uncertainty quantification across P10/P50/P90 reserve estimates

## Design Patterns

- NPV10 is industry standard discount rate for oil field economics
- P50 = median estimate; P90 = 90th percentile (conservative)
- Arps hyperbolic: q = qi / (1 + b*Di*t)^(1/b); b=1 for tight oil

## Cross-References

- **Related entity**: [[pipeline-integrity]] (field life extension decisions)
- **Related entity**: [[cfd-offshore]] (development concept selection)
- **Cross-wiki (engineering)**: [Energy Field Economics](../../../engineering/wiki/concepts/energy-field-economics.md) — comprehensive NPV analysis, Arps decline curves, Monte Carlo simulation, and fiscal regime assessment
- **Cross-wiki (engineering)**: [Field Development Economics](../../../engineering/wiki/concepts/field-development-economics.md) -- similar slugs (56%); similar titles (56%); shared tags: economics, field-development, npv; shared keywords: cross-references, economics, entity, fiscal, regimes
