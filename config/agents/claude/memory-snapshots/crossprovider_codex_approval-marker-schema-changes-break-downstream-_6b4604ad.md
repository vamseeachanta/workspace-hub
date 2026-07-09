---
name: crossprovider codex approval-marker-schema-changes-break-downstream-
description: Approval marker schema changes break downstream validators without compatibility layers
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [schema-evolution, cross-repo, compatibility]
---

Renaming fields in approval markers (e.g., `Reviewed commit:` → `reviewed_commit_sha:`) must be compatible with all downstream validators that parse those markers. If other repos/tools still expect the old spelling, rename breaks their parsing silently. Add an acceptance layer that recognizes both spellings, or coordinate renames across all consumers before field rename.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
