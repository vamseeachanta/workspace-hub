---
name: crossprovider codex stale-local-plan-files-become-handoff-hazards
description: Stale local plan files become handoff hazards
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-maintenance, handoff-hygiene, stale-artifacts]
---

When local plan files reference outdated code paths or CLI commands (e.g., 'modules/metocean/' but code moved to 'metocean/clients/'), the plan stops being a guide and becomes a time trap for the next agent. Refresh local plans when code diverges significantly, or delete them and plan fresh. Stale artifact paths are more damaging than missing plans.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
