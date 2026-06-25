---
name: crossprovider codex privacy-equivalence-leakage-forbidding-one-field
description: Privacy-equivalence leakage: forbidding one field doesn't block adjacent fields
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [privacy, governance, adjacent-field-leak, equivalent-threat]
---

When defining privacy rules to block specific field names, verify that identity cannot leak through adjacent or semantically-equivalent fields. DNV issue #789 found that forbidding `source_label` but allowing `source_root_labels` still exposed identity; similarly, fallback paths can emit raw source as `source_root` when validation fails. Check field clusters, not individual names.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
