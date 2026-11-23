# Plan for #2708: feat(solver-queue): validate OrcaFlex dispatch on licensed-win-1

> **Status:** draft (r1 Claude MAJOR → revised → r2 Claude MAJOR with non-overlapping defects → r3 inline patches applied per `feedback_r3_inline_loop_break_pattern`)
> **Complexity:** T1
> **Date:** 2026-05-14 (drafted) / 2026-05-15 (r1 revision + r2 inline r3 patches)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2708
> **Review artifacts:** scripts/review/results/2026-05-14-plan-2708-claude.md (r1 MAJOR); scripts/review/results/2026-05-15-plan-2708-claude.md (r2 MAJOR — 15 new findings; addressed inline per loop-break rule)

---

## Resource Intelligence Summary

### Existing repo code

- EXISTS: `scripts/solver/submit-job.sh:13` — accepts `orcawave | orcaflex`; rejects everything else. **Always writes `export_excel: true` (line 32) — see Finding 4 below for divergence.**
- EXISTS: `scripts/solver/submit-job.sh:5` — `set -euo pipefail` is active. Implications for downstream `JOB_NAME=$(...)` capture: see r2 Finding 7 below.
- EXISTS: `scripts/solver/submit-job.sh:38-41` — `git add && git commit && git push origin main` runs with NO preceding `git pull`. Submitter push race: see r2 Finding 5 below.
- EXISTS: `scripts/solver/process-queue.py:169-175` — **on each pending job, the dispatcher creates `COMPLETED_DIR/job_name/` BEFORE the solver executes**:
  ```python
  # line 169-175:
  output_dir = COMPLETED_DIR / job_name
  output_dir.mkdir(parents=True, exist_ok=True)
  ...
  completed_job_path = output_dir / job_path.name
  shutil.move(str(job_path), str(completed_job_path))
  ```
  Solver call is at `:180-185`. The directory's existence is NOT a success signal — see r2 Finding 3 below.
- EXISTS: `scripts/solver/process-queue.py:182-183` — dispatches `orcaflex` to `run_orcaflex()`.
- EXISTS: `scripts/solver/process-queue.py:208-214` — failure path has TWO branches:
  ```python
  # line 208-214:
  failed_dir = FAILED_DIR / job_name
  if output_dir.exists():
      shutil.move(str(output_dir), str(failed_dir))
  else:
      failed_dir.mkdir(parents=True, exist_ok=True)
      shutil.move(str(completed_job_path), str(failed_dir / job_path.name))
  ```
  If the solver raised before `output_dir` was populated, the YAML is rescued from inside `output_dir` and re-homed under `failed_dir`. The plan's verification command must tolerate both shapes.
