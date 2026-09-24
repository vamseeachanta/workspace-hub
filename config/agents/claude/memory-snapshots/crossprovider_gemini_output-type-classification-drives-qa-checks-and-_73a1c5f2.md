---
name: crossprovider gemini output-type-classification-drives-qa-checks-and-
description: Output type classification drives QA checks and SME routing
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [classification, qa-routing, sme-dispatch, output-type]
---

Classify WRK output type (rao-diffraction, mooring-analysis, mesh, data-pipeline, calculation, code, generic) based on WRK area/title. Type determines which QA checks run (RAO range/symmetry for diffraction, pretension/MBL% for mooring, schema/null-count for data) and which SME skill to dispatch. Type→SME mapping is canonical; query it before choosing verification strategy.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
