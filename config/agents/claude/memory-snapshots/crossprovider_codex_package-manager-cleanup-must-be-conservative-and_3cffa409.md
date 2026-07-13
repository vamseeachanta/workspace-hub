---
name: crossprovider codex package-manager-cleanup-must-be-conservative-and
description: Package-manager cleanup must be conservative and bounded
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [cache-maintenance, privilege-escalation, package-managers]
---

`apt autoremove` is unsafe for automated daily maintenance (on this host it proposed removing 266 packages including NVIDIA firmware). Package eviction must remain report-only or explicitly allowlisted. Concurrent cleanup must handle overlap with apt-daily, snapd, journald using nonblocking locks and defined boundary behavior.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