- EXISTS: `scripts/solver/process-queue.py:89-132` — `git_push()` runs after each job batch. If a concurrent push has landed since the most recent `git_pull()` (`:73-86`), the push is rejected; `:495` logs `WARNING: Failed to push results (will retry on next poll)` and the function returns 0. Result file stays only on licensed-win-1 until reconciliation. **Dispatcher push race**: see r2 Finding 4 below.
- EXISTS: `scripts/solver/process-queue.py:375-411` — `run_orcaflex()` adapter. Accepts `export_excel` parameter but **never uses it** (no `if export_excel:` branch like `run_orcawave():362-371` has). Plain dynamics solve via `OrcFxAPI.Model(...).RunSimulation()`, then `model.SaveSimulation(<stem>.sim)`. No xlsx export path.
- EXISTS: `scripts/solver/watch-results.sh:10,91` — separately maintained post-processor. Writes `.done` markers into `queue/.processed/` AFTER a job lands in `queue/completed/`. **Not part of the dispatch path; not under test in this plan.**
- EXISTS: `scripts/solver/post-process-hook.py` — OrcaWave-tuned (metric extraction from `.owr`). Fires from `watch-results.sh`. Not part of `process-queue.py`'s direct path.
- EXISTS: `scripts/solver/setup-scheduler.ps1:44` — `ExecutionTimeLimit (New-TimeSpan -Hours 1)` — Task Scheduler will SIGKILL the process at the 1-hour boundary regardless of whether the solver finished. r2 Finding 3 risk path.
- EXISTS: `queue/job-schema.yaml:14` — schema lists `orcawave | orcaflex`.
- EXISTS: `output/orcaflex_validation/pipeline_test_model.dat` — 131,874 bytes, ORCAFLEX header, git-tracked. **Integrity not pre-verified** — r2 Finding 12 below.
- VERIFIED (r2): `git check-ignore queue/completed/sample.sim` → not ignored. `.gitignore` contains no `.sim` rule. `.sim` files WILL be staged by dispatcher's `git add queue/`. Size hazard — r2 Finding 6 below.
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
- `run_orcaflex()` silently ignores `export_excel: true` — known divergence between submit-job.sh hardcoded YAML and the adapter's parameter handling. Documented here; fix is out of scope for #2708. **Per r2 Finding 11: this divergence is documented in the report only — no separate fix-it issue is required as a #2708 close-gate.** Caller (parent #1586) can decide whether to file as a follow-up.
- `process-queue.py:89-132` and `submit-job.sh:38-41` both push without pre-pull. Concurrent push races are real and unmitigated. **Documented here as known dispatcher/submitter behavior; mitigations applied in TDD pre-flight and retry policy below.** Code-level fix is out of scope for #2708.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-15 via `gh issue view`):
- `#2708` — OPEN — feat(solver-queue): validate OrcaFlex dispatch on licensed-win-1 (#1586 child)
- `#1586` — OPEN — Harden solver queue
- `#2641` — OPEN — multi-machine inbox

**File existence** (`ls -la` 2026-05-15):
- EXISTS: `scripts/solver/submit-job.sh` (1,523 bytes)
- EXISTS: `scripts/solver/process-queue.py` (15,949 bytes)
- EXISTS: `scripts/solver/setup-scheduler.ps1`
- EXISTS: `scripts/solver/watch-results.sh` (separate post-processor)
- EXISTS: `queue/job-schema.yaml`
- EXISTS: `output/orcaflex_validation/pipeline_test_model.dat`
- MISSING (new — this plan creates): `docs/reports/2026-05-15-orcaflex-smoke-validation.md` (date updated per r2 Finding 15)

**Line excerpts** (verified 2026-05-15 via Read; r2 reviewer cross-checked):
```
# scripts/solver/submit-job.sh:13-16
if [[ "${SOLVER}" != "orcawave" && "${SOLVER}" != "orcaflex" ]]; then
    echo "ERROR: solver must be 'orcawave' or 'orcaflex', got '${SOLVER}'" >&2
    exit 1
fi

# scripts/solver/submit-job.sh:32 — hardcoded
export_excel: true

# scripts/solver/process-queue.py:169-175 — directory created BEFORE solver runs
output_dir = COMPLETED_DIR / job_name
output_dir.mkdir(parents=True, exist_ok=True)
completed_job_path = output_dir / job_path.name
shutil.move(str(job_path), str(completed_job_path))

# scripts/solver/process-queue.py:182-183 — solver dispatch
elif solver == "orcaflex":
    result_files = run_orcaflex(input_path, output_dir, export_excel)

# scripts/solver/process-queue.py:208-214 — failure-path two-branch
failed_dir = FAILED_DIR / job_name
if output_dir.exists():
    shutil.move(str(output_dir), str(failed_dir))
else:
    failed_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(completed_job_path), str(failed_dir / job_path.name))

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
**Pickup offset:** next firing is anchored to whatever wall-clock time `setup-scheduler.ps1` was originally run, NOT a 30-min clock from submit time. Worst-case wait = full 30 min; average ~15 min. **Per r2 Finding 10: manual `Start-ScheduledTask` is documented as bypass-only — if used, the test does not validate the scheduler cadence path.**

**Gap proofs**:
- `ls queue/completed/ 2>&1 | grep -i orcaflex` → no matches
- `ls queue/failed/ 2>&1 | grep -i orcaflex` → no matches
- `grep -E "\\.sim|queue/" .gitignore 2>&1` → no matches → `.sim` will be committed

**Reproduction proofs**: N/A — positive validation, not failure repro.

<!-- Verification: distinct sources: (1) submit-job.sh, (2) process-queue.py dispatcher + adapters + early-mkdir + failure-branch + push race, (3) job-schema.yaml, (4) watch-results.sh (clarifies it's separate), (5) post-process-hook.py (OrcaWave-tuned), (6) setup-scheduler.ps1 trigger + ExecutionTimeLimit, (7) #1586, (8) #2641, (9) baseline inventory doc, (10) pipeline_test_model.dat. Count: 10 — exceeds minimum 3 ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-14-issue-2708-orcaflex-live-validation.md` |
| Smoke test report | `docs/reports/2026-05-15-orcaflex-smoke-validation.md` (date set to submission day, not plan-draft day) |
| Job submission YAML (auto-created) | `queue/pending/<timestamp>-pipeline_test_model.yaml` |
| Expected completion artifact | `queue/completed/${JOB_NAME}/result.yaml` (must contain `status: completed`) + `<stem>.sim` |
| Expected failure artifact | `queue/failed/${JOB_NAME}/result.yaml` with `status: failed` (if run fails) |
| Plan review — r1 Claude | `scripts/review/results/2026-05-14-plan-2708-claude.md` (MAJOR, 3 blockers + 7 MINOR) |
| Plan review — r2 Claude | `scripts/review/results/2026-05-15-plan-2708-claude.md` (MAJOR, 15 new non-overlapping findings — addressed inline) |

---

## Deliverable

An end-to-end OrcaFlex dispatch from this machine (ace-linux-1) through `submit-job.sh`, git push, licensed-win-1 Task Scheduler **30-min scheduler-cadence pickup** (manual `Start-ScheduledTask` allowed only for retry, not as the primary validation path), and result write-back to either `queue/completed/${JOB_NAME}/` (success — verified by `result.yaml` `status: completed` field, NOT by directory presence) or `queue/failed/${JOB_NAME}/` (failure) will be performed, with the smoke-test report at `docs/reports/2026-05-15-orcaflex-smoke-validation.md` capturing timestamps, durations, full artifact paths, and reproduction recipe for the SUBMITTED job specifically.

---

## Pseudocode

Trivial — see TDD Test List. Operational steps are concrete commands.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Run | `scripts/solver/submit-job.sh orcaflex output/orcaflex_validation/pipeline_test_model.dat "OrcaFlex smoke validation per #2708"` | Submission step (after pre-flight) |
| Auto-create | `queue/pending/<timestamp>-pipeline_test_model.yaml` | Job YAML written by submit-job.sh |
| Auto-move (success) | `queue/completed/${JOB_NAME}/` with `result.yaml` (`status: completed`) + `.sim` | Result location after licensed-win-1 processes successfully |
| Auto-move (failure) | `queue/failed/${JOB_NAME}/` with `result.yaml` (`status: failed`) | Result location after licensed-win-1 processes with failure |
| Create | `docs/reports/2026-05-15-orcaflex-smoke-validation.md` | Smoke test report with timestamps, durations, artifacts (date set to actual submission day) |
| Update | `docs/plans/README.md` | Plan row already added 2026-05-14 commit `4cf347dd2` — no further change |

---

## TDD Test List

Operational verification, not pytest. Each row is a verification command. Pre-flight rows (0a–0e) run BEFORE submission. The remaining rows verify the SUBMITTED job specifically (by captured `${JOB_NAME}`).

| Step | Command | Expected result |
|---|---|---|
| **Pre-flight 0a — scheduled task exists** (run by Windows operator with RDP/console access to licensed-win-1; SSH not available per registry.yaml) | `Get-ScheduledTask -TaskName SolverQueue \| Format-List State,LastRunTime,LastTaskResult` | `State: Ready` (NOT Disabled); `LastTaskResult: 0` (or stale-but-zero); `LastRunTime` within last hour |
| **Pre-flight 0b — watcher state** (Windows operator, same channel) | `Get-Process \| Where-Object {$_.CommandLine -like '*watch-results*'}` | Either empty (watcher NOT running — safe) OR documented as running with `.sim`-handling explicitly verified |
| **Pre-flight 0c — .sim git-stance** (ace-linux-1) | `git check-ignore queue/completed/sample.sim 2>&1; grep -E "\\.sim\|queue/completed" .gitignore` | Document the answer in the report. **Hard guard**: if `.sim` is NOT ignored AND expected output size is unknown, plan must either (a) add `queue/completed/**/*.sim` to `.gitignore` BEFORE submission (separate commit, out of #2708 scope — defer to follow-up), OR (b) accept that the dispatcher's `git push` could fail if `.sim` exceeds GitHub's 100 MB limit, leaving the result stuck on licensed-win-1 per Finding 4. **No size estimate is made from `.dat` size** (per r2 Finding 6: `.sim` size depends on simulation duration + output channels, not `.dat` bytes). |
| **Pre-flight 0d — model integrity smoke** (ace-linux-1, if `OrcFxAPI` is available locally; else mark "deferred — accept-failure mode if statics fail on licensed-win-1") | `uv run python -c "import OrcFxAPI; m = OrcFxAPI.Model('output/orcaflex_validation/pipeline_test_model.dat'); print('LoadData OK; node count:', m.general.NumberOfStaticAnalysisLines if hasattr(m.general, 'NumberOfStaticAnalysisLines') else 'unknown')"` | Either: success (model loads, no `Include` errors) OR explicit "OrcFxAPI not available locally — proceeding with accept-failure mode: if statics fail on licensed-win-1, the test still validates the dispatch path; statics fix is a separate concern". |
| **Pre-flight 0e — push contention check** (ace-linux-1) | `git fetch origin && [[ $(git rev-list --count HEAD..origin/main) -eq 0 ]]` | exit 0 (no unmerged remote commits). If non-zero: `git pull --rebase origin main` before submitting to avoid r2 Finding 5 submitter-push race. |
| **Submit job + capture name + guard** | `OUT=$(bash scripts/solver/submit-job.sh orcaflex output/orcaflex_validation/pipeline_test_model.dat "OrcaFlex smoke validation per #2708") || { echo "submit-job.sh failed"; exit 1; }; JOB_NAME=$(echo "$OUT" \| awk '/Job submitted:/ {gsub(/.*queue\\/pending\\/\|\\.yaml/, "", $0); print}'); [[ -n "${JOB_NAME}" ]] \|\| { echo "JOB_NAME empty — capture failed"; exit 1; }; echo "JOB_NAME=${JOB_NAME}"` | Exit 0 only if submit-job.sh succeeded AND `JOB_NAME` is non-empty. Defends against r2 Finding 7 (set -e + awk silent-empty hazard). |
| **Verify push landed** | `git fetch origin && git log origin/main -10 --format=%s \| grep -q "queue: submit ${JOB_NAME}"` | exit 0 — submit commit appears in last 10 commits on origin/main (not asserting it's HEAD per r2 Finding 8; dispatcher commits may interleave). |
| **Wait for scheduler pickup** | Wait up to 30 min (~15 min average per setup-scheduler.ps1 trigger semantics). **Manual `Start-ScheduledTask -TaskName SolverQueue` is allowed ONLY for retry after 30-min has elapsed without pickup — not as the primary path**, per r2 Finding 10 (manual trigger bypasses the scheduler-cadence validation #1586 references). | (waiting) |
| **Verify outcome — branched by result.yaml** | `git pull && (grep -q '^status: completed$' "queue/completed/${JOB_NAME}/result.yaml" 2>/dev/null && echo COMPLETED) \|\| (grep -q '^status: failed$' "queue/failed/${JOB_NAME}/result.yaml" 2>/dev/null && echo FAILED) \|\| (test -d "queue/completed/${JOB_NAME}" && echo ABANDONED-completed) \|\| (test -d "queue/failed/${JOB_NAME}" && echo ABANDONED-failed) \|\| echo PENDING` | Exactly one of: `COMPLETED`, `FAILED`, `ABANDONED-completed` (dispatcher killed mid-run before writing result.yaml), `ABANDONED-failed`, `PENDING` (still waiting). Per r2 Finding 3: directory presence is NOT a success signal — only `status: completed` in `result.yaml` is. |
| **If COMPLETED — verify .sim** | `ls -la queue/completed/${JOB_NAME}/*.sim 2>/dev/null \| awk '$5 > 0'` | At least one `.sim` file, non-zero bytes |
| **If FAILED — capture diagnostic** | `cat queue/failed/${JOB_NAME}/result.yaml` | YAML with `status: failed` + error message; copy into report |
| **If ABANDONED-** | Per r2 Finding 3: dispatcher was killed mid-run (Windows reboot, SIGKILL, 1-hour `ExecutionTimeLimit` expiry). Operator must inspect licensed-win-1 logs + decide whether to (a) re-trigger SolverQueue, (b) escalate as a dispatcher bug, or (c) close #2708 as inconclusive. | Report the ABANDONED state + license-host log excerpt |
| **If PENDING after 30 min** | Check dispatcher push race per r2 Finding 4: `Get-Content C:\path\to\queue\solver-queue.log -Tail 50` on licensed-win-1 looking for `WARNING: Failed to push results`. If found: result exists on win-1 but never pushed back; manual reconciliation required. | Capture log + reconcile |
| **Report written** | `ls docs/reports/2026-05-15-orcaflex-smoke-validation.md` | File exists with all timestamps, durations, and the outcome state |

---

## Acceptance Criteria

- [ ] Pre-flight steps 0a–0e will be executed; 0a/0b will be coordinated with a Windows operator (RDP/console to licensed-win-1; SSH unavailable). Their outputs will be captured in the report before submission.
- [ ] `submit-job.sh ...` will succeed; `JOB_NAME` will be captured AND non-empty (guarded with `[[ -n "${JOB_NAME}" ]]` after awk parse, per r2 Finding 7).
- [ ] licensed-win-1 will pick up the job within 30 min via the scheduled poll. Manual `Start-ScheduledTask` is allowed as retry-only, NOT the primary validation path (per r2 Finding 10).
- [ ] The branched verify command will return exactly one of: `COMPLETED`, `FAILED`, `ABANDONED-completed`, `ABANDONED-failed`, `PENDING`. **Outcome is determined by the `result.yaml` `status:` field, not by directory existence** (per r2 Finding 3).
- [ ] If COMPLETED: a non-zero `.sim` file will exist in `queue/completed/${JOB_NAME}/`; `result.yaml` will contain `status: completed`.
- [ ] If FAILED: `result.yaml` in `queue/failed/${JOB_NAME}/` will contain `status: failed` with a captured error message. **Retry policy** (per r2 Finding 13): #2708 may be re-submitted up to twice after a FAILED outcome if the root cause is a fixable model issue (path resolution, missing include, statics convergence) — these do not invalidate the dispatch-path validation. If the third FAILED returns the same root cause OR a dispatcher-level error, #2708 closes as `dispatch-validated; model-blocker recorded as separate concern`.
- [ ] If ABANDONED-*: dispatcher was killed mid-run before writing `result.yaml`. Per r2 Finding 3, this is a real edge case from the early-`mkdir(COMPLETED_DIR/job_name)` behavior at `process-queue.py:169-170`. Plan WILL capture the licensed-win-1 logs and report the abandonment state; closure of #2708 in this state requires user judgment (re-run or escalate).
- [ ] If PENDING after 30 min: dispatcher push-race per r2 Finding 4 is the leading hypothesis; operator will tail `queue/solver-queue.log` on licensed-win-1 and reconcile. Plan does NOT block on closing the upstream code-level race fix (out of scope for #2708).
- [ ] `docs/reports/2026-05-15-orcaflex-smoke-validation.md` will document the SUBMITTED JOB (by `${JOB_NAME}`) with submit-timestamp, pickup-timestamp, completion-timestamp, durations, full artifact paths, AND the pre-flight evidence trail.
- [ ] The `export_excel: true` → `run_orcaflex()` divergence will be documented IN THE REPORT only (per r2 Finding 11: not a #2708-close gate; parent #1586 may file as follow-up at its own discretion).

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (r1) | MAJOR | 3 blockers + 7 MINOR; addressed in r1 revision |
| Claude (r2) | MAJOR | 15 new non-overlapping findings (P0: directory existence is not a success signal; pushes race in dispatcher AND submitter; JOB_NAME capture fragile under set-e; .sim size estimate unsupported; pre-flight authorization unspecified; etc.); addressed inline per `feedback_r3_inline_loop_break_pattern` (no r3 review dispatched) |

**Overall result:** MAJOR (r1) → MAJOR (r2 — non-overlapping) → **inline-r3 patched per loop-break exception**. Status:plan-review surfaced for user approval with FULL provenance recorded. Note: per `feedback_codex_sustained_major_loop`, r1 + r2 with DIFFERENT defects each round is NOT the sustained-MAJOR pattern (that requires 3+ rounds of SAME defects). Loop-break is the documented exception.

**Revisions made based on r1 review** (committed 9d9c6e4c7 / 2026-05-15):
1. TDD pickup-check reads `queue/completed/${JOB_NAME}` AND `queue/failed/${JOB_NAME}` (was wrongly `queue/.processed/` which is owned by `watch-results.sh`)
2. Explicit failure-path branch in TDD list
3. Pre-flight 0b checks `watch-results.sh` state on licensed-win-1
4. export_excel divergence documented
5. AC restated for SUBMITTED job (not directory-empty)
6. Pre-flight 0a (scheduled task state) + 0c (.sim gitignore)
7. git fetch before "Verify push landed"
8. 30-min trigger offset documented
9. JOB_NAME captured at submit time
10. .gitignore + size check for .sim

**Revisions made based on r2 review** (this revision, inline r3 per loop-break rule):
1. **r2 Finding 1** — `process-queue.py:172-174` citation corrected to `:169-175`; framed as "directory created BEFORE solver runs", not "on success".
2. **r2 Finding 2** — `:207-213` citation corrected to `:208-214`; failure-path two-branch conditional documented.
3. **r2 Finding 3 (P0)** — TDD branch decision now uses `grep -q '^status: completed$' result.yaml` (NOT directory existence). Added `ABANDONED-completed`/`ABANDONED-failed` outcome paths for the dispatcher-killed-mid-run edge case that exists because `output_dir.mkdir()` runs before the solver.
4. **r2 Finding 4** — Dispatcher push race documented; `If PENDING after 30 min` TDD row captures it.
5. **r2 Finding 5** — Submitter push race documented; Pre-flight 0e added (`git fetch + rev-list count` check; `git pull --rebase` if non-zero).
6. **r2 Finding 6** — `.sim` size estimate removed entirely. Pre-flight 0c now requires either (a) `.gitignore` rule for `queue/completed/**/*.sim` (separate commit, out of scope) OR (b) accept the push-failure risk per Finding 4.
7. **r2 Finding 7** — TDD "Submit job + capture name" wraps `submit-job.sh` exit-check + `JOB_NAME` capture + `[[ -n "${JOB_NAME}" ]]` guard. All downstream rows now safe against `set -e + awk` silent-empty hazard.
8. **r2 Finding 8** — "Verify push landed" now uses `git log origin/main -10 --format=%s | grep -q "queue: submit ${JOB_NAME}"` (presence in recent history), not HEAD-only assertion.
9. **r2 Finding 9** — Pre-flight 0a/0b explicitly named as Windows-operator tasks (RDP/console; SSH unavailable per registry.yaml). Plan does NOT silently assume autonomous remote execution.
10. **r2 Finding 10** — Manual `Start-ScheduledTask` is allowed ONLY for retry after the 30-min window elapses without pickup. The 30-min scheduler-cadence path IS the primary validation per #1586 reference.
11. **r2 Finding 11** — AC #7's "fix-it issue will be filed regardless of outcome" was a scope expansion. Removed; export_excel divergence is now reported in-document only, with parent #1586 free to file as follow-up at its discretion.
12. **r2 Finding 12** — Pre-flight 0d added: optional `OrcFxAPI.Model().LoadData()` smoke on ace-linux-1. If `OrcFxAPI` unavailable locally, accept-failure mode is documented explicitly.
13. **r2 Finding 13** — Retry policy on FAILED added to AC: up to 2 retries for model-side issues; third FAILED with same root cause closes as `dispatch-validated; model-blocker recorded separately`.
14. **r2 Finding 14** — r1 Revisions item 7 rewording: replaced "now uses git fetch" with the actual racy-assertion fix per Finding 8.
15. **r2 Finding 15** — Report path updated from `docs/reports/2026-05-14-...` to `docs/reports/2026-05-15-...` to match the actual submission day.

---

## Risks and Open Questions

- **Risk:** licensed-win-1 may have the SolverQueue task disabled or in an Error state. Pre-flight 0a catches this.
- **Risk:** If `watch-results.sh` IS running on licensed-win-1 and crashes on `.sim`, it could loop into failure. Pre-flight 0b requires explicit operator verification.
- **Risk:** Dispatcher push race (per r2 Finding 4) means a successful solver run may never push results back if concurrent submitter pushes are landing. Result stays on licensed-win-1 until next poll's `git pull` succeeds. Mitigation: TDD `If PENDING after 30 min` row inspects `queue/solver-queue.log` for `WARNING: Failed to push results`.
- **Risk:** Submitter push race (per r2 Finding 5) — `submit-job.sh:38-41` does `git add && commit && push` with no preceding `pull`. Mitigation: pre-flight 0e + manual `git pull --rebase` before submission.
- **Risk:** Dispatcher killed mid-run after `output_dir.mkdir()` but before solver completion / `result.yaml` write produces an `ABANDONED-completed` state (per r2 Finding 3). Plan acknowledges and reports rather than failing.
- **Risk:** `pipeline_test_model.dat` integrity (statics convergence, external `Include` dependencies) is unverified locally if `OrcFxAPI` is not available on ace-linux-1. Pre-flight 0d documents the deferral.
- **Risk:** `.sim` push-back may exceed GitHub's 100 MB limit. Pre-flight 0c forces an explicit decision; recommendation is to add a `.gitignore` rule for `queue/completed/**/*.sim` in a separate commit before this validation runs.
- **Open:** Should `post-process-hook.py` fire for OrcaFlex completion? Currently OrcaWave-tuned. Pre-flight 0b is the gate. Beyond that, follow-up is separate scope.
- **Open:** Does the `export_excel` divergence merit a follow-up issue? Plan defers to user / parent #1586 (per r2 Finding 11 — not a #2708-close gate).

---

## Complexity: T1

**T1** — operational validation, no new code. Submits one job via existing tooling, runs five pre-flight checks (one Windows-operator coordinated), branches verification on `result.yaml` `status:` field (not directory presence), documents the run. Scope grew between r1 and r2 (more pre-flight, more failure-mode acknowledgment) but the deliverable remains a single smoke-test report; complexity classification is unchanged.
