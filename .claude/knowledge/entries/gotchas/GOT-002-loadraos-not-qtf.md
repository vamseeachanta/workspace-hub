---
id: GOT-002
type: gotcha
title: "loadRAOsDiffraction is first-order excitation, NOT a QTF quantity"
category: data
tags: [orcawave, qtf, rao, first-order, diffraction]
repos: [digitalmodel]
confidence: 0.95
created: "2026-02-22"
last_validated: "2026-02-22"
source_type: manual
related: [GOT-001]
status: active
access_count: 0
---

# loadRAOsDiffraction is First-Order, NOT a QTF Quantity

## Symptom

Mixing `loadRAOsDiffraction` into QTF comparison plots produces nonsense comparisons. The property name looks like a "load RAO" which might suggest it belongs with QTF force quantities, but it is not.

## Reality

`diff.loadRAOsDiffraction` returns **first-order excitation forces** (shape: `(nheading, nfreq, 6N)` complex, units kN/m). It appears in the Excel "Load RAOs (diffraction)" sheet (20 rows / 11 freq points).

QTF quantities (mean drift, sum-frequency, difference-frequency) are separate and accessed via the `diff.qtf*` properties.

## Fix

Do not include `loadRAOsDiffraction` in QTF comparison plots. Keep it with first-order (linear) RAO analysis only.

## Source

Confirmed in WRK-204 validation suite, Feb 2026. Documented in `MEMORY.md` and `orcawave-lessons.md`.
