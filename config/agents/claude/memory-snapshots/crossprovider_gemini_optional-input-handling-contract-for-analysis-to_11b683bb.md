---
name: crossprovider gemini optional-input-handling-contract-for-analysis-to
description: Optional input handling contract for analysis tools
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [tool-design, input-contract, graceful-degradation]
---

Distinguish three input categories: reporting-only-optional (missing = no report data), supplemental-if-configured (missing on non-using repos = normal), supplemental-expected (missing when configured = degraded status). Degraded runs emit reports but don't satisfy approval gates. Tests must cover absent input scenarios explicitly.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
