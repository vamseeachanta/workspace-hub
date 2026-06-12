---
name: crossprovider hermes system-vs-hermes-scheduler-divergence-37-cron-ta
description: System vs. Hermes scheduler divergence: 37 cron tasks vs. 8 Hermes jobs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, scheduler, architecture]
---

The workspace runs 37 system-cron entries (via `setup-cron.sh` from YAML) but only 8 active Hermes cron jobs; this divergence is untracked and affects routing decisions for scheduled AI work. Native-Claude scheduled tasks (e.g., `gsd-researcher` via `claude -p`) need evaluation for Hermes Agent migration or explicit exception documentation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
