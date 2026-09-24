---
name: crossprovider codex skills-curation-cron-constraint-local-only-deter
description: Skills-curation cron constraint: local-only deterministic
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron-design, architecture-constraint, skills-curation]
---

The `scripts/cron/skills-curation.sh` wrapper must remain local-only deterministic and avoid network posting. Configuration lives at `config/scheduled-tasks/schedule-tasks.yaml` (id: skills-curation, Monday 04:00 schedule). Manual reconciliation should stay outside the cron path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
