---
name: crossprovider codex adversarial-review-for-data-bridge-code-must-che
description: Adversarial review for data-bridge code must check atomicity, manifest ordering, and deterministic serialization
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [review, testing, data-integrity]
---

Beyond correctness, review fixture/schema code for TOCTOU races, symlink issues, manifest-last semantics, deterministic MSH2 serialization, and signed-orientation constraints. Synthetic fixtures must reject mutable refs and overclaims at gate time.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
