---
name: crossprovider codex hash-framing-doesn-t-mitigate-membership-inferen
description: Hash framing doesn't mitigate membership-inference threat
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [security, threat-model, data-governance, hash-handling]
---

Raw source hashes in public artifacts disclose private-corpus membership regardless of prose context (e.g., 'private ledger example' framing). Classification exemptions like `no_change_private_context` must operate on synthetic/field-name-only values, never assigned raw digests, or the threat model breaks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
