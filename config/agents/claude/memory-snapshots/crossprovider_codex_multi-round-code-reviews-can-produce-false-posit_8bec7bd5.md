---
name: crossprovider codex multi-round-code-reviews-can-produce-false-posit
description: Multi-round code reviews can produce false positives; diff verification is load-bearing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, false-positives, adversarial-review, verification]
---

Adversarial code reviews that iterate multiple times can surface false positives (e.g., claiming `type: string` was removed from a schema when it was retained but location changed). Each escalated finding must be re-verified directly against the diff hunk, not against prior review summaries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
