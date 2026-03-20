---
name: workstations-comprehensive-learning-integration
description: 'Sub-skill of workstations: comprehensive-learning Integration.'
version: 3.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# comprehensive-learning Integration

## comprehensive-learning Integration


The `cron_variant` field maps directly to `CL_MACHINE_MODE` in the comprehensive-learning
skill. No separate config file needed — the skill reads `hostname` at runtime.

| cron_variant        | Role                                                          | Machine(s)                         |
|---------------------|---------------------------------------------------------------|------------------------------------|
| `full`              | Phases 1–9 locally + Phase 10a compilation + Phase 10 report  | dev-primary                        |
| `contribute`        | Phases 1–9 locally + commit derived state                     | dev-secondary, licensed-win-1, licensed-win-2 |
| `contribute-minimal`| Reserved for machines with no AI CLIs                         | (future machines)                  |
