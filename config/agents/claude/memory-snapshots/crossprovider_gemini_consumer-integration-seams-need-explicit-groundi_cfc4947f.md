---
name: crossprovider gemini consumer-integration-seams-need-explicit-groundi
description: Consumer integration seams need explicit grounding
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [api-design, integration-testing, architecture]
---

When adding views/analytics that integrate with downstream consumers, explicitly name the module path and API seam (e.g., `fdas.api.py` exports the disclosure namespace), document what 'unchanged behavior' means, and define regression boundaries (which tests verify no change). Don't assume the seam is obvious.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
