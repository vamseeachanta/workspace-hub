---
name: crossprovider codex setup-cron-filters-by-raw-hostname-ignoring-regi
description: Setup-cron filters by raw hostname, ignoring registry aliases
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, hostname-aliasing, registry, installation]
---

setup-cron.sh filters task installation by checking if the raw short hostname appears in each task's machines list, bypassing registry.yaml schedule_variant machinery. A task intended for hostname alias vamsee-linux1 won't install unless machines explicitly includes both the alias and its canonical name. Test coverage for this mismatch is missing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
