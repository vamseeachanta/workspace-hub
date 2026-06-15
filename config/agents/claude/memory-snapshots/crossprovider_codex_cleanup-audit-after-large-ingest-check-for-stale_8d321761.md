---
name: crossprovider codex cleanup-audit-after-large-ingest-check-for-stale
description: Cleanup audit after large ingest: check for stale scratch and logs
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ingest, cleanup, verification]
---

After ingest work, verify no stale scratch files in `/tmp`, no dangling session logs, no partial commits, and no cleanup locks remain. If destructive cleanup (rm -rf) is blocked by policy, use non-shell deletion or inspection-only verification instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
