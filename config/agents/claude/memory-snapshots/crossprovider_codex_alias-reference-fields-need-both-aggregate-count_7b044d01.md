---
name: crossprovider codex alias-reference-fields-need-both-aggregate-count
description: Alias/reference fields need both aggregate counts and granular labels to avoid misleading consumers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [metadata, aliases, references, schema-design]
---

Singular alias labels hide when a parent alias has multiple children or unmapped siblings. Fix: plural `alias_of_source_root_labels` list + `alias_unmapped_child_count`. This prevents downstream code from treating broad aliases as single-target and missing scope. Audit reference fields for both aggregates and detail; avoid singular proxy fields when multiplicity is real.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
