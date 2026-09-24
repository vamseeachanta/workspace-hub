---
name: crossprovider codex safe-cleanup-triage-defaults-to-no-delete-dispos
description: Safe cleanup triage defaults to no-delete disposition
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup-triage, safety-gate, architecture, llm-wiki-pattern]
---

Always hard-code `delete_ready: False` in cleanup reports. Require explicit owner approval, backup/snapshot confirmation, and provenance/history/retention determination before any delete path opens. Avoid older reconciliation patterns that unlink generated manifests; that is not safe precedent for migration residue or archived content.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
