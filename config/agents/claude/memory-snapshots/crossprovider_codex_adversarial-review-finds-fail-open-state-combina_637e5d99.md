---
name: crossprovider codex adversarial-review-finds-fail-open-state-combina
description: Adversarial review finds fail-open state combinations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, review-technique, state-machine]
---

Independent boolean flags that control access can combine into contradictory states. Adversarial review must probe whether incompatible states can coexist—e.g., public AND private, owned AND unowned simultaneously.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
