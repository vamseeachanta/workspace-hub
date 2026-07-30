---
name: crossprovider codex self-consistency-validation-can-be-coherently-by
description: Self-consistency validation can be coherently bypassed; integrity requires independent source recomputation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [validation-architecture, tamper-evidence, adversarial-testing]
---

Validators that check only JSON shape and internal hash consistency fail against coherent tampering — attackers can falsify all digests together. Integrity checks must independently recompute critical outputs from pinned sources and compare results.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
