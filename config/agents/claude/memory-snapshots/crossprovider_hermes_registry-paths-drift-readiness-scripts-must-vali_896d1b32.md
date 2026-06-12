---
name: crossprovider hermes registry-paths-drift-readiness-scripts-must-vali
description: Registry paths drift; readiness scripts must validate actual paths
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [path-management, readiness-checks, drift-detection]
---

Operator maps and cron configs reference mount paths that diverge from reality (e.g., `/mnt/workspace-hub` vs actual `/mnt/local-analysis/workspace-hub`). Readiness probes must validate observed paths and flag stale references.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
