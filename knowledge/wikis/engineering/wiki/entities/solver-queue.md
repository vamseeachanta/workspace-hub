---
title: "Solver Queue"
tags: [system, solver, orcaflex, queue, pull-pattern]
sources:
  - solver-queue-architecture-doc
added: 2026-04-08
last_updated: 2026-04-08
---

# Solver Queue

Git-based asynchronous job dispatch system for running OrcaFlex/OrcaWave analyses on a licensed Windows machine behind a corporate firewall.

## Status: PRODUCTION

## Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `submit-job.sh` | `scripts/solver/` | Creates job YAML, validates, commits to `queue/pending/`, pushes |
| `process-queue.py` | `scripts/solver/` | Pulls, processes with OrcFxAPI, pushes results |
| `setup-scheduler.ps1` | `scripts/solver/` | One-time Windows Task Scheduler setup (30-min polling) |
| `job-schema.yaml` | `queue/` | YAML job format spec |

## Job Lifecycle

```
queue/pending/ --> process-queue.py --> queue/completed/{job-name}/ (success)
                                   --> queue/failed/{job-name}/    (error)
```

## Machines

- **dev-primary** (ace-linux-1): submits jobs
- **licensed-win-1** (ACMA-ANSYS05): processes jobs with OrcFxAPI

## Key Features

- Dual solver support: OrcaWave (diffraction) + OrcaFlex (structural dynamics)
- PyYAML optional with built-in flat-key fallback parser
- Python 3.9+ compatible
- Batch manifests for multi-job runs
- Results dashboard and watch-results cron

## Cross-References

- **Related concept**: [Git-Based Pull Queue](../concepts/git-based-pull-queue.md)
- **Related entity**: [digitalmodel](../entities/digitalmodel.md)
