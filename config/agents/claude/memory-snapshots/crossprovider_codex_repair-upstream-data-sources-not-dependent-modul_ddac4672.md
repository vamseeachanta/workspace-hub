---
name: crossprovider codex repair-upstream-data-sources-not-dependent-modul
description: Repair upstream data sources, not dependent modules
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [data-integrity, architecture]
---

When data inconsistencies are discovered across multiple systems, repair at the source (canonical upstream repo/database) and add regression tests there. Do not patch dependent modules independently—this prevents divergence and forces all consumers to rebuild from the corrected source.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
