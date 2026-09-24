---
name: crossprovider codex composite-identity-keys-required-in-multi-accoun
description: Composite identity keys required in multi-account distributed systems
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [distributed-systems, identity-model, schema-design]
---

Workflows spanning multiple accounts need composite primary keys `(account_id, context_id)` baked into JSONL schemas, snapshots, fixtures, pseudocode, and idempotency rules from inception. Single-dimension identity is an architectural error that cascades through implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
