---
title: "Deep extraction — Elements riser toolbox OrcaFlex statistics workbooks"
tags: [elements-ingest, riser, orcaflex, extreme-statistics, gumbel, weibull, deep-extraction]
sources:
  - /mnt/ace/digitalmodel/references/riser-toolbox/orcaflex tools/weibul statistics/Weibull Fitting-PR1-1in-1000yrWave-135deg-R3.xlsm
  - /mnt/ace/digitalmodel/references/riser-toolbox/orcaflex tools/gumbel statistics/_PR1-11in-EnvelopeExtraction.xlsm
  - workspace-hub#2536
added: 2026-04-28
last_updated: 2026-04-28
domain: marine-engineering
---

# Deep extraction — Elements riser toolbox OrcaFlex statistics workbooks

This page captures a bounded first-pass extraction from the Elements `Riser Toolbox` corpus. The first pass inspected the smallest high-signal workbooks instead of opening the 158 MB and 286 MB workbooks.

## Source files inspected

| File | Size | Purpose inferred from workbook labels/formulas |
|---|---:|---|
| `Weibull Fitting-PR1-1in-1000yrWave-135deg-R3.xlsm` | 2,316,102 bytes | Weibull fitting over OrcaFlex stress/tension peaks for 1000-year wave headings and seeds |
| `_PR1-11in-EnvelopeExtraction.xlsm` | 4,153,808 bytes | OrcaFlex simulation loading/post-processing and envelope extraction for stress/tension outputs |

## Workbook structure

| Workbook | Sheet | Rows | Columns | Non-empty cells | Formula cells |
|---|---:|---:|---:|---:|---:|
| `Weibull Fitting-PR1-1in-1000yrWave-135deg-R3.xlsm` | `Stress_Weibull_Using(X-T)` | 1026 | 161 | 1576 | 827 |
| `Weibull Fitting-PR1-1in-1000yrWave-135deg-R3.xlsm` | `Stress_SortedPeaks` | 1026 | 161 | 27640 | 66 |
| `Weibull Fitting-PR1-1in-1000yrWave-135deg-R3.xlsm` | `Tension_Weibull_Using(X-T)` | 1050 | 161 | 1421 | 742 |
| `Weibull Fitting-PR1-1in-1000yrWave-135deg-R3.xlsm` | `Tension_SortedPeaks` | 1050 | 161 | 24258 | 63 |
| `_PR1-11in-EnvelopeExtraction.xlsm` | `Post-Process` | 1788 | 21 | 2030 | 938 |
| `_PR1-11in-EnvelopeExtraction.xlsm` | `Stress` | 1805 | 81 | 146204 | 240 |
| `_PR1-11in-EnvelopeExtraction.xlsm` | `Tension` | 1805 | 81 | 146123 | 160 |
| `_PR1-11in-EnvelopeExtraction.xlsm` | `__$Orcina_Hidden_Sheet$__` | 53 | 9 | 128 | 0 |

## Method signals extracted

- Workbook labels show repeated OrcaFlex simulation cases such as `1000YRPWAVE_000deg_r1`, `1000YRPWAVE_045deg_r1`, `1000YRPWAVE_135deg_r1`, through multiple headings and random seeds.
- Weibull workbooks separate stress and tension workflows into `*_Weibull_Using(X-T)` sheets and `*_SortedPeaks` sheets.
- Formula samples include `AVERAGE(...)` over peak ranges and log transformations such as `LN(value^2 + value^2) - 2*LN(value)`, consistent with fitting distribution parameters from sorted peaks.
- Gumbel/envelope workbook sheets include `Post-Process`, `Stress`, and `Tension`, with formulas that build `load <simulation>.sim` commands and simulation labels.
- The hidden Orcina sheet indicates an Orcina/OrcaFlex workbook integration context (`Version 9.6c`, `Requires 9.3c1`, script file names, arc length fields).

## Bounded extraction decision

The remaining Riser Toolbox files include very large `.xlsm` workbooks. This first pass intentionally did not parse every cell in those large files into wiki text; the raw files remain link-only in `/mnt/ace`. A second pass should target one workbook at a time with a specific code-porting objective.

## Cross-links

- Concept: [Riser extreme statistics from OrcaFlex workbooks](../concepts/riser-extreme-statistics-orcaflex-workbooks.md)
- Existing related concept: [VIV Riser Fatigue](../../../engineering/wiki/concepts/viv-riser-fatigue.md)
- Catalog page: [Elements ingest catalog — digitalmodel-riser-toolbox](elements-digitalmodel-riser-toolbox.md)
