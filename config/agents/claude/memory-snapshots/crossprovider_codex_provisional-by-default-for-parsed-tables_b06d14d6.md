---
name: crossprovider codex provisional-by-default-for-parsed-tables
description: Provisional-by-default for parsed tables
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [data-modeling, ingest, uncertainty-tracking]
---

Mark parsed tables `parse_status: provisional-unverified` and raw captures `raw-unverified`; NEVER mark as verified on extraction alone. This convention explicitly tracks extraction confidence and avoids false assurance of correctness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
