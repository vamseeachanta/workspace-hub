---
name: crossprovider codex hard-coded-no-delete-disposition-owner-approval-
description: Hard-coded no-delete disposition + owner approval gates are safer than conditional paths
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [safety-defaults, disposition-model, no-delete-gate]
---

Scripts that conditionally enable deletion based on boolean logic (e.g., `if all_signatures_match: mark_delete_candidate`) invite accidental deletion paths. Safer pattern: hard-code `delete_ready: False`, require explicit owner approval, require backup/snapshot ID, and mark 'metadata signatures are not delete evidence.' Reuse the #736 archive cleanup model, not older reconciliation scripts with unlink paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
