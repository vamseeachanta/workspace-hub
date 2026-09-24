---
name: crossprovider codex slow-filesystem-audits-benefit-from-targeted-sea
description: Slow filesystem audits benefit from targeted searches over full-tree scans
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, mounted-filesystem, audit-strategy]
---

On slow-mounted storage, full-tree scans and concurrent test execution hang; targeted filename/content grep and count-only inventories complete in reasonable time. Test processes on slow I/O produce long timeouts and incomplete output, making fresh test claims risky without verified completion signals.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
