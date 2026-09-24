---
name: crossprovider codex pre-completion-cleanup-audit-prevents-session-re
description: Pre-completion cleanup audit prevents session residue accumulation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup, session-hygiene]
---

Running the repository cleanup audit (checking for orphan stashes, lock files, `/tmp/` scratch, and abandoned task-owned edits) before marking a task complete prevents accumulating operational debt. The audit sorts findings into CLEAN / EXPECTED / UNEXPECTED buckets; only CLEAN or named-EXPECTED residue allows completion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
