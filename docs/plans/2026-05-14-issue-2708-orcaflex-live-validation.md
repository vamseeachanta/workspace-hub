# Plan for #2708: feat(solver-queue): validate OrcaFlex dispatch on licensed-win-1

> **Status:** draft (revised after r1 Claude review — 22 findings addressed)
> **Complexity:** T1
> **Date:** 2026-05-14 (drafted) / 2026-05-15 (r1 revision)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2708
> **Review artifacts:** scripts/review/results/2026-05-14-plan-2708-claude.md (r1 MAJOR; revised below)

---

## Resource Intelligence Summary

### Existing repo code

- EXISTS: `scripts/solver/submit-job.sh:13` — accepts `orcawave | orcaflex`; rejects everything else. **Always writes `export_excel: true` (line 32) — see Finding 4 below for divergence.**
- EXISTS: `scripts/solver/process-queue.py:182-183` — dispatches `orcaflex` to `run_orcaflex()`.
- EXISTS: `scripts/solver/process-queue.py:172-174` — on success, dispatcher MOVES job dir to `COMPLETED_DIR / job_name`.
- EXISTS: `scripts/solver/process-queue.py:207-213` — on failure, dispatcher MOVES job dir to `FAILED_DIR / job_name` (NOT `COMPLETED_DIR`).
- EXISTS: `scripts/solver/process-queue.py:375-411` — `run_orcaflex()` adapter. Accepts `export_excel` parameter but **never uses it** (no `if export_excel:` branch like `run_orcawave():362-371` has). Plain dynamics solve via `OrcFxAPI.Model(...).RunSimulation()`, then `model.SaveSimulation(<stem>.sim)`. No xlsx export path.
- EXISTS: `scripts/solver/watch-results.sh:10,91` — separately maintained post-processor. Writes `.done` markers into `queue/.processed/` AFTER a job lands in `queue/completed/`. **Not part of the dispatch path; not under test in this plan.**
- EXISTS: `scripts/solver/post-process-hook.py` — OrcaWave-tuned (metric extraction from `.owr`). Fires from `watch-results.sh`. Not part of `process-queue.py`'s direct path.
- EXISTS: `queue/job-schema.yaml:14` — schema lists `orcawave | orcaflex`.
- EXISTS: `output/orcaflex_validation/pipeline_test_model.dat` — 131,874 bytes, ORCAFLEX header, git-tracked.
- GAP: No `queue/completed/` or `queue/failed/` entry for an OrcaFlex job — confirmed via `ls queue/completed/ queue/failed/` returning OrcaWave-only directory names.

### Standards

Not applicable — operational-validation issue.

### LLM Wiki pages consulted

No relevant wiki pages.

### Documents consulted

- `docs/plans/2026-05-13-issue-2548-control-plane-machine-inventory.md` — adjacent docs work; same git-poll dispatch model.
- Related issue #1586 — parent; "remaining work: validate against real queue use".
- Related issue #2641 — multi-machine inbox parent; AQWA scoped separately.
- `docs/ops/2026-05-04-multimachine-baseline-inventory.md` §5 — OrcaFlex target for licensed Windows only.

### Gaps identified

