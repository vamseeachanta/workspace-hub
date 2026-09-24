---
name: crossprovider codex pre-completion-cleanup-audit-gate-before-marking
description: Pre-completion cleanup audit gate before marking wiki ingest done
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup, verification-gate, quality-assurance]
---

Before final report, run repo cleanup audit: verify no broken wiki links, no temp command artifacts, no untracked residue under /tmp, git status is clean. Prevents orphaned state and ensures future work finds a clean baseline. Manifest as read-only probe when audit script unavailable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
