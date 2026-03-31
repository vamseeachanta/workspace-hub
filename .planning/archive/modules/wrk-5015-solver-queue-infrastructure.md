# WRK-5015 — Solver Queue Infrastructure Plan

**Issue:** GH-1503 | **Machine:** acma-ansys05 (licensed-win-1)
**Approved by:** vamseeachanta (2026-03-30)

---

## Context

This machine (`acma-ansys05`) holds an OrcFxAPI 11.6c licence. The goal is to automate
job processing so that `dev-primary` can push solver jobs via git and have them
auto-executed here every 30 minutes without manual logins.

Prerequisites on this machine (all confirmed):
- Python 3.13.5 ✅
- OrcFxAPI 11.6c ✅
- Git 2.52.0 ✅
- Task Scheduler access (as Administrator) — to be confirmed at runtime

---

## Phase 0 — TDD First (tests before implementation)

Write `scripts/solver/tests/test-process-queue.py` covering:

| Test class | Cases |
|------------|-------|
| `TestJobYamlSchema` | valid job loads OK; missing `solver` key raises; unknown solver raises |
| `TestQueuePoller` | empty pending dir → no-op; one job YAML → processed; completed job not re-processed |
| `TestOrcaWaveRunner` | valid `.owd` path → `OrcFxAPI.Diffraction` called; bad path → `JobError` raised |
| `TestOrcaFlexRunner` | valid `.dat` path → `OrcFxAPI.Model` called; bad path → `JobError` raised |
| `TestOutputLayout` | after run, `queue/completed/JOBID/` contains result file + `job.yaml` |

Run: `uv run python -m pytest scripts/solver/tests/ -v` — all RED before Phase 1.

---

## Phase 1 — Core: process-queue.py (Claude leads)

**File:** `scripts/solver/process-queue.py`

```
Entry point:  python process-queue.py [--repo-root PATH] [--dry-run]
```

### Logic

```
1. git pull origin main  (fetch latest pending jobs)
2. scan queue/pending/*.yaml
3. for each YAML:
   a. parse + validate schema
   b. dispatch to solver runner (orcawave | orcaflex)
   c. write output to queue/completed/JOBID/
   d. move YAML to queue/completed/JOBID/job.yaml
   e. append line to queue/solver-queue.log
4. git add queue/completed/ queue/solver-queue.log
5. git commit -m "chore(queue): process JOBID [auto]"
6. git push origin main
```

### Key functions

| Function | Responsibility |
|----------|---------------|
| `load_job(path)` | Parse YAML, validate schema, return `JobSpec` dataclass |
| `run_orcawave(job, repo_root)` | `OrcFxAPI.Diffraction(input_file).Calculate().SaveResults(out_path)` |
| `run_orcaflex(job, repo_root)` | `OrcFxAPI.Model(input_file) → .RunSimulation() → .SaveSimulation(out_path)` |
| `process_queue(repo_root, dry_run)` | Main loop: scan → dispatch → commit |
| `log_entry(job, status, elapsed)` | Append structured line to `queue/solver-queue.log` |

### Error handling

- Any `JobError` → move YAML to `queue/failed/JOBID.yaml`, log error, continue next job
- Git push failure → log warning, leave completed files for next run to retry
- Never raise from top-level — Task Scheduler must not see non-zero exit for transient errors

### Reviewer assignment

- **Claude**: initial implementation + self-review
- **Codex**: correctness review (OrcFxAPI API usage, error paths) — **hard gate**
- **Gemini**: defensive review (silent failures, git race conditions)

---

## Phase 2 — Windows Task Scheduler: setup-scheduler.ps1 (Claude leads, Gemini reviews)

**File:** `scripts/solver/setup-scheduler.ps1`

```powershell
# Must be run as Administrator
$RepoRoot = "D:\workspace-hub"
$PythonExe = (& uv python find)
$ScriptPath = "$RepoRoot\scripts\solver\process-queue.py"
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument $ScriptPath -WorkingDirectory $RepoRoot
$Trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 30) -Once -At (Get-Date)
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 25) -MultipleInstances IgnoreNew
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName "SolverQueue" -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force
```

