---
title: "Energy Field Development Economics"
tags: [economics, npv, field-development, arps, monte-carlo, fiscal-regime]
sources:
  - career-learnings-seed
added: 2026-04-08
last_updated: 2026-04-08
---

# Energy Field Development Economics

The economics of oil and gas field development — from discovery to abandonment. The core question: is this field commercially viable, and what is the optimal development plan? Every engineering decision (number of wells, platform type, pipeline route, subsea vs. dry tree) ultimately feeds into the economic model.

## Net Present Value (NPV)

The fundamental metric for field development decisions:

```
NPV = sum( cashflow_t / (1 + r)^t )  for t = 0 to T
```

Where:
- **cashflow_t** = revenue - opex - capex - taxes - royalties in year t
- **r** = discount rate (typically 10% for oil and gas — hence "NPV10")
- **T** = field life (typically 15-30 years)

**NPV10** (NPV at 10% discount rate) is the industry standard comparison metric. A positive NPV10 means the project returns more than 10% on invested capital.

### Other Economic Indicators

| Metric | Definition | Decision Use |
|--------|-----------|--------------|
| **IRR** (Internal Rate of Return) | Discount rate at which NPV = 0 | Must exceed hurdle rate (typically 12-15%) |
| **Payback period** | Time to recover initial investment | Shorter is better; typically < 5 years for sanction |
| **PI** (Profitability Index) | NPV / capex | Used to rank competing projects with different scales |
| **Breakeven price** | Oil price at which NPV = 0 | Key sensitivity — must be below forward curve |

## Key Sensitivities

Field development economics are most sensitive to (in approximate order):

1. **Oil/gas price** — dominates all other uncertainties
2. **Production profile** — peak rate, plateau duration, decline rate
3. **Capex** — drilling costs typically 40-60% of total capex
4. **Opex** — operating costs per barrel (lifting cost)
5. **Abandonment cost** — decommissioning is a late but significant cash outflow
6. **Fiscal regime** — government take determines the operator's net cashflow

## Breakeven Calculation

```
Breakeven = (opex + capex_recovery) / (production x royalty_net)
```

Where:
- **opex** = annual operating expenditure
- **capex_recovery** = total capex amortised over field life
- **production** = annual production volume (barrels or BOE)
- **royalty_net** = (1 - royalty_rate) — the fraction of production the operator keeps

This gives the minimum oil price at which the project breaks even. A project with breakeven at $45/bbl is viable in most price scenarios; one at $75/bbl is marginal.

## Fiscal Regimes

The government take structure determines how much of the gross revenue reaches the operator:

| Regime Type | Mechanism | Typical Government Take |
|-------------|-----------|------------------------|
| **Royalty/Tax** (US, UK, Norway) | Royalty on gross production + corporate tax on profits | 40-78% (Norway highest) |
| **Production Sharing Contract (PSC)** (Indonesia, Angola, Nigeria) | Cost oil recovery + profit oil split | 55-85% |
| **Service Contract** (Iraq, Iran) | Fixed fee per barrel to contractor | 85-95% (operator has no price exposure) |
| **Concessionary** (Middle East legacy) | Royalty + tax, usually favorable terms | 30-60% |

PSCs are common in deepwater West Africa and Southeast Asia. Understanding the fiscal terms is essential before running economics — the same reservoir can be commercial under one regime and uncommercial under another.

## Production Decline — Arps Equations

After the plateau period, production declines. **Arps decline curve analysis** models this empirically:

### Hyperbolic Decline (General Form)

```
q(t) = qi / (1 + b * Di * t)^(1/b)
```

Where:
- **qi** = initial rate (at start of decline)
- **Di** = initial decline rate (fraction per year)
- **b** = Arps exponent (0 < b < 1 for conventional, b ~ 1 for tight oil/shale)
- **t** = time from start of decline

### Special Cases

