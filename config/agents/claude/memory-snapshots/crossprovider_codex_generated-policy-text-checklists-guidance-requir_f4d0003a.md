---
name: crossprovider codex generated-policy-text-checklists-guidance-requir
description: Generated policy text (checklists, guidance) requires governance review
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [generated-text, governance, policy-wording]
---

When scripts generate human-readable or governance-facing text (e.g., future_gate_checklist), the wording itself must pass privacy/governance review, not just the underlying data. Hardcoded category names (e.g., 'raw paths', 'source filenames', 'purchaser metadata') in checklist text violate privacy constraints even if actual payloads are abstracted.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
