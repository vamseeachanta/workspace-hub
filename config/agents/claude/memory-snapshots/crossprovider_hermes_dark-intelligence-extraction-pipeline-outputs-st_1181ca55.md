---
name: crossprovider hermes dark-intelligence-extraction-pipeline-outputs-st
description: Dark intelligence extraction pipeline outputs stuck as TODO stubs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dark-intelligence, code-generation, technical-debt]
---

Mature Excel formula extraction pipeline exists (656K+ formulas extracted from 6 workbooks via 12+ scripts) but outputs are gitignored TODO stubs in digitalmodel/calculations.py, not wired into modules. Priority 1 ROI: wire existing extractions (SN curves, flowback, conductor length) into live modules before batch-processing the 3,600 remaining Excel files.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
