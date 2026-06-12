---
name: crossprovider hermes dark-intelligence-extraction-stuck-at-promotion-
description: Dark intelligence extraction stuck at promotion phase
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dark-intelligence, code-promotion, bottleneck]
---

The extraction pipeline (formula parsing, dependency DAG, code generation) is mature and proven on 6 workbooks with 656K+ formulas extracted, but outputs sit as TODO stubs in digitalmodel/ never wired into live modules. The bottleneck is NOT extraction but promotion—Excel calculations (SN curves, flowback, conductor length) exist as parsed YAML/Python but aren't integrated. Priority 1 for ROI is wiring existing stubs into modules, not extracting more.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
