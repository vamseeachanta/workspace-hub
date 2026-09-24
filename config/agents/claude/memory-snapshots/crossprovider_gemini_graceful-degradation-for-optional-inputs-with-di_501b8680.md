---
name: crossprovider gemini graceful-degradation-for-optional-inputs-with-di
description: Graceful degradation for optional inputs with diagnostic logging
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [error-handling, robustness, optional-inputs, testing]
---

When optional config/data files are missing, detector must not crash—record skipped inputs in summary report and explicitly test absent-input paths. This robustness pattern prevents cascading failures in analysis tools.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
