# Plan for #2641: Hands-off multi-machine inbox ingestion for OrcaWave, OrcaFlex, and AQWA

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-05-04
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2641
> **Review artifacts:** pending adversarial review

---

## Phase 0: baseline inventory first

Per user guidance, this plan starts with the basic machine/file/repo inventory before solver automation. The live inventory artifact is:

- `docs/ops/2026-05-04-multimachine-baseline-inventory.md`

That inventory answers:

- what each machine's role is;
- which repos should exist on which machines;
- which machines can access `/mnt/ace`, `/mnt/dde`, `/mnt/elements`, rawdata, project data, and llm/wiki/document stores;
- which AI programs are installed on ace-linux-1 and ace-linux-2;
- which simulation tools are available on ace-linux-2 vs licensed Windows hosts;
- what readiness tasks must happen before direct work is deployed from ace-linux-2.

## Executive decision

Use the existing Git-backed solver queue as the later solver-automation backbone, but do **not** start there. First normalize the multi-machine baseline: repos, mounts, AI tools, cron paths, and rawdata/knowledge access.

After that baseline is green: do **not** try to run licensed solvers on `ace-linux-2`.

- `ace-linux-1`: control plane, canonical `/mnt/ace`, queue observability, dashboard/result post-processing.
- `ace-linux-2`: AI worker and open-source engineering/preprocessing node; add inbox ingestion + queue submission only after repo/mount/path/cron readiness is fixed.
- `licensed-win-1` / `licensed-win-2`: solver execution hosts through Windows Task Scheduler + Git Bash because they hold OrcaFlex/ANSYS licenses and currently have no SSH route.

