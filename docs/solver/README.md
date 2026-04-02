# Solver Queue — Documentation

## Overview

The solver queue enables asynchronous job submission from any machine to
`licensed-win-1` (the only machine with OrcaFlex/OrcaWave licenses). Jobs are
managed via git: submit a YAML job file, the queue processor picks it up, runs
the solver, and commits the results.

## Architecture

```
queue/pending/     <- Submit jobs here (YAML files)
queue/completed/   <- Successful results + metadata
queue/failed/      <- Failed jobs + error info
queue/.processed/  <- Marker files for watch-results.sh
data/solver-results-log.jsonl  <- Metrics log (JSONL)
docs/solver/queue-dashboard.md <- Auto-generated dashboard
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/solver/process-queue.py` | Main queue processor — polls pending/, runs solver, moves to completed/failed |
| `scripts/solver/submit-job.sh` | Submit a single solver job (creates YAML, commits, pushes) |
| `scripts/solver/submit-batch.sh` | Submit multiple jobs from a batch manifest YAML |
| `scripts/solver/validate_manifest.py` | Validate batch manifests before submission (#1650) |
| `scripts/solver/retry_handler.py` | Retry logic with exponential backoff for transient failures (#1654) |
| `scripts/solver/results_dashboard.py` | Generate dashboard from JSONL results log (#1648) |
| `scripts/solver/watch-results.sh` | Watch completed/ for new results, trigger post-processing |
| `scripts/solver/post-process-hook.py` | Extract metrics from results to JSONL log |
| `scripts/solver/queue-health.sh` | Report queue health status (HEALTHY/WARNING/CRITICAL) |

## Quick Start

### Submit a single job

```bash
bash scripts/solver/submit-job.sh orcawave "path/to/model.owd" "My description"
```

### Submit a batch

```bash
# Validate first
uv run python scripts/solver/validate_manifest.py manifests/my-batch.yaml

# Submit (dry-run)
bash scripts/solver/submit-batch.sh manifests/my-batch.yaml --dry-run

# Submit for real
bash scripts/solver/submit-batch.sh manifests/my-batch.yaml
```

### Check queue health

```bash
bash scripts/solver/queue-health.sh
bash scripts/solver/queue-health.sh --json
```

### Generate dashboard

```bash
uv run python scripts/solver/results_dashboard.py
# Output: docs/solver/queue-dashboard.md
```

## Retry Logic (#1654)

When a job fails with a transient error (connection timeout, file lock, network
issues), the retry handler automatically retries with exponential backoff:

- **Max retries**: 3 (configurable)
- **Backoff**: 1s, 2s, 4s (exponential with ±25% jitter)
- **Max delay**: 60s cap
- **Permanent failures**: License errors, invalid models, parse errors — not retried
- **Logging**: All retry events appended to `data/retry-log.jsonl`

### Transient vs Permanent Classification

| Error Type | Retried? | Examples |
|-----------|----------|----------|
| Connection timeout | Yes | "Connection timed out after 30s" |
| File lock | Yes | "Could not acquire lock on input.owd" |
| Network error | Yes | "Network is unreachable" |
| Git conflict | Yes | "error: failed to push some refs" |
| License error | No | "License check failed: no valid license" |
| Invalid model | No | "Invalid model file format" |
| Unknown solver | No | "Unknown solver: foobar" |
| Parse error | No | "YAML parse error: invalid syntax" |

## Batch Manifest Validation (#1650)

Validate manifests before submission to catch errors early:

```bash
uv run python scripts/solver/validate_manifest.py path/to/manifest.yaml
```

### Checks performed

1. File exists and is valid YAML
2. Has required `jobs` key with non-empty list
3. Each job has required fields: `name`, `solver_type`, `model_file`
4. `solver_type` is valid (`orcawave` or `orcaflex`)
5. No duplicate job names
6. File references exist (warnings only)
7. Schema version compatibility

### Manifest schema

```yaml
schema_version: "1"
jobs:
  - name: my-job
    solver_type: orcawave
    model_file: path/to/model.owd
    description: "Optional description"
```

## Dashboard + Cron (#1648)

The results dashboard is auto-generated from `data/solver-results-log.jsonl`:

- **Watch-results**: Every 4 hours on ace-linux-1 (polls for new completed jobs)
- **Dashboard regen**: Daily at 05:00 UTC on ace-linux-1
- **Output**: `docs/solver/queue-dashboard.md`

Cron entries are declared in `config/scheduled-tasks/schedule-tasks.yaml`:
- `solver-watch-results`: `0 */4 * * *`
- `solver-dashboard`: `0 5 * * *`

## Related Issues

- #1654 — Retry logic with exponential backoff
- #1650 — Batch manifest validation CLI
- #1648 — Watch-results cron + JSONL dashboard
