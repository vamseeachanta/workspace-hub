# Solver Queue — Setup & Usage

Git-based job queue for dispatching OrcaWave/OrcaFlex solver jobs to licensed-win-1.
No SSH or inbound connections required — licensed-win-1 polls via git pull.

## Architecture

```
dev-primary                        licensed-win-1
───────────                        ──────────────
submit-job.sh                      Task Scheduler (30 min)
  → queue/pending/job.yaml           → git pull
  → git push                         → process-queue.py
                                     → queue/completed/job/
                                     → git push
  ← git pull
  ← results in queue/completed/
```

## One-Time Setup on licensed-win-1

Run these steps once via RDP or physical access. After this, no further logins needed.

### Prerequisites

Verify these are installed (all should already be present):

```powershell
python --version          # 3.9-3.14 required
git --version             # any recent version
python -c "import OrcFxAPI; print(OrcFxAPI.DLLVersion())"  # OrcaFlex must be installed
```

### Steps

```powershell
# 1. Clone or pull the repo
cd D:\workspace-hub          # adjust path as needed
git pull origin main

# 2. Create the Task Scheduler job (run as Administrator)
powershell -ExecutionPolicy Bypass -File .\scripts\solver\setup-scheduler.ps1

# 3. Verify the task was created
Get-ScheduledTask -TaskName 'SolverQueue'

# 4. Test with a manual run
Start-ScheduledTask -TaskName 'SolverQueue'
Start-Sleep -Seconds 30
Get-Content queue\solver-queue.log -Tail 20
```

Expected output: "No pending jobs" (queue is empty).

### Troubleshooting

| Issue | Fix |
|-------|-----|
| `python` not found | Install via `uv python install 3.12` or Windows Store |
| `import OrcFxAPI` fails | Install OrcaFlex from Orcina, then `pip install OrcFxAPI` |
| Task Scheduler permission denied | Run PowerShell as Administrator |
| `git push` fails in queue log | Ensure git credentials are configured: `git config credential.helper manager` |

## Submitting Jobs (from dev-primary)

```bash
# Submit an OrcaWave job
bash scripts/solver/submit-job.sh orcawave \
  "docs/domains/orcawave/L00_validation_wamit/2.1/OrcaWave v11.0 files/test01.owd" \
  "L00 validation smoke test"

# Submit an OrcaFlex job
bash scripts/solver/submit-job.sh orcaflex \
  "path/to/model.dat" \
  "Mooring analysis run"
```

The script creates a YAML job file in `queue/pending/`, commits, and pushes.
licensed-win-1 picks it up within 30 minutes (or trigger manually).

## Checking Results

```bash
git pull origin main
ls queue/completed/         # completed jobs with results
ls queue/failed/            # failed jobs with error details
cat queue/completed/*/result.yaml  # job metadata
```

## Job YAML Format

See `queue/job-schema.yaml` for the full schema. Minimal example:

```yaml
solver: orcawave
input_file: path/to/input.owd
export_excel: true
description: "My analysis job"
```

## Files

| File | Purpose |
|------|---------|
| `scripts/solver/submit-job.sh` | Submit jobs from dev-primary |
| `scripts/solver/process-queue.py` | Process pending jobs (runs on licensed-win-1) |
| `scripts/solver/setup-scheduler.ps1` | One-time Task Scheduler setup |
| `queue/job-schema.yaml` | Job format documentation |
| `queue/pending/` | Jobs waiting to be processed |
| `queue/completed/` | Successful results |
| `queue/failed/` | Failed jobs with error details |
