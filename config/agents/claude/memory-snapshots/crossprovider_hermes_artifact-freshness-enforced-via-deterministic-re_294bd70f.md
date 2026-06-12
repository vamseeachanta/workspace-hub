---
name: crossprovider hermes artifact-freshness-enforced-via-deterministic-re
description: Artifact freshness enforced via deterministic regeneration and byte comparison
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, freshness, deterministic-build]
---

Publication-eligible artifacts must be regenerated into a temp directory and byte-compared against committed versions to detect stale source or report drift. Validator mirrors generator scope gates to catch configuration divergence.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
