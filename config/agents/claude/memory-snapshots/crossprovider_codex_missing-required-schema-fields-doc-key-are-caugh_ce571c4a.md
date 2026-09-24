---
name: crossprovider codex missing-required-schema-fields-doc-key-are-caugh
description: Missing required schema fields (doc_key) are caught by strict validators
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-validation, governance-control, registry-constraint]
---

Domain schemas marking fields as required are enforced at the changed-path validator level. New artifacts missing required fields (e.g., `doc_key` in registry pages) fail hard during validation. This is the control working as designed; it surfaces incomplete specs before approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
