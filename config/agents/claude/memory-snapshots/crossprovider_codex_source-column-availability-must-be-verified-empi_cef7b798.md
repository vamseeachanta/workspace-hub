---
name: crossprovider codex source-column-availability-must-be-verified-empi
description: Source column availability must be verified empirically, not assumed
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-sources, archive-handling, provenance]
---

Multi-member archives (e.g., PDQ ZIP with many member files) may have promised columns in schema but missing in the actual selected member. Verify column presence at load time and emit provenance metadata in output manifests, not just row counts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
