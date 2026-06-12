---
name: crossprovider gemini wrk-archival-pattern-move-to-archive-yyyy-mm-set
description: WRK archival pattern: move to archive/YYYY-MM/, set status=archived, record commit hash
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [workflow, history]
---

When archiving a work item: move file to `archive/YYYY-MM/WRK-NNN.md`, set YAML status to `archived`, add `completed_at` ISO timestamp, and record the commit hash (`commit: <sha>`) that marked completion. Enables historical traceability.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
