---
name: crossprovider hermes work-queue-files-should-be-auto-generated-artifa
description: Work queue files should be auto-generated artifacts from label queries
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [automation, github-integration, single-source-of-truth]
---

Generate notes/agent-work-queue.md by querying GitHub labels at runtime (via scripts/refresh-agent-work-queue.sh or on-demand), not by manual maintenance. Keeps the queue always in sync with live issue state without two-phase reconciliation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
