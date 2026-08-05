---
name: crossprovider codex exception-detail-loss-in-legacy-compatibility-re
description: Exception detail loss in legacy compatibility refactors
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [backwards-compatibility, error-handling, diagnostics]
---

Old code catching exceptions without binding them (e.g., catching `AbscissaGapError` and emitting generic `INVALID_ABSCISSA`) loses actionable detail. Refactored code must preserve exception detail through new paths or downstream consumers become less informed than the original.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
