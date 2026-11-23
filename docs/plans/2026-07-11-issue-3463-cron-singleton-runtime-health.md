# Plan for #3463: Cron singleton enforcement and bounded runtime health

> **Status:** plan-review
> **Complexity:** T3
> **Date:** 2026-07-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3463
> **Client:** N/A
> **Lane:** lane:claude
> **Execution mode:** parallel-readonly for planning/review; single-lane for implementation because runtime state, schedule metadata, and health classification share one contract
> **Review artifacts:** `scripts/review/results/2026-07-11-plan-3463-{claude,codex,gemini}-r1.md` | `scripts/review/results/2026-07-11-plan-3463-{claude,codex}-r2.md`
> **Human-facing companion:** `docs/reports/2026-07-11-issue-3463-cron-singleton-runtime-health-plan.html`

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/monitoring/cron-health-check.sh` currently classifies tasks from latest-log presence, age, and error patterns. Its YAML projection excludes command identity, runtime budget, lock policy, and runtime-state evidence, so it cannot distinguish a live task from a stale log or count overlapping invocations.
- `scripts/monitoring/tests/test_cron_health_check.sh` is the canonical behavioral suite. It covers log age, missing logs, error scanning, JSON output, machine filtering, and self-log recursion, but it has no runtime-state, PID-reuse, overlap, or lock-contention fixtures.
- `scripts/cron/cron_render.py` resolves `schedule_by_machine` and substitutes one global `$LOG` per machine variant. For a full variant, `$LOG` resolves to `logs/quality/cron-wrapper.log`, while the `repository-sync` catalog record declares `logs/repository-sync-*.log`.
- `scripts/cron/cron_transaction.py` already supplies fail-closed installed-crontab classification. The implementation will reuse its cataloged/preserved/uncataloged model rather than create a second unmanaged-entry classifier.
- `scripts/cron/harness-update.sh` supplies a nonblocking `flock` precedent, but it silently skips contention with exit 0 and emits no durable machine-readable contention evidence. The new runtime contract will not copy that silent-success behavior.
- `config/scheduled-tasks/schedule-tasks.yaml` intentionally maps `hermes-claude-bridge` to 04:25 on `ace-linux-1` and includes `--commit`. Therefore, 04:25 is expected machine staggering; an installed command without `--commit` is source/install drift.

### Standards and governance

| Contract | Status | Source |
|---|---|---|
| Issue → plan → adversarial review → user approval → TDD | mandatory | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| Canonical schedule authority | active | `config/scheduled-tasks/schedule-tasks.yaml` and `docs/ops/scheduled-tasks.md` |
| Safe crontab convergence | active | `scripts/cron/cron_transaction.py`, issue #2969 |
| Legal/client-identifier scan | mandatory before commit/PR | `.claude/skills/coordination/legal-sanity-scan/SKILL.md` |
| Security baseline | mandatory | loaded `AGENTS.md`: validate input, avoid `eval`, do not expose secrets, fail closed |

### Documents and issues consulted

- [Issue #3463](https://github.com/vamseeachanta/workspace-hub/issues/3463) defines the bounded-audit evidence, no-kill planning boundary, singleton requirement, runtime-health states, and safe termination documentation goal.
- [Issue #1512](https://github.com/vamseeachanta/workspace-hub/issues/1512) establishes log-oriented cross-machine health; this plan will preserve that behavior as an independent health dimension.
- `docs/plans/2026-04-26-issue-2291-cron-health-failure-detection.md` narrows prior health work to log evidence and supplies the canonical TDD suite and JSON compatibility constraints.
- [Issue #3347](https://github.com/vamseeachanta/workspace-hub/issues/3347) owns legacy setup-cron false-SKIP/false-ADD behavior. This plan will test current convergence but will not absorb a general legacy-installer rewrite.
- `docs/plans/2026-05-20-issue-2762-hermes-system-cron-routing-contract.md` and `docs/plans/2026-05-20-issue-2765-scheduler-parity-report-system-cron-hermes-gateway.md` keep scheduler migration and cross-scheduler parity out of scope.
- `docs/ops/scheduled-tasks.md` is the operator-facing inventory, but its task/log table lags the YAML source and will be regenerated or corrected from the canonical contract.
- Drive-index query `cron repository sync overlap runtime health schedule` returns no relevant operational precedent. The `master_document_index` coverage gap reports the reason `unreachable`; unrelated engineering/personal-drive hits will not be persisted.

### Evidence (embedded verification)

**Issue status** (verified 2026-07-11T10:52Z with `gh issue view`):

- [#3463](https://github.com/vamseeachanta/workspace-hub/issues/3463) — OPEN — `status:needs-plan` — `bug(cron): prevent overlapping jobs and add bounded runtime-health detection`
- [#1512](https://github.com/vamseeachanta/workspace-hub/issues/1512) — CLOSED — log-oriented cron health foundation
- [#3347](https://github.com/vamseeachanta/workspace-hub/issues/3347) — OPEN — setup-cron fingerprint false-SKIP/false-ADD

**Line excerpts**:

```text
config/scheduled-tasks/schedule-tasks.yaml:648-660
  ace-linux-1: "25 4 * * *"
  bash scripts/memory/bridge-hermes-claude.sh --commit

