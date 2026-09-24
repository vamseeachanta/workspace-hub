---
name: crossprovider codex validation-must-verify-derivation-not-just-self-
description: Validation must verify derivation, not just self-consistency
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, integrity-checking, adversarial-testing]
---

Hash validation that checks only internal consistency (supplied digest matches recomputed digest from supplied operands) cannot detect coherently falsified source hashes. Independently recompute digests from pinned sources and disk artifacts before comparison.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