The eventual solver operating model is: **drop files into an inbox -> Linux cron ingests/validates/queues -> Windows licensed host polls and runs -> results committed -> Linux watcher post-processes and reports.**

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/solver/submit-job.sh` exists and creates one queue YAML under `queue/pending/`, commits, and pushes. It currently accepts only `orcawave` and `orcaflex`.
- `scripts/solver/submit-batch.sh` exists and validates a batch manifest with jobs containing `name`, `solver_type`, and `model_file`. It currently rejects anything outside `{orcawave, orcaflex}`.
- `scripts/solver/validate_manifest.py` exists and enforces `VALID_SOLVER_TYPES = {"orcawave", "orcaflex"}`.
- `scripts/solver/process-queue.py` exists and is the Windows-side queue processor; it pulls, processes all `queue/pending/*.yaml`, moves results to completed/failed, and pushes.
- `scripts/solver/watch-results.sh` exists and post-processes `queue/completed/` results on Linux.
- `config/scheduled-tasks/schedule-tasks.yaml` already has `solver-watch-results` and `solver-dashboard`, but does **not** yet have an inbox ingestion task or Windows solver-processing task entry.

### Machine/registry findings

- `config/workstations/registry.yaml` identifies `ace-linux-1` as the dev-primary/control host with workspace at `/mnt/local-analysis/workspace-hub` and knowledge/storage at `/mnt/ace`.
- `config/workstations/registry.yaml` identifies `ace-linux-2` as dev-secondary, but the recorded workspace path is stale (`/mnt/workspace-hub`) relative to observed reality (`/mnt/local-analysis/workspace-hub`).
- `ace-linux-2` has `/mnt/dde`, `/mnt/local-analysis`, and NFS access to ace-linux-1's knowledge store at `/mnt/remote/ace-linux-1/ace`; it does not have direct `/mnt/ace`.
- `licensed-win-1` / `licensed-win-2` are Windows simulation-license hosts with OrcaFlex/ANSYS in the registry, but `ssh: null`; bootstrap must use physical/GUI or pre-existing Windows Task Scheduler/Git Bash.

### Solver capability findings

- `ace-linux-2` has `claude`, `codex`, `hermes`, `gh`, `git`, `uv`, and `tmux`, plus open-source engineering tools such as Gmsh, FreeCAD, Blender, ParaView, CalculiX, QGIS, and GDAL.
- `ace-linux-2` does **not** have `OrcFxAPI`, `OrcaFlex`, `OrcaWave`, `aqwa`, `ansys`, or `matlab`; Python import of `OrcFxAPI` fails.
- Therefore `ace-linux-2` can ingest, validate, preprocess, and dispatch but cannot execute Orcina/ANSYS jobs.

### Gaps identified

- No inbox/drop-folder ingestion tool exists.
- AQWA/ANSYS is not represented in the queue schema, manifest validator, submit scripts, or processor dispatch.
- No machine-capability router exists for solver jobs.
- `ace-linux-2` cron is drifted and references stale `/mnt/workspace-hub` paths.
- Windows licensed-host Task Scheduler entries are not represented with enough concrete installation/verification steps for this new solver processing loop.

### Evidence

**Issue status** (verified 2026-05-05T03:19:28Z via `gh issue view`):
- `#2641` — OPEN — `feat(solver-queue): hands-off multi-machine inbox ingestion for OrcaWave, OrcaFlex, and AQWA`

**Line excerpts:**

`docs/solver/README.md` documents the existing Git-backed queue:
```text
queue/pending/     <- Submit jobs here (YAML files)
queue/completed/   <- Successful results + metadata
queue/failed/      <- Failed jobs + error info
```

`docs/solver/README.md` documents current supported manifest solver types:
```text
Each job has required fields: name, solver_type, model_file
solver_type is valid (orcawave or orcaflex)
```

`config/scheduled-tasks/schedule-tasks.yaml` already defines result-side scheduler entries:
```text
id: solver-watch-results
schedule: "0 */4 * * *"
machines: [ace-linux-1]
```

**Gap proofs:**
- `scripts/solver/validate_manifest.py` has `VALID_SOLVER_TYPES = {"orcawave", "orcaflex"}`; AQWA is absent.
- `queue/job-schema.yaml` documents only `solver: "orcawave | orcaflex"`; AQWA is absent.
- `ace-linux-2` check showed `OrcFxAPI`, `OrcaFlex`, `OrcaWave`, `aqwa`, `ansys`, `matlab` all not found.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-04-issue-2641-multimachine-solver-inbox-ingestion.md` |
| Issue | `https://github.com/vamseeachanta/workspace-hub/issues/2641` |
| Inbox ingestion script | `scripts/solver/ingest-inbox.py` |
| Cron wrapper | `scripts/cron/solver-inbox-ingest.sh` |
| Queue schema | `queue/job-schema.yaml` |
| Manifest validator | `scripts/solver/validate_manifest.py` |
| Single submitter | `scripts/solver/submit-job.sh` |
| Batch submitter | `scripts/solver/submit-batch.sh` |
| Windows queue processor | `scripts/solver/process-queue.py` |
| Scheduled tasks | `config/scheduled-tasks/schedule-tasks.yaml` |
| Solver docs | `docs/solver/README.md` |
| Tests | `tests/solver/test_inbox_ingest.py`, updates to existing solver tests |

---

## Deliverable

A hands-off solver inbox pipeline where a valid manifest/input bundle dropped into a canonical location is automatically validated, queued, routed to the appropriate licensed Windows solver host, processed, and post-processed without manually touching ace-linux-1, ace-linux-2, or the licensed Windows machines after bootstrap.

---

## Concrete operating model

### Canonical directories

Create and document these repo-local paths:

```text
queue/inbox/accepted/      # staging records for accepted submissions
queue/inbox/drop/          # optional repo-local drop location, ignored except manifests/bundles
queue/inbox/quarantine/    # invalid or partially copied submissions with error reports
queue/inbox/archive/       # ingested source manifests/bundles after queue submission
queue/pending/             # existing execution queue
queue/completed/           # existing successful execution outputs
queue/failed/              # existing failed execution outputs
logs/solver/               # ingestion, processing, dashboard logs
```

