# Plan for #2708: feat(solver-queue): validate OrcaFlex dispatch on licensed-win-1

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-05-14
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2708
> **Review artifacts:** scripts/review/results/2026-05-14-plan-2708-claude.md

---

## Resource Intelligence Summary

### Existing repo code

- EXISTS: `scripts/solver/submit-job.sh:13` — accepts `orcawave | orcaflex`; rejects everything else.
- EXISTS: `scripts/solver/process-queue.py:182-183` — dispatches `orcaflex` to `run_orcaflex()`.
- EXISTS: `scripts/solver/process-queue.py:375-410` — `run_orcaflex()` adapter wired to `OrcFxAPI.Model`.
- EXISTS: `queue/job-schema.yaml:14` — schema lists `orcawave | orcaflex` as valid solver values.
- EXISTS: `scripts/solver/setup-scheduler.ps1` — Windows Task Scheduler config; polls every 30 minutes via `git pull origin main` then `python process-queue.py`.
- EXISTS: `output/orcaflex_validation/pipeline_test_model.dat` — 131,874 byte file, ORCAFLEX header verified, git-tracked.
- GAP: No `queue/completed/` or `queue/failed/` entry for an OrcaFlex job (only OrcaWave entries) — confirmed via `ls queue/completed/ queue/failed/` returning OrcaWave-only directory names.

### Standards

Not applicable — this is an operational-validation issue.

### LLM Wiki pages consulted

No relevant wiki pages for this dispatch validation.

### Documents consulted

- `docs/plans/2026-05-13-issue-2548-control-plane-machine-inventory.md` — adjacent docs work; describes the git-poll dispatch model used here.
- Related issue #1586 — parent; queue hardening; closing comment states "remaining work: validate against real queue use".
- Related issue #2641 — multi-machine inbox parent; scopes AQWA separately.
- `docs/ops/2026-05-04-multimachine-baseline-inventory.md` §5 — confirms OrcaFlex is target for licensed Windows hosts only.

### Gaps identified

