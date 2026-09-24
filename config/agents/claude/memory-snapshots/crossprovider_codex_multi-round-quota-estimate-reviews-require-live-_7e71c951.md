---
name: crossprovider codex multi-round-quota-estimate-reviews-require-live-
description: Multi-round quota/estimate reviews require live producer evidence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [quota, testing, verification, semantics]
---

Test passes do not verify cache-fallback semantics, reset-fallback polarity, or estimate source naming; multi-agent reviews must cite live producer mappings (e.g., `.primary.usedPercent` for Codex 5h polarity) and empirically confirm correctness across r1/r2/r3 rounds rather than relying on code inspection alone.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
