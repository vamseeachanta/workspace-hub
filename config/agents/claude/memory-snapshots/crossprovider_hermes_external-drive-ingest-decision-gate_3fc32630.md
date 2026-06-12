---
name: crossprovider hermes external-drive-ingest-decision-gate
description: External-drive ingest decision gate
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-ingest, user-gate, external-storage]
---

Before ingesting ambiguous source folders from external drives, require explicit user confirmation on disposition (client project vs. general workflow, project codes, team assignments). Capture decisions in a disposition table; do not proceed with copies/moves until ambiguity is resolved.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
