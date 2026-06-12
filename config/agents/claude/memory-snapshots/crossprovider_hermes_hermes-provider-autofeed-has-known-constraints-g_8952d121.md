---
name: crossprovider hermes hermes-provider-autofeed-has-known-constraints-g
description: Hermes provider autofeed has known constraints: Gemini 429/no-capacity, Codex stdin stall
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, provider-constraints, operational]
---

Gemini Pro/Flash hit repeated 429 errors on capacity exhaustion. Codex lanes experienced stdin stall; replacements use EOF-safe stdin-file pattern. Autofeed can pause at 14/48 runs. Plan parallel work around these constraints.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