### Gemini review focus

- Principal / privilege minimisation (SYSTEM vs named service account)
- Execution time limit vs solver runtime for large models
- `-MultipleInstances IgnoreNew` — correct concurrency behaviour?
- Idempotency: `-Force` overwrites existing task cleanly

---

## Phase 3 — Submission helper: submit-job.sh (Claude)

**File:** `scripts/solver/submit-job.sh`

```bash
#!/usr/bin/env bash
# Usage: bash submit-job.sh orcawave <input_file> <description>
set -euo pipefail
SOLVER=$1; INPUT=$2; DESC=$3
JOBID="$(date +%Y%m%d-%H%M%S)-${SOLVER}"
YAML="queue/pending/${JOBID}.yaml"
cat > "$YAML" <<EOF
id: ${JOBID}
solver: ${SOLVER}
input_file: "${INPUT}"
description: "${DESC}"
submitted_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
submitted_by: "$(hostname)"
EOF
git add "$YAML"
git commit -m "chore(queue): submit ${SOLVER} job ${JOBID}"
git push origin main
echo "Job submitted: ${JOBID}"
```

---

## Phase 4 — Verification & GH-1503 close-out

Run the full issue verification block from PowerShell (as Administrator):

```powershell
cd D:\workspace-hub
git pull origin main
python --version
python -c "import OrcFxAPI; print(f'OrcFxAPI DLL: {OrcFxAPI.DLLVersion()}')"
git --version; git remote -v
Get-ScheduledTask -TaskName 'SolverQueue' | Format-List TaskName,State
Start-ScheduledTask -TaskName 'SolverQueue'
Start-Sleep -Seconds 30
Get-Content queue\solver-queue.log -Tail 20
```

Post output as comment on GH-1503. Close issue.

---

## Stage 6 — Cross-Review Matrix

| File | Claude | Codex (hard gate) | Gemini |
|------|--------|-------------------|--------|
| `process-queue.py` | ✅ self | ⬜ required | ⬜ advisory |
| `setup-scheduler.ps1` | ✅ self | ⬜ advisory | ⬜ required |
| `submit-job.sh` | ✅ self | ⬜ advisory | — |
| `test-process-queue.py` | ✅ self | ⬜ required | — |

Command: `scripts/review/cross-review.sh scripts/solver/process-queue.py all`

---

## Execution Order

```
Stage 0  → TDD: write all tests (RED)
Stage 10 → Phase 1: process-queue.py (GREEN)
Stage 10 → Phase 2: setup-scheduler.ps1
Stage 10 → Phase 3: submit-job.sh
Stage 10 → Phase 4: queue/ directory structure
Stage 6  → Cross-review (Claude/Codex/Gemini)
Stage 7  → Gate evidence verification
Stage 15 → Run setup-scheduler.ps1 (as Admin)
Stage 15 → End-to-end smoke test
Stage 15 → Post GH-1503 comment + close
Stage 20 → Archive WRK-5015
```

---

## Decisions (approved 2026-03-30)

1. **Git credentials** — use SYSTEM account. Git credential manager must be pre-configured
   for SYSTEM on this machine; validate during Phase 4 smoke test.
2. **Solver scope** — Phase 1 includes both `run_orcawave()` and `run_orcaflex()`. Avoids
   rework; both share the same queue/dispatch pattern.
3. **Execution time limit** — start at 25 min; `process-queue.py` will log elapsed time per
   job so the limit can be raised in `setup-scheduler.ps1` once real runtimes are observed.
4. **Concurrency (`IgnoreNew`)** — confirmed correct. If a solver run outlasts the 30-min
   trigger interval, the duplicate trigger is silently dropped. The next tick picks up any
   remaining jobs once the long run finishes. No backlog accumulation.