config/scheduled-tasks/schedule-tasks.yaml:841-854
  repository-sync schedule: "0 */4 * * *"
  command redirects to $LOG
  declared log: logs/repository-sync-*.log

scripts/cron/cron_render.py:27-28,99-100
  full-variant $LOG: logs/quality/cron-wrapper.log
  contribute-variant $LOG: /tmp/workspace-hub-cron.log
```

**Reproduction proof** (bounded runtime probe, 2026-07-11T05:52:53-05:00):

```text
$ pgrep -af 'scripts/cron-repository-sync.sh|scripts/sync/sync-ecosystem.sh'
1114507 ... bash scripts/cron-repository-sync.sh ...
1540137 ... bash scripts/cron-repository-sync.sh ...
1838041 ... bash scripts/cron-repository-sync.sh ...

$ ps -eo pid,ppid,pgid,sid,etimes,stat,wchan:24,args ...
1114507 ... pgid=1114507 sid=1114507 etimes=35571 do_wait
1540137 ... pgid=1540137 sid=1540137 etimes=21172 do_wait
1838041 ... pgid=1838041 sid=1838041 etimes=6771  do_wait

$ pgrep -afi 'import[-_ ]timing|importtime|python.*-X[[:space:]]+importtime'
<only the probe shell matched; no target process matched>
```

- The live defect matches the issue: **YES** — three independent process groups remain active across successive four-hour ticks.
- The probe also demonstrates why unguarded `pgrep -f` will be rejected as the primary health mechanism: it matches its own shell command.
- No process will be signaled during planning or implementation without a separate, fresh user-approved operational action.

**Pre-existing test baseline** (verified 2026-07-11T11:08Z):

```text
$ uv run pytest scripts/cron/tests/test_validate_schedule.py -q
19 passed, 1 failed
FAILED test_setup_cron_dry_run_expands_workspace_hub_and_log
literal $WORKSPACE_HUB appears in mkdir -p inserted after placeholder expansion
```

- Task 3 will convert this known renderer-order failure from RED to GREEN before adding repository-sync-specific rendering assertions. It will not be treated as a regression introduced by runtime work.

### Gaps identified

- No task-owned runtime evidence contract exists.
- No PID start-token validation exists to distinguish a live owner from PID reuse.
- No durable lock-contention evidence exists.
- No runtime/overlap dimension exists in cron-health JSON or console output.
- No generic semantic validation ties a rendered redirection target to a task's declared `log:` family.
- No safe process-group response runbook exists for operators.

---

## Design Decision

The implementation will use a task-owned runtime record plus a nonblocking singleton lock. The record will contain task ID, PID, process-group/session identifiers, process start token, start timestamp, and lock/result state. Cron health will validate only the bounded PIDs named by opted-in task records; it will not enumerate repository trees or use broad substring process searches.

Repository sync will become the first enforced singleton. Other tasks will opt in by declaring runtime metadata and invoking the same runner in later issue-scoped changes; #3463 will configure only tasks needed to satisfy the reproduced defect and will keep the framework reusable.

Rejected alternatives:

1. `pgrep -f`/substring scans will be rejected because they self-match, confuse wrapper descendants with independent runs, and cannot defeat PID reuse.
2. Per-script ad hoc PID files will be rejected because they duplicate lifecycle and validation logic.
3. systemd/Hermes scheduler migration will be rejected because it expands into #2762/#2765.

---

## Artifact Map

| Artifact | Path |
|---|---|
| Canonical plan | `docs/plans/2026-07-11-issue-3463-cron-singleton-runtime-health.md` |
| Human-facing plan | `docs/reports/2026-07-11-issue-3463-cron-singleton-runtime-health-plan.html` |
| Runtime contract/runner | `scripts/cron/cron_runtime.py` |
| Repository-sync wrapper | `scripts/cron-repository-sync.sh` |
| Health integration | `scripts/monitoring/cron-health-check.sh` |
| Canonical task metadata | `config/scheduled-tasks/schedule-tasks.yaml` |
| Runtime unit tests | `tests/cron/test_cron_runtime.py` |
| Health behavioral tests | `scripts/monitoring/tests/test_cron_health_check.sh` |
| Schedule semantic tests | `scripts/cron/tests/test_validate_schedule.py` |
| Renderer/apply tests | `tests/cron/test_cron_render.py`, `tests/cron/test_cron_apply.py`, `tests/cron/test_cron_transaction.py` |
| Operator inventory | `docs/ops/scheduled-tasks.md` |
| Safe response runbook | `docs/ops/cron-process-response.md` |
| Review artifacts | `scripts/review/results/2026-07-11-plan-3463-*-r1.md`, `scripts/review/results/2026-07-11-plan-3463-*-r2.md` |

---

## Deliverable

A tested, opt-in cron runtime contract will prevent overlapping repository-sync mutation, expose bounded runtime/overlap evidence independently from log health, reconcile canonical/rendered schedule evidence, and document user-gated process-group response.

---

## Interfaces and Pseudocode

### Canonical YAML contract

```yaml
runtime:
  singleton: true
  max_seconds: 10800
  state_dir: .claude/state/cron-runtime/repository-sync
  filesystem_wait_wchans: [request_wait_answer]
