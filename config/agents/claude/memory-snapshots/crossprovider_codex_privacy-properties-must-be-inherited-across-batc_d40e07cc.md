---
name: crossprovider codex privacy-properties-must-be-inherited-across-batc
description: Privacy properties must be inherited across batch progression, not redefined per batch
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [batch-evolution, privacy-debt, api-contract]
---

Early batches (001-007) used exact labels; batch 008 hardened to opaque handles + HMAC commitments. Later batches can't regress to simpler models without breaking privacy guarantees. New batch implementations should inherit prior batch's privacy model as a minimum, then extend.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