- No recorded OrcaFlex dispatch result on licensed-win-1 — implementation exists, validation does not.
- No smoke-test report convention for non-OrcaWave solvers — this plan establishes the pattern.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-14 via `gh issue view`):
- `#2708` — OPEN — feat(solver-queue): validate OrcaFlex dispatch on licensed-win-1 (#1586 child)
- `#1586` — OPEN — Harden solver queue: batch submission, result watcher, auto post-processing
- `#2641` — OPEN — feat(solver-queue): hands-off multi-machine inbox ingestion for OrcaWave, OrcaFlex, and AQWA

**File existence** (`ls -la` 2026-05-14):
- EXISTS: `scripts/solver/submit-job.sh` (1,523 bytes, executable)
- EXISTS: `scripts/solver/process-queue.py` (15,949 bytes, executable)
- EXISTS: `scripts/solver/setup-scheduler.ps1`
- EXISTS: `queue/job-schema.yaml`
- EXISTS: `output/orcaflex_validation/pipeline_test_model.dat` (131,874 bytes, git-tracked via `git ls-files`)
- MISSING (new — this plan creates): `docs/reports/2026-05-14-orcaflex-smoke-validation.md`

**Line excerpts** (`grep -n` 2026-05-14):
```
# scripts/solver/submit-job.sh:13
if [[ "${SOLVER}" != "orcawave" && "${SOLVER}" != "orcaflex" ]]; then

# scripts/solver/process-queue.py:182-183
elif solver == "orcaflex":
    result_files = run_orcaflex(input_path, output_dir, export_excel)

# queue/job-schema.yaml:14
    solver: "orcawave | orcaflex"
```

**Gap proofs**:
- `ls queue/completed/ 2>&1 | grep -i orcaflex` → no matches → no OrcaFlex job has been processed.
- `ls queue/failed/ 2>&1 | grep -i orcaflex` → no matches → no OrcaFlex job has been attempted.

**Reproduction proofs**:
N/A — this issue is positive validation, not a failure repro. The implementation exists but has never been exercised; this issue exercises it. Marked intentional per `issue-planning-mode` SKILL.md Step 1.5 skip-allowed rule.

<!-- Verification: distinct sources: (1) submit-job.sh, (2) process-queue.py, (3) job-schema.yaml, (4) #1586, (5) #2641, (6) baseline inventory doc, (7) pipeline_test_model.dat. Count: 7 — exceeds minimum 3 ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-14-issue-2708-orcaflex-live-validation.md` |
| Smoke test report | `docs/reports/2026-05-14-orcaflex-smoke-validation.md` |
| Job submission YAML (auto-created) | `queue/pending/<timestamp>-pipeline_test_model.yaml` |
| Expected completion artifact | `queue/completed/<timestamp>-pipeline_test_model/result.yaml` + `.sim` |
| Plan review — Claude | `scripts/review/results/2026-05-14-plan-2708-claude.md` |

---

## Deliverable

An end-to-end OrcaFlex dispatch from this machine (ace-linux-1) through `submit-job.sh`, git push, licensed-win-1 30-min Task Scheduler pickup, and result write-back will be performed, with the smoke-test report at `docs/reports/2026-05-14-orcaflex-smoke-validation.md` capturing exact timestamps, durations, and artifact paths.

---

## Pseudocode

Trivial — see Files to Change. Operational steps are concrete commands, not pseudocode.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Run | `scripts/solver/submit-job.sh orcaflex output/orcaflex_validation/pipeline_test_model.dat "OrcaFlex smoke validation per #2708"` | Submission step |
| Auto-create | `queue/pending/<timestamp>-pipeline_test_model.yaml` | Job YAML written by submit-job.sh |
| Auto-move | `queue/completed/<job-name>/` OR `queue/failed/<job-name>/` | Result location after licensed-win-1 processes |
| Create | `docs/reports/2026-05-14-orcaflex-smoke-validation.md` | Smoke test report with timestamps, durations, artifacts |
| Update | `docs/plans/README.md` | Add plan row |

---

## TDD Test List

Operational verification, not pytest. Each row is a verification command.

| Step | Command | Expected result |
|---|---|---|
| Submit job | `bash scripts/solver/submit-job.sh orcaflex output/orcaflex_validation/pipeline_test_model.dat "OrcaFlex smoke validation per #2708"` | Exit 0; "Job submitted: queue/pending/<timestamp>-pipeline_test_model.yaml" printed; commit pushed to origin/main |
| Verify push landed | `git log -1 origin/main --format=%s` | "queue: submit <job-name>" |
| Wait for pickup | Wait up to 30 min OR ask user to run `Start-ScheduledTask -TaskName SolverQueue` on licensed-win-1 | (waiting; no command output) |
| Verify pickup occurred | `git pull && ls queue/.processed/ \| tail -3` | New entry matches submitted job-name |
| Verify completion | `git pull && ls queue/completed/<job-name>/result.yaml` | File exists |
| Verify completion status | `grep "status:" queue/completed/<job-name>/result.yaml` | `status: completed` |
| Verify .sim artifact | `ls queue/completed/<job-name>/*.sim` | File exists, non-zero bytes |
| Report written | `ls docs/reports/2026-05-14-orcaflex-smoke-validation.md` | File exists |

---

## Acceptance Criteria

- [ ] `submit-job.sh orcaflex output/orcaflex_validation/pipeline_test_model.dat "..."` will succeed, print job path, and push commit
- [ ] licensed-win-1 will pick up the job (within 30 min via scheduled poll, OR by manual trigger)
- [ ] `queue/completed/<job-name>/result.yaml` will contain `status: completed`
- [ ] A `.sim` output file will exist in the completed directory
- [ ] `docs/reports/2026-05-14-orcaflex-smoke-validation.md` will document the run with submit-timestamp, pickup-timestamp, completion-timestamp, durations, and artifact paths
- [ ] No regression: `queue/pending/` will be empty after run (job moved to completed/)
- [ ] If run fails: failure will be recorded under `queue/failed/<job-name>/`, root cause analysed, and a fix-it issue filed before #2708 closes

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |

**Overall result:** PENDING

---

## Risks and Open Questions

- **Risk:** 30-minute polling latency may make this issue feel stuck. Mitigation: user can manually trigger `Start-ScheduledTask -TaskName SolverQueue` on licensed-win-1 from any RDP/console session.
- **Risk:** `pipeline_test_model.dat` may have dependencies (external paths, library references) that fail on `D:\workspace-hub` instead of the dev path. Mitigation: if first run fails, inspect the .dat with `OrcFxAPI.Model().LoadData()` locally for path issues before re-submitting.
- **Risk:** licensed-win-1 may not have the SolverQueue scheduled task running (paused, Windows session locked, AV interference). Pre-flight: ask user to confirm task state via `Get-ScheduledTask -TaskName SolverQueue` before submission.
- **Open:** If the .sim file is large (>50MB), should it be committed back to git or stored outside? Plan recommends commit unless >100MB (then defer to git-LFS or external storage).
- **Open:** Is `post-process-hook.py` expected to fire for OrcaFlex completion? It is currently OrcaWave-tuned (metric extraction from `.owr`). OrcaFlex `.sim` post-processing is separate scope (#1586 or #1698 ANSYS sibling). Plan recommends: if the hook errors on `.sim`, log and skip rather than fail the run; track as follow-up.

---

## Complexity: T1

**T1** — operational validation, no new code. Submits one job via existing tooling, waits for pickup, documents the result. The 30-min wait is the bulk of the wall-clock time; the active work is the report.
