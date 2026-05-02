---
title: "Deep extraction — Elements suction pile sizing corpus"
tags: [elements-ingest, suction-pile, api-rp-2a, geotechnical, offshore-foundations, deep-extraction]
sources:
  - /mnt/ace/digitalmodel/references/suction-pile-sizing/SUCTION PILE SIZING PROGRAM.pdf
  - /mnt/ace/digitalmodel/references/suction-pile-sizing/SUCPILE.xlsm
  - /mnt/ace/digitalmodel/references/suction-pile-sizing/pile soil defl i doris system-suction pile.xlsm
  - workspace-hub#2536
added: 2026-04-28
last_updated: 2026-04-28
domain: marine-engineering
---

# Deep extraction — Elements suction pile sizing corpus

This page captures the first-pass extraction from the small Elements suction pile sizing corpus. Raw files remain in `/mnt/ace/digitalmodel/references/suction-pile-sizing/`; wiki content is metadata and methodology summary only.

## Source files inspected

| File | Size | Extraction result |
|---|---:|---|
| `SUCTION PILE SIZING PROGRAM.pdf` | 94,745 bytes | `pdftotext -layout`; 251 extracted lines |
| `SUCPILE.xlsm` | 53,804 bytes | workbook structure via `openpyxl`; formulas preserved as metadata |
| `pile soil defl i doris system-suction pile.xlsm` | 62,339 bytes | workbook structure via `openpyxl`; formulas preserved as metadata |

## Extracted method summary

- The program is an Excel-based Doris suction pile sizing workbook with the original execution location noted as a Doris T: drive path.
- The sizing method treats global pile behavior as rigid-body rotation in deforming soil, with local shell deformation treated as a later detail-design/stiffening problem.
- Lateral resistance and angular deflection are based on API RP-2A `p-y` relationships for sand and clay soils.
- Vertical resistance and pull-out factor of safety are based on API RP-2A `t-z` relationships.
- Soil layers are modeled independently in their zones; the input format supports a practical limit of 10 layers for preliminary sizing.
- Overburden pressure is computed along depth to determine API parameters including clay shallow/deep boundary `Xr`.
- Solver residuals combine force and moment imbalance; solution target is stated as 1/100th of applied load with a 1,000 iteration cap.
- Newton's method is used; valid preliminary problems are expected to converge quickly, often within 50 iterations.

## User inputs identified

| Group | Inputs |
|---|---|
| Pile geometry | diameter, wall thickness, pile length, embedded depth, water-table depth |
| Loads | lateral force, vertical force, applied moment, force elevation from bottom of pile |
| Installation/model flags | plugged/unplugged indicator, number of soil layers/divisions |
| Soil layers | depth, soil type (`s` sand / `c` clay), wet in-situ density, friction angle, cohesion, epsilon strain at 50% unconfined shear strength |

## Workbook structure

| Workbook | Sheet | Rows | Columns | Non-empty cells | Formula cells |
|---|---:|---:|---:|---:|---:|
| `SUCPILE.xlsm` | `Sheet1` | 92 | 20 | 1287 | 466 |
| `SUCPILE.xlsm` | `wall evaluation` | 13 | 5 | 30 | 9 |
| `SUCPILE.xlsm` | `Sheet3` | 1 | 1 | 0 | 0 |
| `pile soil defl i doris system-suction pile.xlsm` | `Sheet1` | 1001 | 13 | 490 | 109 |
| `pile soil defl i doris system-suction pile.xlsm` | `Sheet2` | 1 | 1 | 0 | 0 |

## Acceptance / caution notes

- This is a methodology extraction, not a certified design tool validation.
- The source PDF cites API RP-2A 1993; any production reuse should reconcile with current API RP 2GEO/API RP 2A lineage and project-specific geotechnical data.
- The workbook has macros/VBA context and Doris system dependencies; do not assume standalone execution without a controlled reproduction task.

## Cross-links

- Concept: [Suction pile preliminary sizing with API p-y/t-z curves](../concepts/suction-pile-preliminary-sizing-api-py-tz.md)
- Existing related concept: [Pile Capacity — Alpha Method](../../../engineering/wiki/concepts/pile-capacity-alpha-method.md)
- Catalog page: [Elements ingest catalog — digitalmodel-suction-pile-sizing](elements-digitalmodel-suction-pile-sizing.md)