- No recorded OrcaFlex dispatch result on licensed-win-1 — code exists, never exercised.
- No smoke-test report convention for non-OrcaWave solvers — this plan establishes it.
- `run_orcaflex()` silently ignores `export_excel: true` — known divergence between submit-job.sh hardcoded YAML and the adapter's parameter handling. Documented here; fix is out of scope for #2708 but filed as follow-up before this issue closes.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-14 via `gh issue view`):
- `#2708` — OPEN — feat(solver-queue): validate OrcaFlex dispatch on licensed-win-1 (#1586 child)
- `#1586` — OPEN — Harden solver queue
- `#2641` — OPEN — multi-machine inbox

**File existence** (`ls -la` 2026-05-14):
- EXISTS: `scripts/solver/submit-job.sh` (1,523 bytes)
- EXISTS: `scripts/solver/process-queue.py` (15,949 bytes)
- EXISTS: `scripts/solver/setup-scheduler.ps1`
- EXISTS: `scripts/solver/watch-results.sh` (separate post-processor)
- EXISTS: `queue/job-schema.yaml`
- EXISTS: `output/orcaflex_validation/pipeline_test_model.dat`
- MISSING (new — this plan creates): `docs/reports/2026-05-14-orcaflex-smoke-validation.md`

**Line excerpts** (verified 2026-05-14):
```
# scripts/solver/submit-job.sh:13-16
if [[ "${SOLVER}" != "orcawave" && "${SOLVER}" != "orcaflex" ]]; then
    echo "ERROR: solver must be 'orcawave' or 'orcaflex', got '${SOLVER}'" >&2
    exit 1
fi

# scripts/solver/submit-job.sh:32 — hardcoded
export_excel: true

# scripts/solver/process-queue.py:182-183
elif solver == "orcaflex":
    result_files = run_orcaflex(input_path, output_dir, export_excel)

# scripts/solver/process-queue.py:172-174 (success path)
shutil.move(str(job_dir), str(COMPLETED_DIR / job_name))

# scripts/solver/process-queue.py:207-213 (failure path)
shutil.move(str(job_dir), str(FAILED_DIR / job_name))

# scripts/solver/process-queue.py:375-411 — run_orcaflex
def run_orcaflex(input_path, output_dir, export_excel):
    # ... loads model, runs simulation, saves .sim
    # NO `if export_excel:` xlsx branch
```

**Setup-scheduler trigger** (`scripts/solver/setup-scheduler.ps1:35-37`):
```
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 30) `
    -RepetitionDuration (New-TimeSpan -Days 3650)
```
**Pickup offset:** the next firing is anchored to whatever wall-clock time `setup-scheduler.ps1` was originally run, NOT a 30-min clock starting at submit time. Worst-case wait = full 30 min; average ~15 min.

**Gap proofs**:
- `ls queue/completed/ 2>&1 | grep -i orcaflex` → no matches
- `ls queue/failed/ 2>&1 | grep -i orcaflex` → no matches
- `git check-ignore queue/completed/anything.sim 2>&1` → (must be run before submission per Finding 10)

**Reproduction proofs**: N/A — positive validation, not failure repro. Implementation exists but unexercised. Intentional skip per `issue-planning-mode` SKILL.md Step 1.5.

<!-- Verification: distinct sources: (1) submit-job.sh, (2) process-queue.py dispatcher + adapters + success+failure paths, (3) job-schema.yaml, (4) watch-results.sh (clarifies it's separate), (5) post-process-hook.py (OrcaWave-tuned), (6) setup-scheduler.ps1 trigger semantics, (7) #1586, (8) #2641, (9) baseline inventory doc, (10) pipeline_test_model.dat. Count: 10 — exceeds minimum 3 ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-14-issue-2708-orcaflex-live-validation.md` |
| Smoke test report | `docs/reports/2026-05-14-orcaflex-smoke-validation.md` |
| Job submission YAML (auto-created) | `queue/pending/<timestamp>-pipeline_test_model.yaml` |
| Expected completion artifact | `queue/completed/<job-name>/result.yaml` + `<stem>.sim` |
| Expected failure artifact | `queue/failed/<job-name>/result.yaml` (if run fails) |
| Plan review — Claude (r1) | `scripts/review/results/2026-05-14-plan-2708-claude.md` |
| Plan review — Claude (r2) | `scripts/review/results/2026-05-15-plan-2708-claude.md` |

---

## Deliverable

An end-to-end OrcaFlex dispatch from this machine (ace-linux-1) through `submit-job.sh`, git push, licensed-win-1 Task Scheduler pickup (15-min average / 30-min worst case wait), and result write-back to either `queue/completed/<job-name>/` (success) or `queue/failed/<job-name>/` (failure) will be performed, with the smoke-test report at `docs/reports/2026-05-14-orcaflex-smoke-validation.md` capturing exact timestamps, durations, artifact paths, and final state for the SUBMITTED job specifically.

---

## Pseudocode

Trivial — see TDD Test List. Operational steps are concrete commands.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Run | `scripts/solver/submit-job.sh orcaflex output/orcaflex_validation/pipeline_test_model.dat "OrcaFlex smoke validation per #2708"` | Submission step |
| Auto-create | `queue/pending/<timestamp>-pipeline_test_model.yaml` | Job YAML written by submit-job.sh |
| Auto-move (success) | `queue/completed/<job-name>/` with `result.yaml` + `.sim` | Result location after licensed-win-1 processes successfully |
| Auto-move (failure) | `queue/failed/<job-name>/` with `result.yaml` | Result location after licensed-win-1 processes with failure |
| Create | `docs/reports/2026-05-14-orcaflex-smoke-validation.md` | Smoke test report with timestamps, durations, artifacts |
| Update | `docs/plans/README.md` | Plan row already added 2026-05-14 commit `4cf347dd2` — no further change |

---

## TDD Test List

Operational verification, not pytest. Each row is a verification command. The first three rows are PRE-FLIGHT — they run BEFORE submission. The remaining rows verify the SUBMITTED job specifically (by captured `${JOB_NAME}`).

| Step | Command | Expected result |
|---|---|---|
| **Pre-flight 0a — scheduled task exists** | (Operator on licensed-win-1) `Get-ScheduledTask -TaskName SolverQueue \| Format-List State,LastRunTime,LastTaskResult` | `State: Ready` (NOT Disabled); `LastTaskResult: 0` (or stale-but-zero); `LastRunTime` within last hour |
| **Pre-flight 0b — watcher state** | (Operator on licensed-win-1) `Get-Process \| Where-Object {$_.CommandLine -like '*watch-results*'}` | Either empty (watcher NOT running — safe) OR documented as running with `.sim`-handling explicitly verified (see Finding 3 below) |
| **Pre-flight 0c — .sim gitignore stance** | `git check-ignore queue/completed/sample.sim 2>&1` followed by `cat .gitignore \| grep -E "\\.sim\|queue/"` | Document the answer in the report. If `.sim` is NOT ignored, also pre-check expected size (`.sim` for this model est. <5 MB based on .dat size); accept commit-back. If `.sim` may exceed 50 MB on this model, decide BEFORE submission whether to add a `.gitignore` rule (out of scope for this issue) or accept the commit-back. |
| **Submit job + capture name** | `JOB_NAME=$(bash scripts/solver/submit-job.sh orcaflex output/orcaflex_validation/pipeline_test_model.dat "OrcaFlex smoke validation per #2708" \| awk '/Job submitted:/ {gsub(/.*queue\\/pending\\/\|\\.yaml/, "", $0); print}')` | `JOB_NAME` is set to `<timestamp>-pipeline_test_model`; commit pushed to origin/main; submission output printed |
| **Verify push landed** | `git fetch origin && git log -1 origin/main --format=%s` | "queue: submit ${JOB_NAME}" (uses explicit fetch — local origin/main ref may be stale otherwise) |
| **Wait for pickup** | Wait up to 30 min (~15 min average per setup-scheduler.ps1 trigger semantics) OR ask user to run `Start-ScheduledTask -TaskName SolverQueue` on licensed-win-1 for instant pickup | (waiting) |
| **Verify outcome — branched** | `git pull && (ls queue/completed/${JOB_NAME}/ 2>/dev/null && echo COMPLETED) \|\| (ls queue/failed/${JOB_NAME}/ 2>/dev/null && echo FAILED) \|\| echo PENDING` | One of: `COMPLETED`, `FAILED`, or `PENDING` (still waiting) |
| **If COMPLETED — verify .sim** | `ls -la queue/completed/${JOB_NAME}/*.sim` | At least one `.sim` file, non-zero bytes |
| **If COMPLETED — verify result.yaml** | `grep "^status:" queue/completed/${JOB_NAME}/result.yaml` | `status: completed` |
| **If FAILED — capture diagnostic** | `cat queue/failed/${JOB_NAME}/result.yaml` | YAML with `status: failed` and error message; copy into report |
| **Report written** | `ls docs/reports/2026-05-14-orcaflex-smoke-validation.md` | File exists |

---

## Acceptance Criteria

- [ ] Pre-flight steps 0a-0c will be executed and their outputs captured in the report before submission
- [ ] `submit-job.sh orcaflex output/orcaflex_validation/pipeline_test_model.dat "..."` will succeed, print the job path, push commit; `${JOB_NAME}` will be captured for downstream verification
- [ ] licensed-win-1 will pick up the job within 30 min (or operator will manually trigger SolverQueue task for instant pickup)
- [ ] Exactly one of `queue/completed/${JOB_NAME}/` OR `queue/failed/${JOB_NAME}/` will exist after pickup — the branched verify command confirms which
- [ ] If COMPLETED: a `.sim` file will exist in `queue/completed/${JOB_NAME}/`; `result.yaml` will contain `status: completed`
- [ ] If FAILED: `result.yaml` in `queue/failed/${JOB_NAME}/` will contain `status: failed` with a captured error message; a fix-it follow-up issue will be filed before #2708 closes
- [ ] `docs/reports/2026-05-14-orcaflex-smoke-validation.md` will document the SUBMITTED JOB specifically (by `${JOB_NAME}`) with submit-timestamp, pickup-timestamp, completion-timestamp, durations, and full artifact paths — NOT a claim that `queue/pending/` is empty (other submitters may have queued jobs concurrently)
- [ ] The `export_excel: true` → `run_orcaflex()` ignores divergence (Finding 4) will be documented in the report and a separate fix-it issue will be filed regardless of outcome

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (r1) | MAJOR | 3 blockers + 7 MINOR; all addressed in this revision (see "Revisions made" below) |
| Claude (r2) | PENDING | — |

**Overall result (r1):** MAJOR — revised. r2 pending.

**Revisions made based on r1 review:**
1. **Blocker 1** — TDD "Verify pickup occurred" now reads `queue/completed/${JOB_NAME}/` and `queue/failed/${JOB_NAME}/` (the two dispatcher write paths) via a branched check. `.processed/` is documented as `watch-results.sh`-owned and explicitly out of the verification chain.
2. **Blocker 2** — TDD list now has explicit "If FAILED" branch with diagnostic capture, so the operator can distinguish "not picked up" from "picked up and failed".
3. **Blocker 3** — Pre-flight 0b checks `watch-results.sh` process state on licensed-win-1. If running, the operator must verify `.sim` handling before submission (cheaper than expanding scope to harden the hook). If not running, submission proceeds. Eliminates the silent-loop risk.
4. **MINOR 4** — `export_excel: true` / `run_orcaflex()` ignore divergence documented in Resource Intelligence and Acceptance Criteria; fix-it follow-up will be filed.
5. **MINOR 5** — AC #6 restated: "the SUBMITTED job will be absent from queue/pending/" (verifiable via `${JOB_NAME}`), not "directory will be empty".
6. **MINOR 6** — Pre-flight 0a added (scheduled task state check) BEFORE the 30-min wait window opens.
7. **MINOR 7** — "Verify push landed" now uses `git fetch origin && git log -1 origin/main`.
8. **MINOR 8** — 30-min trigger semantics explained in Resource Intel + Deliverable: anchored to setup-scheduler.ps1 run time, not submit time. Average ~15 min.
9. **MINOR 9** — TDD row 1 now uses `JOB_NAME=$(...)` capture so downstream rows are runnable verbatim.
10. **MINOR 10** — Pre-flight 0c added: `git check-ignore` for `.sim` and explicit pre-submission size/.gitignore decision.

---

## Risks and Open Questions

- **Risk:** licensed-win-1 may have the SolverQueue task disabled or in an Error state. Pre-flight 0a catches this.
- **Risk:** If watch-results.sh IS running on licensed-win-1 and crashes on `.sim`, it could loop into failure (per r1 Finding 3). Pre-flight 0b requires explicit operator verification before submission.
- **Risk:** `pipeline_test_model.dat` may reference external paths (libraries, included models) that resolve differently on `D:\workspace-hub` than on Linux dev paths. Mitigation: if first run fails with path-not-found errors, inspect the .dat with `OrcFxAPI.Model().LoadData()` locally before re-submitting.
- **Open:** Should `post-process-hook.py` fire for OrcaFlex completion? It is currently OrcaWave-tuned. If watcher is running on licensed-win-1, the hook may error on `.sim`. Pre-flight 0b is the gate. Beyond that, follow-up is separate scope (#1586 or new issue).
- **Open:** Does Finding 4 (`export_excel: true` ignored by `run_orcaflex()`) warrant immediate fix in this PR or a separate one? Plan defers to separate — keeps T1 scope clean.

---

## Complexity: T1

**T1** — operational validation, no new code. Submits one job via existing tooling, runs three pre-flight checks, branches verification on outcome, documents the run. The wait dominates wall-clock; the active work is the pre-flight checks + report.