Shared-store optional mirror:

```text
ace-linux-1: /mnt/ace/solver-inbox/drop/
ace-linux-2: /mnt/remote/ace-linux-1/ace/solver-inbox/drop/
```

Windows workspace remains Git-backed:

```text
licensed-win-1: D:\workspace-hub\queue\pending\
licensed-win-2: D:\workspace-hub\queue\pending\
```

### Job contract v2

Support both existing v1 batch manifests and a richer v2 manifest:

```yaml
schema_version: "2"
batch_id: calm-buoy-rao-sweep-001
submitted_by: vamsee
jobs:
  - name: calm-buoy-orcawave-base
    solver_type: orcawave
    model_file: data/solver-inputs/calm/base.owd
    target_host: licensed-win-1
    output_dir: queue/completed/calm-buoy-orcawave-base
    description: Base OrcaWave diffraction run

  - name: calm-buoy-orcaflex-check
    solver_type: orcaflex
    model_file: data/solver-inputs/calm/check.yml
    target_host: licensed-win-1
    description: OrcaFlex static/dynamic check

  - name: aqwa-unit-box
    solver_type: aqwa
    model_file: data/solver-inputs/aqwa/unit-box.dat
    target_host: licensed-win-2
    description: ANSYS AQWA batch run
```

Accepted solver names:

```text
orcawave
orcaflex
aqwa        # alias for ansys-aqwa
ansys-aqwa  # canonical internal route if needed
```

### Machine routing

| Solver | Execution host | Linux role |
|---|---|---|
| OrcaWave | `licensed-win-1` preferred; `licensed-win-2` fallback if installed | ingest, validate, queue, post-process |
| OrcaFlex | `licensed-win-1` preferred; `licensed-win-2` fallback if installed | ingest, validate, queue, post-process |
| AQWA/ANSYS | `licensed-win-2` preferred unless registry confirms `licensed-win-1` has working AQWA | ingest, validate, queue, post-process |
| Gmsh/OpenFOAM/FreeCAD/CalculiX/QGIS preprocessing | `ace-linux-2` eligible | execute/preprocess and create solver-ready inputs |

### Scheduling

Add canonical scheduled-task entries only through `config/scheduled-tasks/schedule-tasks.yaml`:

1. `solver-inbox-ingest`
   - Machines: `[ace-linux-1, ace-linux-2]`
   - Frequency: every 10-15 minutes, staggered to avoid duplicate races.
   - Command: `bash scripts/cron/solver-inbox-ingest.sh --once`
   - Uses file locks and idempotent markers.

2. `solver-process-queue-windows`
   - Machines: `[licensed-win-1, licensed-win-2]`
   - Scheduler: `windows-task-scheduler`
   - Frequency: every 15-30 minutes.
   - Command: Git Bash runs `uv run --no-project python scripts/solver/process-queue.py --host <host-id>` or equivalent.

3. Keep existing:
   - `solver-watch-results` every 4h on `ace-linux-1`.
   - `solver-dashboard` daily on `ace-linux-1`.

### Race/atomicity rules

- Inbox ingestion must ignore files still being copied. Require either:
  - manifest suffix `.ready.yaml`, or
  - sidecar marker `<batch>.ready`.
- Ingestion uses `flock`/lock file to prevent concurrent Linux ingestion of the same batch.
- Accepted inbox bundles are moved to archive only after queue YAMLs are written and `git push` succeeds.
- Invalid bundles move to quarantine with `error.yaml` and original inputs preserved.
- Windows processor must claim jobs with a host-specific lock/claim marker before running, so two licensed hosts do not execute the same job.

---

## Pseudocode

