---
title: "Field Development Economics"
description: "Integrated field development economics framework, wiring worldenergydata's extensive FDAS and economics modules into the digitalmodel field_development package"
keywords: "field-development, economics, npv, irr, capex, opex, fiscal-regime, dcf"
author: "ACE Engineer"
url: "/knowledge/engineering/field-development-economics"
canonical: "https://aceengineer.com/knowledge/engineering/field-development-economics"
domain: "engineering"
---

# Field Development Economics

*By [ACE Engineer](https://aceengineer.com) -- Expert Offshore and Marine Engineering Consulting*

Integrated field development economics framework, wiring worldenergydata's extensive FDAS and economics modules into the digitalmodel field_development package

## Capabilities

| Module | Source | Coverage |
|--------|--------|----------|
| FDAS (13 files) | worldenergydata | NPV, MIRR, IRR, payback, cashflow engine, price deck manager |
| Economics (3 files) | worldenergydata | CashFlowSchedule, carbon NPV, breakeven, tornado charts |
| Cost module (6 files) | worldenergydata | ML-based cost predictor + 71 real sanctioned project benchmarks |
| BSEE cost analysis (10 files) | worldenergydata | Cost engine, calibration, 120+ synthetic records |
| BSEE financial (10 files) | worldenergydata | Full field NPV/MIRR + drilling cost allocation |
| Decommissioning (8 files) | worldenergydata | ABEX estimation, late-life identification |
| Drilling economics (5 files) | worldenergydata | Batch drilling, Wright learning curve |
| Reservoir (2 files) | worldenergydata | OOIP, EUR, Monte Carlo |
| Lower Tertiary (7 files) | worldenergydata | 8 ultra-deepwater GoM fields with full financials |

## Fiscal Regimes

Five country-specific fiscal regime models:

| Country | Key Features |
|---------|-------------|
| Norway | 78% marginal tax (22% + 56% special petroleum tax) |
| UK | RFCT + Supplementary Charge + EPL |
| Brazil | Concession + Production Sharing Agreement |
| Nigeria | Deepwater PSC |
| US | Federal + state-level royalties |

## Architecture

`digitalmodel/field_development/economics.py` serves as a facade importing from worldenergydata modules, with a unified input schema matching FDAS + cost predictor needs.

## Cross-References

- **Related concept**: Energy Field Economics
- **Related entity**: digitalmodel

---

## Work With Us

ACE Engineer provides expert engineering consulting across offshore, marine, and subsea disciplines. Our team combines deep domain expertise with modern computational tools to deliver reliable, auditable results.

[Contact us](https://aceengineer.com/contact) to discuss how we can support your project.

*Visit [aceengineer.com](https://aceengineer.com) for our full range of services.*

