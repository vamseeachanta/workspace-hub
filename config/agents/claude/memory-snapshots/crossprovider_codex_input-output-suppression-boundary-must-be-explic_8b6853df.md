---
name: crossprovider codex input-output-suppression-boundary-must-be-explic
description: Input→output suppression boundary must be explicit
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [schema, governance, requirements]
---

When a plan consumes raw data (labels, exact counts, root names) but claims clean output, explicitly specify what fields are dropped/transformed, not assume suppressions are obvious. Session 5/6: plan claimed no raw labels in output but read manifest with `active_root_label`, `residue_root_label`, exact `file_count` without defining the projection boundary. Document the allowlist: what enters, what is filtered/transformed, what exits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
