---
name: crossprovider codex apt-autoremove-in-unattended-automation-is-dange
description: APT autoremove in unattended automation is dangerous
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [system-maintenance, automation-safety]
---

Simulation showed removal of 266 packages including dev libraries and NVIDIA firmware. Keep autoremove report-only and require manual review before execution; never auto-run on production systems.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
