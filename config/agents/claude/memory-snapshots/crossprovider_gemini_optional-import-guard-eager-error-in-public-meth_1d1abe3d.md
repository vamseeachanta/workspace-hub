---
name: crossprovider gemini optional-import-guard-eager-error-in-public-meth
description: Optional import guard: eager error in public method, not lazy in generator
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [dependency-guarding, error-handling, python]
---

Place ImportError raise in the public method (e.g., `stream_sample()`), not deferred inside the generator frame. This ensures the error is visible immediately on call, not silently when iteration begins. Prevents users from discovering missing optional dependencies mid-loop.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