```text
solver-inbox-ingest.sh:
    set WORKSPACE_HUB from env or git root
    acquire logs/solver/solver-inbox-ingest.lock
    run uv run --no-project python scripts/solver/ingest-inbox.py --once
    append stdout/stderr to logs/solver/inbox-ingest-YYYYMMDD.log

scripts/solver/ingest-inbox.py:
    discover inbox roots from config/env/defaults
    git pull origin main, fail fast if dirty queue paths conflict
    for each manifest matching *.ready.yaml:
        parse YAML
        validate schema and file references
        normalize solver aliases (aqwa -> ansys-aqwa if needed)
        choose target_host from manifest or registry capability map
        write queue/pending/<timestamp>-<job>.yaml atomically via temp + rename
        write acceptance record under queue/inbox/accepted/
        move source manifest/bundle to archive on successful push
        move source manifest/bundle to quarantine on validation error
    git add queue/pending queue/inbox logs? docs? (logs probably local-only unless policy says otherwise)
    git commit/push if pending jobs changed

process-queue.py --host HOST_ID:
    git pull origin main
    load registry capabilities
    list queue/pending/*.yaml
    for each job:
        skip if target_host not this HOST_ID and this host lacks solver capability
        atomically claim job
        dispatch by solver:
            orcawave -> run_orcawave(...)
            orcaflex -> run_orcaflex(...)
            aqwa/ansys-aqwa -> run_aqwa(...)
        move to completed/failed with result.yaml
    git commit/push results
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/solver/ingest-inbox.py` | Main drop-folder ingestion, validation, quarantine, queue creation |
| Create | `scripts/cron/solver-inbox-ingest.sh` | Cron-safe wrapper with lock/log discipline |
| Modify | `scripts/solver/validate_manifest.py` | Support schema v2 and AQWA/ANSYS solver types |
| Modify | `scripts/solver/submit-job.sh` | Accept AQWA/ANSYS and write richer queue YAML while preserving v1 compatibility |
| Modify | `scripts/solver/submit-batch.sh` | Accept AQWA/ANSYS and call shared validator/normalizer |
| Modify | `scripts/solver/process-queue.py` | Add host-aware claim/routing and AQWA dispatch stub/implementation |
| Modify | `queue/job-schema.yaml` | Document v2 queue schema, solver types, host routing, ready markers |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | Add Linux inbox ingestion and Windows process-queue scheduler entries |
| Modify | `docs/solver/README.md` | Operator documentation and bootstrap instructions |
| Modify | `docs/ops/scheduled-tasks.md` | Update machine roles and ace-linux-2 path drift note |
| Modify | `config/workstations/registry.yaml` | Correct ace-linux-2 workspace path or explicitly add alias/symlink contract |
| Create | `tests/solver/test_inbox_ingest.py` | TDD for ingestion/quarantine/atomic queue writes |
| Modify | `tests/solver/test_manifest_validator.py` | AQWA/schema v2 coverage |
| Modify | existing `tests/solver/*` | Queue processor routing, dashboard/health assumptions if needed |

---

## TDD Test List

| Test name | What it verifies |
|---|---|
| `test_manifest_accepts_aqwa_solver_type` | v2 manifest accepts `aqwa` / `ansys-aqwa` |
| `test_manifest_preserves_v1_orcawave_orcaflex_compatibility` | existing manifests still validate |
| `test_inbox_ingest_requires_ready_marker` | partially copied files are ignored |
| `test_inbox_ingest_valid_manifest_creates_pending_jobs` | accepted manifest creates expected `queue/pending/*.yaml` |
| `test_inbox_ingest_invalid_manifest_quarantines_with_error` | invalid bundle moves to quarantine with actionable error file |
| `test_inbox_ingest_is_idempotent` | rerunning ingestion does not duplicate pending jobs |
| `test_router_selects_windows_host_for_aqwa` | AQWA never routes to ace-linux-2 |
| `test_router_selects_licensed_host_for_orcaflex_or_orcawave` | Orcina jobs route to licensed Windows host |
| `test_process_queue_skips_jobs_for_other_host` | host-specific worker does not execute another host's claimed job |
| `test_process_queue_handles_unknown_solver_as_permanent_failure` | unsupported solver fails clearly |

