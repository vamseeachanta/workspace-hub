---
name: crossprovider codex non-finite-values-propagate-silently-into-false-
description: Non-finite values propagate silently into false-safe verdicts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [safety, validation]
---

NaN/Inf geometry or loads propagate through comparisons, making them evaluate False and producing incorrect safe verdicts (e.g., 'not buckled') instead of ValidationError. Fail closed: validate non-finite inputs early and explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
