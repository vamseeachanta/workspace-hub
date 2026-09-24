---
name: crossprovider codex adversarial-review-must-verify-committed-artifac
description: Adversarial review must verify committed artifacts, not just implementation claims
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-discipline, verification, testing]
---

Code review should verify the actual committed CSV hashes, row counts, manifest digests, and packaged data against the announced contract—not just inspect the implementation. Defects in extraction logic only appear when comparing real emitted rows against the source catalogs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
