---
name: crossprovider hermes three-layer-red-test-pattern-for-public-safe-art
description: Three-layer RED test pattern for public-safe artifact validation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [public-oss, validation, tdd, adversarial-testing, artifact-safety]
---

When generating artifacts from tracked sources for public consumption, explicit RED tests must catch: (1) unresolved/untracked targets leaking into edge artifacts, (2) CSV/JSONL header/count/value divergence, (3) private patterns (absolute paths /mnt /home, vendor names, credentials) in all output surfaces. Existence-only checks miss all three.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
