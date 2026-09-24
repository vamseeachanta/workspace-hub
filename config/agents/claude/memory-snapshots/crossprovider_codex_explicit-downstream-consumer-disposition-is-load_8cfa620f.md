---
name: crossprovider codex explicit-downstream-consumer-disposition-is-load
description: Explicit downstream consumer disposition is load-bearing in cross-provider infrastructure changes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [harness-design, downstream-coupling, config-management]
---

When adding new workstation/capability entries to config (registry, readiness, harness config), you must explicitly identify every downstream script that reads that config and document whether it works unchanged, needs modification, will break, or is out-of-scope. Skipping this creates silent coupling bugs. Example: adding macbook-portable to registry affects workstation-status.sh, ai-tools-status.sh, cron-health-check.sh, and compare-harness-state.sh — each requires explicit disposition.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
