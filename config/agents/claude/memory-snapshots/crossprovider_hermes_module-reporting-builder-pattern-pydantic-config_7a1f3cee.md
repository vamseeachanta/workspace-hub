---
name: crossprovider hermes module-reporting-builder-pattern-pydantic-config
description: Module reporting builder pattern: Pydantic config + section-based decomposition
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [reporting-architecture, builder-pattern, fault-tolerance]
---

OrcaWave and OrcaFlex reporting use identical pattern: config.py (Pydantic ReportConfig), builder.py (orchestrator), sections/ (8 standalone builders per section: model_summary, rao_plots, hydro_matrices, etc). Each section is fault-tolerant (catches exceptions, shows error badges). Output: self-contained HTML with embedded Plotly.js charts. Config enables per-section enable/disable. This pattern generalizes to any multi-section report (code reviews, design specs, project assessments).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
