---
title: "Riser extreme statistics from OrcaFlex workbooks"
tags: [riser, orcaflex, weibull, gumbel, extreme-statistics, fatigue, post-processing]
sources:
  - ../sources/elements-riser-toolbox-deep-extraction.md
  - /mnt/ace/digitalmodel/references/riser-toolbox
added: 2026-04-28
last_updated: 2026-04-28
domain: marine-engineering
---

# Riser extreme statistics from OrcaFlex workbooks

The Elements Riser Toolbox contains legacy Excel/VBA workflows for post-processing OrcaFlex `.sim` results into stress/tension envelopes and extreme statistics.

## Workflow pattern inferred

1. Generate OrcaFlex simulations across wave headings and random seeds.
2. Load simulation result files using workbook-generated Orcina script/command strings.
3. Extract stress and tension responses along arc length.
4. Sort/aggregate peaks by heading and seed.
5. Fit Weibull/Gumbel-style extreme statistics to estimate design responses.
6. Preserve envelope maxima/minima for stress and tension design review.

## Signals from extracted workbooks

- Case labels include `1000YRPWAVE_<heading>deg_r<seed>`.
- Stress and tension are handled as separate data products.
- Sheets are structured around `SortedPeaks`, `Weibull_Using(X-T)`, `Stress`, `Tension`, and `Post-Process`.
- Hidden Orcina metadata indicates dependency on OrcaFlex/Orcina workbook integration, not plain static spreadsheets.

## Reuse in digitalmodel

A future migration should favor deterministic Python pipelines:

- OrcaFlex result extraction via `OrcFxAPI`,
- tabular intermediate files with explicit units,
- distribution fitting with scipy/statsmodels,
- regression fixtures from a small source workbook,
- HTML/PDF reports for engineering review.

## Cross-links

- Source extraction: [Deep extraction — Elements riser toolbox OrcaFlex statistics workbooks](../sources/elements-riser-toolbox-deep-extraction.md)
- Related concept: [VIV Riser Fatigue](../../../engineering/wiki/concepts/viv-riser-fatigue.md)
