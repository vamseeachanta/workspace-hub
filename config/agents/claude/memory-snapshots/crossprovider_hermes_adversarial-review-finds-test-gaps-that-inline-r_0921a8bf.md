---
name: crossprovider hermes adversarial-review-finds-test-gaps-that-inline-r
description: Adversarial review finds test gaps that inline reviews miss
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review, testing, cross-provider, defect-hunting]
---

Codex adversarial review on #2720 discovered that telegram dispatch readiness tests lack stale/spoofed evidence cases, while inline code reviews did not. Cross-provider review (Claude + Codex) is higher-signal than single-provider.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
