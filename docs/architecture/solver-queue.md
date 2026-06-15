# Solver Queue — Git-Based Pull Queue Architecture

> Reusable pattern: asynchronous job dispatch across firewall-separated machines using git as the transport layer.

## Problem

Corporate firewalls block inbound connections to licensed solver machines (e.g., OrcaFlex on Windows). Traditional SSH-based push models fail. A pull-based architecture using git as the message bus satisfies the constraint: only outbound connections from the solver machine are needed.

## Architecture

dev-primary submits a YAML job file to `queue/pending/` and pushes to GitHub. licensed-win-1 (ACMA-ANSYS05) polls via `git pull` every 30 minutes using Windows Task Scheduler. The queue processor runs each pending job with OrcFxAPI, moves results to `queue/completed/` or `queue/failed/`, and pushes back.

### Data Flow

```
dev-primary                    GitHub                    licensed-win-1
──────────                    ──────                    ──────────────
submit-job.sh ──push──>  queue/pending/job.yaml
                                                   <──pull── Task Scheduler (30 min)
                                                            process-queue.py
                                                            OrcFxAPI execution
                           queue/completed/job.yaml <──push── results + logs
poll for results <──pull──
```

### Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `scripts/solver/submit-job.sh` | dev-primary | Creates job YAML, validates solver type and input file, commits to `queue/pending/`, pushes |
| `scripts/solver/process-queue.py` | licensed-win-1 | Pulls latest, processes pending jobs with OrcFxAPI (OrcaWave + OrcaFlex), pushes results |
| `scripts/solver/setup-scheduler.ps1` | licensed-win-1 | One-time Task Scheduler setup for 30-min polling |
| `queue/job-schema.yaml` | repo root | Documents the YAML job format (required: solver, input_file; optional: export_excel, description) |

### Job Lifecycle

```
queue/pending/  -->  [process-queue.py]  -->  queue/completed/{job-name}/  (success)
                                         -->  queue/failed/{job-name}/     (error)
```

Each completed job gets a `result.yaml` with status, elapsed time, and output file list. Failed jobs include the error message.

## Key Design Decisions

1. **Git as transport** (not SSH, not HTTP API) — zero infrastructure beyond the existing repo
2. **Pull-based polling** (not push) — satisfies corporate firewall; only outbound connections needed
3. **YAML job files** (not database) — human-readable, git-diffable, auditable
4. **PyYAML optional** with built-in flat-key fallback parser — minimal dependencies on solver machine
5. **Python 3.9+ compatible** — matches OrcFxAPI support range (typing.Optional/List, not union syntax)
6. **Dual solver support** — OrcaWave (diffraction analysis) and OrcaFlex (structural dynamics) in one processor

## Reuse Pattern

This pattern applies to any scenario where:
- A compute resource is behind a firewall that blocks inbound connections
- Job throughput is low enough for 30-minute polling latency
- Git is available on both sides
- Jobs are describable as small YAML files

Potential future applications: CFD job dispatch to dev-secondary, FEA batch runs, any licensed-tool automation.

## References

- Phase 7 Plan 02: `.planning/phases/07-solver-verification-gate/07-02-PLAN.md`
- Phase 7 Summary: `.planning/phases/07-solver-verification-gate/07-02-SUMMARY.md`
- Job schema: `queue/job-schema.yaml`
- Memory: `project_solver_queue_architecture.md`
