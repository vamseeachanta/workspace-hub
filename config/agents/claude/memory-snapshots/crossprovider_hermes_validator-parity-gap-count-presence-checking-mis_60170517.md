---
name: crossprovider hermes validator-parity-gap-count-presence-checking-mis
description: Validator parity gap: count/presence checking misses stale artifacts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validator-gap, artifact-staleness, public-repo]
---

Validators checking only section counts/presence, not content alignment, can miss stale or misaligned reports. Example: CSV report counts match but content drifts; lexicographic report filename selection bypasses date validation. **Why:** production validators often optimize for speed; content-hash or date-based comparison adds rigor. **How to apply:** in public-repo validators, add `_validate_content_hash` or date-freshness checks alongside counts; catch both new-content drifts and stale-artifact regressions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
