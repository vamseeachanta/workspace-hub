---
name: crossprovider hermes file-disposition-decisions-must-reconcile-agains
description: File disposition decisions must reconcile against prior architecture ratifications
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, integration-planning, prior-art]
---

Elements external-drive ingest requires cross-linking against workspace-hub#1544 (canonical /mnt/ace/<repo-name>/<domain>/ layout) and #1355/#1540/#1757/#1904 (consolidation/dedup decisions) before finalizing folder placements. Layout decisions are load-bearing and cannot be made in isolation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
