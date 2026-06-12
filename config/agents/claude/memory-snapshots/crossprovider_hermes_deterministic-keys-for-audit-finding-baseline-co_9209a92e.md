---
name: crossprovider hermes deterministic-keys-for-audit-finding-baseline-co
description: Deterministic keys for audit finding baseline compatibility
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit-schema, baseline-matching, key-design, compatibility]
---

v1→v2 audit migrations require explicit key recipes per finding family (e.g., `family + normalized_subject + rule_id + stable_sorted_scope`) to ensure carry-forward matching. Without deterministic keys, every v2 finding is treated as new, breaking waiver semantics and flooding baseline diffs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
