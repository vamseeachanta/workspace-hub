# Disagreement report — plan #2708 (2026-05-15)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

- **Line citation `process-queue.py:172-174` mischaracterizes the dispatcher's behavior.** Plan §"Existing repo code" claims `:172-174` is "on success, dispatcher MOVES job dir to `COMPLETED_DIR / job_name`". Verified actual content at `:169-175`:
-    ```python
-    output_dir = COMPLETED_DIR / job_name          # line 169
-    output_dir.mkdir(parents=True, exist_ok=True)  # line 170
-    completed_job_path = output_dir / job_path.name # line 174
-    shutil.move(str(job_path), str(completed_job_path))  # line 175
-    ```
-    This runs **unconditionally before the solver executes** (solver call is at `:180-185`). It moves the *YAML file* (not a "job dir") INTO an already-mkdir'd `COMPLETED_DIR/job_name/`. The plan's framing as "on success" is wrong by both control-flow and timing.
- **Line citation `process-queue.py:207-213` (failure path) misses the conditional branch.** Plan claims `:207-213 shutil.move(str(job_dir), str(FAILED_DIR / job_name))`. Verified actual at `:208-214`:
-    ```python
-    failed_dir = FAILED_DIR / job_name
-    if output_dir.exists():
-        shutil.move(str(output_dir), str(failed_dir))
-    else:
-        failed_dir.mkdir(parents=True, exist_ok=True)
-        shutil.move(str(completed_job_path), str(failed_dir / job_path.name))
-    ```
-    Two distinct branches exist. The plan cites a flat single-statement form that doesn't match the source. Plan range is also truncated at `:213` (missing `:214`).
- **TDD branch decision command (`ls queue/completed/${JOB_NAME}/`) is not a success signal.** Plan line 160:
-    ```
-    git pull && (ls queue/completed/${JOB_NAME}/ 2>/dev/null && echo COMPLETED) || (ls queue/failed/${JOB_NAME}/ ...)
-    ```
-    Given Finding 1, `queue/completed/${JOB_NAME}/` is created **before** the solver runs. If `process-queue.py` is killed mid-run (Windows reboot, SIGKILL, Task Scheduler 1-hour `ExecutionTimeLimit` expiry — `setup-scheduler.ps1:44`) **before** the except-handler at `:204-224` fires, the COMPLETED directory will exist on licensed-win-1 with just the moved YAML, no `result.yaml`. On the next iteration the dispatcher's `git_push()` (`:89-132`) stages it via `git add queue/` and pushes. ace-linux-1's `git pull` then sees a `queue/completed/${JOB_NAME}/` that means "abandoned" — and the plan branches to COMPLETED. The subsequent `ls *.sim` and `grep status:` rows would fail, but the BRANCH choice is wrong. Correct signal: `grep -q '^status: completed$' queue/completed/${JOB_NAME}/result.yaml`.
- **Dispatcher push race with concurrent submitter is unsurfaced.** `process-queue.py:89-132` does `git add queue/ && git commit && git push origin main`. If any other submitter pushes between licensed-win-1's `git_pull` (`:73-86`) and `git_push`, the push is rejected as non-fast-forward. The dispatcher logs `WARNING: Failed to push results (will retry on next poll)` (`:495`) but returns 0 — the partial result stays *only on licensed-win-1*. ace-linux-1's verify will see PENDING for an unbounded period until licensed-win-1 reconciles. Plan does not list this in §Risks or pre-flight, and there is no mechanism to detect "result exists on win-1 but never pushed".
- **Submitter-side push race in `submit-job.sh` is unsurfaced.** `submit-job.sh:38-41` does `git add && git commit && git push origin main` with no preceding `git pull`. If licensed-win-1 has pushed a result commit since ace-linux-1's last pull, the submitter's push is rejected. Plan AC #2 says push "will succeed" — no condition or retry. Plan does not require a `git pull --rebase` pre-step.
- **`.sim` file size estimate is unsupported.** Plan TDD pre-flight 0c: ".sim for this model est. <5 MB based on .dat size". OrcaFlex `.sim` files store full time-series across all elements × time-step × output channels — the size is governed by simulation duration and output settings inside the `.dat`, not the `.dat` file's own byte count. There is no defensible inference from 131,874 bytes of `.dat` to `<5 MB` of `.sim`. If `.sim` exceeds GitHub's 100 MB limit, the dispatcher's `git_push` fails permanently and the plan stalls in the failure mode of Finding 4 (silent dispatcher state divergence). Plan should specify either (a) an empirical pre-run on an available OrcaFlex install, (b) a hard size guard before commit, or (c) a `.gitignore` rule for `queue/completed/*.sim` with sidecar metadata.
- **`JOB_NAME` capture fragility under failure.** Plan TDD "Submit job + capture name":
-    ```
-    JOB_NAME=$(bash scripts/solver/submit-job.sh ... | awk '/Job submitted:/ {...}')
-    ```
-    `submit-job.sh` has `set -euo pipefail` (`:5`). If `git push` fails (Finding 5) or the file-exists check fails, the script exits 1 *before* the `echo "Job submitted:"` at `:43`. Awk then matches nothing and emits an empty line. `JOB_NAME=""` silently. Every downstream row then operates on `queue/completed//` and `queue/failed//` — `ls` returns the directory listing (not "no such file"), and `echo COMPLETED` fires spuriously. Plan must check `[ -n "${JOB_NAME}" ]` after capture.
- **`git log -1 origin/main` expected output is racy.** Plan TDD "Verify push landed" expects `"queue: submit ${JOB_NAME}"`. But licensed-win-1's dispatcher commit message is `"queue: process completed jobs"` (`:111`). Between `submit-job.sh`'s push (T+0) and the verify step's `git fetch` (T+1), licensed-win-1 may have pushed its own commit on top. Expected output then becomes `"queue: process completed jobs"`, not the plan's stated value. The check needs to assert the *presence* of the submit commit in recent history (e.g., `git log origin/main -5 --format=%s | grep -q "queue: submit ${JOB_NAME}"`), not the HEAD.
- **Pre-flight 0a-0b require human operator on licensed-win-1 that is not authorized in the plan.** Plan AC #1: "Pre-flight steps 0a-0c will be executed and their outputs captured in the report before submission". Steps 0a and 0b are PowerShell commands run *on licensed-win-1*. The plan does not name who runs them, nor does it provide a remote-execution channel (RDP/SSH/git-poll). If the test runs autonomously from ace-linux-1 and no Windows operator is engaged, AC #1 is unsatisfiable. This is either an undocumented manual prerequisite or a missing automation step.
- **`Start-ScheduledTask` "instant pickup" path bypasses the scheduler under test.** Plan §Wait step: "OR ask user to run `Start-ScheduledTask` ... for instant pickup". If the validation goal is "end-to-end dispatch including Task Scheduler polling cadence", manual trigger invalidates the test. If the goal is just "OrcaFlex adapter works on licensed-win-1", the 30-min polling is irrelevant. Plan does not disambiguate, so the AC list permits a result that doesn't actually validate the schedule-driven path #1586 references.
- **AC #7 couples #2708 close to a follow-up issue without scoping it.** "The `export_excel: true` → `run_orcaflex()` ignores divergence will be documented in the report and a separate fix-it issue will be filed regardless of outcome". The divergence is real (verified: `run_orcaflex` has no `if export_excel:` branch). But binding #2708 closure to filing a *new* GitHub issue is a scope expansion that the issue itself does not authorize. Either move this to the parent #1586 punch-list or drop the AC.
- **`pipeline_test_model.dat` integrity is unverified.** The `.dat` is git-tracked at 131,874 bytes and last modified 2026-04-05. Plan §Risks acknowledges path-resolution might fail but does not pre-check (a) statics convergence, (b) external file dependencies (`Include` references inside the .dat), or (c) that the model is actually runnable. If the model fails statics on licensed-win-1, the test reports FAILED — distinguishable from "OrcaFlex dispatch is broken" only by manual inspection of the error message. Plan should add a Linux-side `OrcFxAPI.Model().LoadData()` smoke (mentioned in §Risks but not promoted to pre-flight) OR explicitly accept that a statics failure still validates the dispatch path.
- **No retry/re-submission policy on FAILED.** Plan AC #6 says a failure files a follow-up issue; it does not say whether #2708 can re-submit after fixing the cause or whether #2708 closes as "failed but dispatch worked". Procedural gap.
- **Plan §"Revisions made" item 7 misstates the bug it fixed.** Item 7: "MINOR 7 — 'Verify push landed' now uses `git fetch origin && git log -1 origin/main`." After `git push origin main` succeeds, the local `origin/main` ref is already updated by push — the prior version's defect (whatever it was) is not solved by adding `git fetch`. As noted in Finding 8, the actual defect is the racy expected-output assertion, which the revision did not address.
- **Date drift in artifact filename.** Plan dates itself "2026-05-14 (drafted) / 2026-05-15 (r1 revision)" but the smoke-test report path remains `docs/reports/2026-05-14-orcaflex-smoke-validation.md` (Artifact Map row 2, Files to Change row 5). If the live validation runs on 2026-05-15 or later, the date in the report filename will not match the day the test was actually conducted. Minor but a forensics-trail smell.

