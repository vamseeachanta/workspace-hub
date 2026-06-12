---
name: crossprovider hermes aggressive-token-fragment-redaction-causes-marke
description: Aggressive token fragment redaction causes marker corruption
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [redaction, hermes, string-handling]
---

#2720 redaction uses 4-character token chunks with `.replace()` iteration, causing collisions with substrings like `ACTE` that mutate prior `[REDACTED]` markers into `[RED[REDACTED]D]`. Longer fragments or full-token redaction only is safer; iterative substring replacement is fragile for random-space secrets.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