```

`validate-schedule.py` will reject non-boolean `singleton`, `max_seconds` outside the fixed inclusive range 60–604,800 seconds (one minute through seven days), absolute/traversing `state_dir` paths, duplicate state directories, malformed wait-channel tokens, and runtime metadata on non-cron tasks. The seven-day ceiling will keep every runtime budget bounded while accommodating the slowest existing weekly maintenance class; repository sync will use 10,800 seconds, below its four-hour cadence.

### Runtime runner

```text
run(task_id, argv, cwd, log_path, schedule):
    load and validate the task's runtime contract from canonical YAML
    open controlled lock path without following an attacker-controlled symlink
    attempt nonblocking exclusive flock
    if contention:
        atomically replace contention.json without modifying active.json
        exit with a documented non-success contention code
    open the validated log path and spawn argv directly in cwd in a new process group
    atomically write active.json with supervisor identity plus child pid, child pgid,
        child /proc start token, and UTC start time
    on TERM/INT/HUP, forward the signal to the child process group
    reap the direct child and poll only the recorded child PGID until it no longer exists,
        while retaining the lock
    atomically write last-result.json with success/failure/signal result
    remove active.json only after the child group exits
    release the lock last
```

### Runtime inspection

```text
inspect(state_dir, now):
    validate active.json, contention.json, and last-result.json independently
    if active.json exists:
        read only its recorded child PID/PGID's /proc start token, stat, and wchan
        if child PID is absent or start token differs: return stale_or_reused_pid
        if contention is newer than active start: return overlap
        if stat/wchan matches configured filesystem-wait evidence: return filesystem_wait
        if elapsed > max_seconds: return excessive_runtime
        return active_within_budget
    if last-result exists and reports zero exit: return completed_success
    if last-result exists and reports nonzero/signal: return completed_failure
    if contention exists without a valid active owner: return orphan_contention
    return never_started
```

### Cron-health composition

```text
for each machine-applicable task:
    calculate existing log_status independently
    if runtime metadata exists:
        calculate runtime_status through cron_runtime.py inspection
    combine with explicit precedence:
        overlap, excessive_runtime, filesystem_wait, completed_failure,
        orphan_contention, or invalid/stale identity => problem / exit 1
        active_within_budget => visible RUNNING dimension; do not erase log evidence
        completed_success => completed runtime dimension; log evidence remains authoritative
        never_started => visible missing runtime evidence for runtime-managed tasks
        unavailable runtime probe => UNKNOWN, visible and fail-closed for singleton tasks
    emit both log_status and runtime_status in JSON
