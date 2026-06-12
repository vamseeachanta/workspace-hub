---
name: crossprovider gemini hostname-based-cron-automation-tier-selection-el
description: Hostname-based cron automation tier selection eliminates per-machine setup
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [deployment, multi-machine, automation]
---

Case statement on `hostname -s` maps machines to cron_variant (full/contribute/contribute-minimal); Windows machines print Task Scheduler instructions. Single deployment script auto-configures each machine without manual setup or environment-specific branches.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
