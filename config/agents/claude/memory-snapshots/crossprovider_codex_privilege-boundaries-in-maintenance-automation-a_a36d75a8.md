---
name: crossprovider codex privilege-boundaries-in-maintenance-automation-a
description: Privilege boundaries in maintenance automation are hazardous
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [automation, privilege, safety, cron]
---

User cron with sudo -n lacks proper fail-closed semantics and observability. Automatic package removal (`apt autoremove`, full cache eviction) is too aggressive without explicit approval per tool. Root-owned `/etc/cron.d` entry is structurally different from user crontab executing checkout code — implementation must create root-owned installer, not just user task.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