| b Value | Decline Type | Typical Application |
|---------|-------------|---------------------|
| b = 0 | Exponential | Conventional reservoirs, mature fields |
| 0 < b < 1 | Hyperbolic | Most reservoirs during primary depletion |
| b = 1 | Harmonic | Tight oil, shale wells, heavy oil |

**b = 1 for tight oil** (shale wells): the Arps harmonic model fits the long, slow decline seen in unconventional wells. Using b = 0 (exponential) for shale underestimates EUR (Estimated Ultimate Recovery) significantly.

### Modified Hyperbolic

In practice, hyperbolic decline eventually transitions to exponential (the reservoir approaches boundary-dominated flow). Use a **modified hyperbolic**: hyperbolic until the decline rate reaches a terminal decline rate (typically 5-8% per year), then switch to exponential.

## Monte Carlo Simulation

Deterministic economics give a single NPV. **Monte Carlo simulation** captures the range of outcomes by sampling from probability distributions for uncertain parameters:

| Parameter | Distribution Type | Key Percentiles |
|-----------|------------------|-----------------|
| Oil price | Log-normal or triangular | Reflects forward curve uncertainty |
| Reserves (STOIIP) | Log-normal | P10 (optimistic), P50 (most likely), P90 (conservative) |
| Recovery factor | Triangular or uniform | Range from analogue fields |
| Capex | Triangular | -15% / base / +30% asymmetric |
| Opex | Triangular | -10% / base / +20% |

**Key percentile definitions** (SPE/PRMS convention):
- **P90** = conservative estimate (90% probability of exceeding this value)
- **P50** = median (best estimate)
- **P10** = optimistic estimate (only 10% probability of exceeding)

Note: P90 is the **low** case, not the high case. This is a common source of confusion — the "P" refers to the probability of exceeding, not the percentile of the distribution.

Run 10,000+ iterations to get stable P10/P50/P90 NPV estimates. Plot the cumulative distribution function (CDF) to show the full range of outcomes to decision-makers.

## Key Patterns

1. **NPV10 standard discount rate** — always report NPV at 10% for comparability
2. **P50 = median, P90 = conservative** — P90 is the low case (90% chance of exceeding)
3. **Arps hyperbolic: q = qi/(1+b*Di*t)^(1/b), b=1 for tight oil** — do not use exponential decline for shale wells
4. **Breakeven price is the single most important screening metric** — if breakeven exceeds the company's price assumption, the project does not proceed

## Practical Guidance

- **Tornado diagrams** show which parameter has the most impact on NPV. Almost always: oil price first, then production volume, then capex. If your tornado shows opex as the top driver, check the model.
- **Real options** thinking: a phased development (Phase 1: minimum facilities, Phase 2: expansion if prices hold) can be more valuable than a single large-capex development, because it preserves optionality.
- **Sunk cost trap**: exploration costs are sunk. The sanction decision should be based on forward-looking economics only. A field is not commercial just because you spent $200M finding it.
- **Abandonment timing**: fields often operate well past their economic optimum because the operator defers abandonment costs. Model this explicitly — late-life opex can exceed revenue.

## Cross-References

- **Related concept**: [[pipeline-integrity-assessment]] — integrity management costs are a significant opex line item
- **Related concept**: [[cathodic-protection-design]] — CP lifecycle cost feeds into opex modeling
- **Related concept**: [[ai-drill-well-on-paper]] — well planning optimization directly affects drilling capex
- **Cross-wiki (marine-engineering)**: [Process Safety](../../../marine-engineering/wiki/concepts/process-safety.md) — safety systems (SIS, relief, deluge) are significant capex and opex items in field development
- **Cross-wiki (maritime-law)**: [Environmental Liability](../../../maritime-law/wiki/concepts/environmental-liability.md) — environmental liability exposure (CLC, OPA 90) is a material risk in field development economics
- **Cross-wiki (maritime-law)**: [OPA 90](../../../maritime-law/wiki/concepts/opa-90.md) — unlimited gross-negligence liability impacts deepwater project risk assessment and insurance costs
- **Source**: [Career Learnings Seed](../sources/career-learnings-seed.md)