```

The existing top-level `status` field will remain for compatibility and will use documented precedence; new `log_status`, `runtime_status`, `supervisor_pid`, `child_pid`, `child_pgid`, `sid`, `process_state`, `wait_channel`, `elapsed_seconds`, and `evidence_timestamp` fields will provide non-lossy detail. `filesystem_wait` will inspect the recorded mutating child, not the waiting supervisor, and will require either process state `D` or an exact configured wait-channel token. The report will preserve the raw bounded state/wchan evidence so an operator can distinguish a configured match from inference. No environment variables or full command lines will enter the JSON report.

---

## Implementation Tasks and TDD Order

### Task 1: Lock the runtime contract with RED tests

- Add `tests/cron/test_cron_runtime.py` fixtures using temporary directories and short-lived child processes.
- Add failing tests for one successful lock owner, second-run contention, child rather than supervisor identity, lock release after success/error/signal only after the recorded child PGID disappears, forwarded signals, stale PID, PID start-token mismatch, completed success/failure, never-started evidence, filesystem wait, controlled state paths, separate atomic evidence files, and unsupported `/proc` behavior.
- Extend `scripts/cron/tests/test_validate_schedule.py` with failing schema/security tests before adding YAML runtime fields.
- Run the focused tests and retain the expected RED output in the implementation issue comment.

### Task 2: Implement the minimal runtime runner

- Create `scripts/cron/cron_runtime.py` with separate pure parsing/inspection functions and a CLI execution boundary.
- Keep the file below 400 lines and every function below 50 lines.
- Accept `--task-id`, `--cwd`, `--log`, and an argv tail after `--`; reject a compound shell string. Use argv-preserving subprocess execution without `eval`, `shell=True`, or command-string interpolation.
- Spawn the child in a dedicated process group, record the child PID/PGID/start token after spawn, forward TERM/INT/HUP, reap the direct child, and poll only the recorded PGID until it disappears while retaining the singleton lock. No automatic KILL escalation will occur. Repository-sync descendants will be required to remain in that PGID; daemonizing or calling `setsid()` will be a contract violation covered by a negative fixture and documented as unsupported.
- Keep `active.json`, `contention.json`, and `last-result.json` separate. Make each write atomic through same-directory temporary files and rename so a contender cannot overwrite owner identity or completion evidence.
- Re-run Task 1 tests to GREEN, then run `bash -n scripts/cron-repository-sync.sh`.

### Task 3: Enforce repository-sync singleton and correct its log contract

- Preserve the existing failing `test_setup_cron_dry_run_expands_workspace_hub_and_log` as the first RED fixture. Correct renderer ordering so `_ensure_log_dir()` runs before placeholder expansion (or re-expand the inserted prefix), then prove no generated line contains literal `$WORKSPACE_HUB`.
- Extend renderer and validation tests so the repository-sync rendered redirection family equals its declared `log:` family and contains the runtime wrapper invocation.
- Update the repository-sync catalog command and wrapper integration only after those tests fail. `scripts/cron-repository-sync.sh` will be the enforced cron/manual wrapper boundary and will call the runner with structured argv equivalent to `scripts/repository_sync`; the catalog will continue to invoke that wrapper rather than pass a compound command into the runner.
- Preserve the wrapper's dated `logs/repository-sync-*.log` as the canonical execution log; remove reliance on the machine-global `$LOG` for this task.
- Add a hermetic two-invocation test proving only one mutation stub executes and contention produces durable evidence. Add a bypass test proving two direct wrapper invocations cannot overlap; direct invocation of the lower-level `scripts/repository_sync` tool will remain explicitly outside the scheduled-wrapper contract.

### Task 4: Add independent runtime health to cron-health

- Extend the canonical Bash behavioral suite first with fixtures for `never_started`, `active_within_budget`, `completed_success`, `completed_failure`, `filesystem_wait`, `excessive_runtime`, `overlap`, orphan contention, dead PID, reused PID, invalid state, unavailable probe, and combined fresh-log/overlap precedence.
- Add assertions that cron-health/probe ancestors never appear as target evidence and that no broad filesystem command is invoked.
- Integrate `cron_runtime.py inspect` into `cron-health-check.sh` while preserving current log classifications and JSON consumers.
- Verify exit 1 for overlap/excessive/stale-invalid singleton evidence and documented behavior for `RUNNING` and `UNKNOWN`.

### Task 5: Reconcile installed schedule drift safely

- Add explicit `installed_fingerprint` metadata for catalog-owned tasks using the existing all-fields-match vocabulary (`script_basename`, `cwd_contains`, and `owner_repo` where applicable). The transaction will not treat a bare substring as ownership evidence.
- Add transactional fixtures containing the stale same-schedule Hermes command without `--commit`, an old-schedule bridge entry, exact duplicate catalog-attributable entries, an external line that merely contains the same script substring, preserved external entries, and uncataloged entries.
- Prove `cron_apply.py` will replace entries attributable only through the complete explicit fingerprint, report but preserve genuinely external duplicates, and fail closed on unknown ownership. Detection will not imply reconciliation when ownership is unknown.
- Assert 04:25 remains the expected `ace-linux-1` bridge schedule and the rendered command contains `--commit` exactly once.
- Do not mutate live crontab during automated tests. Any later live apply will require a dry-run diff and explicit operator approval.

### Task 6: Document operation and verify all gates

- Update `docs/ops/scheduled-tasks.md` from canonical YAML, including actual per-machine bridge staggering, repository-sync log, runtime metadata, and health states.
- Create `docs/ops/cron-process-response.md` with a bounded snapshot template, exact PID/PPID/PGID/SID/elapsed/wchan/descendant evidence, import-timing exact-command proof, cron-daemon PGID protection, TERM/wait/recheck sequence, and separately approved escalation.
- Make the runbook state that recorded PIDs are never reusable commands and that no automated termination will occur.
- Run focused tests, schedule validation, Bash syntax checks, diff-only legal scan, and targeted security scanner.

---

## TDD Test List

| Test | Expected contract |
|---|---|
| `test_second_runner_reports_contention_without_running_command` | one mutator executes; second invocation emits durable overlap evidence and non-success status |
| `test_signal_is_forwarded_and_lock_is_held_until_child_group_exits` | no live mutator survives lock release; next invocation cannot start early |
| `test_runtime_inspects_child_not_waiting_supervisor` | filesystem wait and PID identity come from the recorded mutating child |
| `test_lock_is_held_until_recorded_pgid_disappears` | direct-child exit alone cannot release the singleton while an in-group descendant remains |
| `test_owner_and_contention_evidence_cannot_overwrite_each_other` | separate atomic files preserve owner, contention, and result evidence |
| `test_completed_success_failure_and_never_started_are_distinct` | absent live PID does not turn a normal completed run into stale-PID failure |
| `test_runtime_state_rejects_pid_start_token_mismatch` | PID reuse classifies as `stale_or_reused_pid` |
| `test_runtime_state_path_is_repo_relative_and_controlled` | absolute, traversal, duplicate, and symlink-abusable paths fail closed |
| `test_runtime_inspection_reads_only_recorded_pid` | no `pgrep -f`, broad `/proc`, or filesystem traversal occurs |
| `test_repository_sync_rendered_log_matches_declared_family` | generated line and `log:` both target dated `logs/repository-sync-*` evidence |
| `test_repository_sync_two_ticks_execute_one_mutator` | singleton enforcement prevents overlap under a hermetic stub |
| `test_cron_health_keeps_log_and_runtime_dimensions_independent` | a fresh log cannot hide overlap/excessive runtime; a live run cannot erase stale log evidence |
| `test_cron_health_runtime_status_precedence_and_exit_codes` | every runtime state maps to documented console, JSON, counters, and exit code |
| `test_cron_health_classifies_configured_filesystem_wait` | bounded stat/wchan evidence produces `filesystem_wait` without a filesystem scan |
| `test_runtime_probe_does_not_match_itself_or_ancestors` | probe/monitor shell never becomes task evidence |
| `test_ace_linux_1_bridge_renders_0425_with_commit` | intentional stagger remains and installed-command drift becomes detectable |
| `test_transaction_reconciles_catalog_duplicates_but_preserves_external` | exact ownership policy governs replacement/preservation/fail-closed behavior |
| `test_catalog_ownership_never_uses_bare_substring_match` | an external command containing the same script text is preserved or blocks, never silently dropped |
| `test_runbook_never_uses_cron_daemon_group_or_automatic_sigkill` | documentation safety invariants remain enforced |

---

## Acceptance Criteria

- [ ] Repository sync cannot execute a second mutating invocation while the first owns its singleton lock.
- [ ] Never-started, active, completed-success, completed-failure, contention, filesystem-wait, excessive-runtime, stale/reused-PID, orphan-contention, and probe-unavailable states produce distinct bounded machine-readable evidence.
- [ ] TERM/INT/HUP is forwarded to the child group and the singleton lock remains held until every mutating child exits; the runner never performs automatic KILL escalation.
- [ ] Runtime health records and inspects the mutating child PID/PGID/start token rather than the waiting supervisor.
- [ ] Cron health reports log and runtime dimensions independently and preserves backward-compatible top-level status semantics.
- [ ] Runtime inspection reads only declared state and a recorded PID identity; it performs no broad FUSE, repo-tree, or process substring scan.
- [ ] The repository-sync declared log family equals the rendered and wrapper-emitted log family.
- [ ] The effective `ace-linux-1` Hermes bridge remains 04:25 and includes `--commit`; source/install drift is covered by tests.
- [ ] Transactional reconciliation detects catalog duplicates/unmanaged drift while preserving external ownership and failing closed on unknown entries.
- [ ] Safe-response documentation requires a fresh bounded snapshot and user approval before TERM and separate approval before escalation.
- [ ] Import-timing response requires exact live command evidence and cannot infer identity from a stale name or unrelated Python process.
- [ ] New code respects 400-lines/file and 50-lines/function limits and contains no hardcoded secrets, absolute workspace paths, `eval`, or shell interpolation.
- [ ] `uv run pytest tests/cron/test_cron_runtime.py tests/cron/test_cron_render.py tests/cron/test_cron_apply.py tests/cron/test_cron_transaction.py -q` passes.
- [ ] `bash scripts/monitoring/tests/test_cron_health_check.sh` passes.
- [ ] `uv run --no-project python scripts/cron/validate-schedule.py` and `uv run pytest scripts/cron/tests/test_validate_schedule.py -q` pass.
- [ ] `bash -n scripts/cron-repository-sync.sh scripts/monitoring/cron-health-check.sh` passes.
- [ ] `bash scripts/legal/legal-sanity-scan.sh --diff-only` and the targeted security scan pass.
- [ ] Code/artifact adversarial cross-review completes before closeout.
- [ ] Implementation and verification evidence is posted as a comment on [#3463](https://github.com/vamseeachanta/workspace-hub/issues/3463).

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE (r1/r2) | r1 hit a temporary-checkout trust gate; r2 from the trusted checkout did not complete before the bounded review window |
| Codex | MAJOR (r1/r2), r3 patched inline | r1 findings are incorporated. r2 requires child rather than supervisor evidence, exact-PGID lock retention, explicit catalog fingerprints instead of substring ownership, durable review paths, and disclosure/fix of the pre-existing renderer-order failure; the inline r3 revision incorporates these findings under the mandated loop-break rule |
| Gemini | UNAVAILABLE (r1) | no non-interactive Gemini credentials are configured on this machine |

**Overall result:** plan-review candidate with minority-provider risk surfaced — two Codex rounds return MAJOR with non-overlapping defects, both revision waves are incorporated, and the workspace r3 loop-break rule forbids another automatic dispatch. Claude and Gemini are unavailable, so there is no provider consensus. The user approval checkpoint will explicitly carry this residual review-diversity risk.

---

## Risks and Open Questions

- **Risk — lock scope:** a lock only protects callers using the scheduled wrapper. `scripts/cron-repository-sync.sh` will be the named enforcement boundary and direct wrapper invocation will remain guarded; the lower-level `scripts/repository_sync` manual tool will remain outside this cron-specific contract and will be documented as unsafe to run concurrently.
- **Risk — state spoofing/symlinks:** runtime state is local machine evidence. Controlled repo-relative paths, ownership checks, atomic replacement, and no-follow behavior will reduce local tampering risk.
- **Risk — abrupt power loss:** stale state will remain possible. PID start-token validation will make it visible without blocking a legitimate new run.
- **Risk — compatibility:** JSON consumers may rely on `status`. The plan will add dimensions without removing existing keys and will test precedence.
- **Risk — legacy installer scope:** #3347 may still require separate repair. #3463 will rely on transactional convergence and will not silently broaden into an installer rewrite.
- **Open question resolved for planning:** `ace-linux-1` bridge 04:25 is intentional, not drift; missing `--commit` is drift.
- **Open question resolved for planning:** initial singleton enforcement will target repository sync, while the runtime contract will remain opt-in and reusable.

---

## Complexity: T3

**T3** — the work will change a mutating cron boundary, introduce a runtime-state security contract, extend health-report compatibility, reconcile rendered schedule evidence, and add an operator safety runbook across multiple test surfaces.
