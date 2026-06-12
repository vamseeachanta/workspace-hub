---
name: crossprovider codex hostname-to-cron-variant-mapping-for-multihost-d
description: Hostname-to-cron-variant mapping for multihost deployments
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [deployment, cross-platform, automation]
---

Map short hostname to cron_variant (full, contribute, contribute-minimal) via case statement. Windows machines fall through to Task Scheduler instructions instead of cron. Enables single script to serve heterogeneous environments.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