---

## Acceptance Criteria

- [ ] `uv run --no-project python scripts/solver/validate_manifest.py <v2-manifest>` accepts OrcaWave, OrcaFlex, and AQWA examples.
- [ ] `bash scripts/solver/submit-batch.sh <v1-manifest> --dry-run` still works for existing v1 manifests.
- [ ] `bash scripts/cron/solver-inbox-ingest.sh --once --dry-run` reports accepted/quarantined candidates without changing queue state.
- [ ] Dropping a `.ready.yaml` batch into the canonical inbox creates pending jobs and archives the source batch.
- [ ] Invalid/drop-in-progress submissions are quarantined or ignored safely.
- [ ] `process-queue.py` has host-aware routing and does not run licensed solvers on `ace-linux-2`.
- [ ] Windows Task Scheduler bootstrap instructions include exact Git Bash commands for `licensed-win-1` and `licensed-win-2`.
- [ ] `config/scheduled-tasks/schedule-tasks.yaml` validates with the canonical schedule validator.
- [ ] `ace-linux-2` path drift is fixed or documented with a tested symlink; stale direct crontab entries are removed/replaced by generated schedule entries.
- [ ] Solver docs explain drop-folder usage, manifest examples, result locations, and recovery/quarantine handling.

---

## Bootstrap sequence

1. **Plan review gate**
   - Run adversarial review for this plan.
   - Move #2641 to `status:plan-review`.
   - Wait for user approval before code changes.

2. **Linux implementation**
   - Implement validator and ingestion tests first.
   - Implement `ingest-inbox.py` + cron wrapper.
   - Add schedule YAML entries and validate.

3. **ace-linux-2 readiness repair**
   - Sync/pull workspace safely after resolving dirty/untracked files.
   - Correct registry path or create verified `/mnt/workspace-hub -> /mnt/local-analysis/workspace-hub` compatibility symlink.
   - Replace stale remote crontab with generated canonical tasks.

4. **Windows licensed-host bootstrap**
   - On each licensed Windows host, verify Git Bash, `git pull`, Python/uv, OrcFxAPI/OrcaFlex/OrcaWave/ANSYS commands.
   - Install Task Scheduler entries from canonical schedule docs/scripts.
   - Run a dry-run/diagnostic mode before live jobs.

5. **End-to-end smoke**
   - Drop one tiny OrcaWave example and one invalid manifest.
   - Verify accepted job enters pending, invalid one quarantines.
   - Verify Windows processor consumes accepted job and commits result.
   - Verify ace-linux-1 watcher post-processes completed result.

---

## Risks and Open Questions

- **Risk:** Windows hosts have no SSH. Initial Task Scheduler installation/verification still requires physical/GUI access unless a remote management channel is added.
- **Risk:** AQWA batch command details are not yet verified. The plan must include a probe/dry-run adapter before treating AQWA execution as production-ready.
- **Risk:** Git-backed queue can conflict if multiple hosts push simultaneously. Claims and retries must use pull/rebase/push discipline.
- **Risk:** Shared `/mnt/ace` visibility to Windows is not confirmed. The first implementation should prefer repo-local Git-backed manifests and only use shared storage as an optional drop mirror.
- **Open:** Which Windows host should be canonical AQWA runner? Default proposal is `licensed-win-2` until live probes confirm otherwise.
- **Open:** Should large solver input binaries live in Git, `/mnt/ace`, or a hybrid pointer manifest? Default proposal: manifests in Git, large binaries in shared storage with checksum/path fields.

---

## Complexity: T3

**T3** — multi-machine orchestration, schema migration, scheduler changes, Windows licensed-host routing, AQWA support, idempotent ingestion, and cross-host race handling.
