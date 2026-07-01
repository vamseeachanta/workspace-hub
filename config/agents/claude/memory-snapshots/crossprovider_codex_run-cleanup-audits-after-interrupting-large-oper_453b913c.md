---
name: crossprovider codex run-cleanup-audits-after-interrupting-large-oper
description: Run cleanup audits after interrupting large operations
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [workflow, cleanup, safety]
---

When interrupting long-running searches or scans, run a cleanup audit to verify no residue (temp files, incomplete state) was left behind. This prevents transient work from contaminating the shared environment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
