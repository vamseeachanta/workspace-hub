---
name: crossprovider gemini provider-specific-behaviors-in-cross-review-watc
description: Provider-specific behaviors in cross-review: watchdog, timeout, INVALID_OUTPUT
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [cross-review, provider-behaviors, reliability]
---

Claude: watchdog/PGID cleanup for long review sessions. Codex: INVALID_OUTPUT detection and timeout handling. Gemini: log format divergence (ISO+INFO vs YAML). These are internal to `cross-review.sh all`; orchestrators should not duplicate or override them. Timeout and INVALID_OUTPUT are failure modes to be caught and handled by the unified script, not by individual orchestrators.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
