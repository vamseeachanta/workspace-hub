# Plan for #3463: Cron singleton enforcement and bounded runtime health

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3463
> **Client:** N/A
> **Lane:** lane:claude
> **Execution mode:** parallel-readonly for planning/review; single-lane for implementation because runtime state, schedule metadata, and health classification share one contract
> **Review artifacts:** `scripts/review/results/2026-07-11-plan-3463-claude.md` | `scripts/review/results/2026-07-11-plan-3463-codex.md` | `scripts/review/results/2026-07-11-plan-3463-gemini.md`
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
| Review artifacts | `scripts/review/results/2026-07-11-plan-3463-{claude,codex,gemini}.md` |

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
  state_file: .claude/state/cron-runtime/repository-sync.json
```

`validate-schedule.py` will reject non-boolean `singleton`, non-positive or unreasonably large `max_seconds`, absolute/traversing `state_file` paths, duplicate state paths, and runtime metadata on non-cron tasks. The exact upper bound will be fixed in the failing validator tests before implementation.

### Runtime runner

```text
run(task_id, command, schedule):
    load and validate the task's runtime contract from canonical YAML
    open controlled lock path without following an attacker-controlled symlink
    attempt nonblocking exclusive flock
    if contention:
        atomically write bounded contention evidence
        exit with a documented non-success contention code
    record pid, pgid, sid, /proc start token, and UTC start time atomically
    execute the requested command without eval or shell interpolation
    record exit result atomically
    release lock on normal, error, or signal path
```

### Runtime inspection

```text
inspect(runtime_record, now):
    validate schema and task id
    read only the recorded PID's /proc identity
    if PID is absent: return stale_pid
    if start token differs: return stale_or_reused_pid
    if contention evidence is newer than the run: return overlap
    if elapsed > max_seconds: return excessive_runtime
    otherwise: return active_within_budget
```

### Cron-health composition

```text
for each machine-applicable task:
    calculate existing log_status independently
    if runtime metadata exists:
        calculate runtime_status through cron_runtime.py inspection
    combine with explicit precedence:
        overlap or excessive_runtime or invalid/stale identity => problem / exit 1
        active_within_budget => visible RUNNING dimension; do not erase log evidence
        unavailable runtime probe => UNKNOWN, visible and fail-closed for singleton tasks
    emit both log_status and runtime_status in JSON
```

The existing top-level `status` field will remain for compatibility and will use documented precedence; new `log_status`, `runtime_status`, `active_pid`, `pgid`, `sid`, `elapsed_seconds`, and `evidence_timestamp` fields will provide non-lossy detail. No environment variables or full command lines will enter the JSON report.

---

## Implementation Tasks and TDD Order

### Task 1: Lock the runtime contract with RED tests

- Add `tests/cron/test_cron_runtime.py` fixtures using temporary directories and short-lived child processes.
- Add failing tests for one successful lock owner, second-run contention, lock release after success/error/signal, stale PID, PID start-token mismatch, controlled state paths, atomic state replacement, and missing `flock`/unsupported `/proc` behavior.
- Extend `scripts/cron/tests/test_validate_schedule.py` with failing schema/security tests before adding YAML runtime fields.
- Run the focused tests and retain the expected RED output in the implementation issue comment.

### Task 2: Implement the minimal runtime runner

- Create `scripts/cron/cron_runtime.py` with separate pure parsing/inspection functions and a CLI execution boundary.
- Keep the file below 400 lines and every function below 50 lines.
- Use argv-preserving subprocess execution; do not use `eval`, `shell=True`, or command-string interpolation.
- Make state and contention writes atomic through same-directory temporary files and rename.
- Re-run Task 1 tests to GREEN, then run `bash -n scripts/cron-repository-sync.sh`.

### Task 3: Enforce repository-sync singleton and correct its log contract

- First extend renderer and validation tests so the repository-sync rendered redirection family equals its declared `log:` family and contains the runtime runner invocation.
- Update the repository-sync catalog command and wrapper integration only after those tests fail.
- Preserve the wrapper's dated `logs/repository-sync-*.log` as the canonical execution log; remove reliance on the machine-global `$LOG` for this task.
- Add a hermetic two-invocation test proving only one mutation stub executes and contention produces durable evidence.

### Task 4: Add independent runtime health to cron-health

- Extend the canonical Bash behavioral suite first with fixtures for `active_within_budget`, `excessive_runtime`, `overlap`, dead PID, reused PID, invalid state, unavailable probe, and combined fresh-log/overlap precedence.
- Add assertions that cron-health/probe ancestors never appear as target evidence and that no broad filesystem command is invoked.
- Integrate `cron_runtime.py inspect` into `cron-health-check.sh` while preserving current log classifications and JSON consumers.
- Verify exit 1 for overlap/excessive/stale-invalid singleton evidence and documented behavior for `RUNNING` and `UNKNOWN`.

### Task 5: Reconcile installed schedule drift safely

- Add transactional fixtures containing the stale same-schedule Hermes command without `--commit`, an old-schedule bridge entry, exact duplicate unmanaged entries, preserved external entries, and uncataloged entries.
- Prove `cron_apply.py` will replace catalog-owned stale variants, preserve genuinely external entries, and fail closed on unknown ownership.
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
| `test_lock_releases_after_success_error_and_signal` | no orphan lock prevents the next valid run |
| `test_runtime_state_rejects_pid_start_token_mismatch` | PID reuse classifies as `stale_or_reused_pid` |
| `test_runtime_state_path_is_repo_relative_and_controlled` | absolute, traversal, duplicate, and symlink-abusable paths fail closed |
| `test_runtime_inspection_reads_only_recorded_pid` | no `pgrep -f`, broad `/proc`, or filesystem traversal occurs |
| `test_repository_sync_rendered_log_matches_declared_family` | generated line and `log:` both target dated `logs/repository-sync-*` evidence |
| `test_repository_sync_two_ticks_execute_one_mutator` | singleton enforcement prevents overlap under a hermetic stub |
| `test_cron_health_keeps_log_and_runtime_dimensions_independent` | a fresh log cannot hide overlap/excessive runtime; a live run cannot erase stale log evidence |
| `test_cron_health_runtime_status_precedence_and_exit_codes` | every runtime state maps to documented console, JSON, counters, and exit code |
| `test_runtime_probe_does_not_match_itself_or_ancestors` | probe/monitor shell never becomes task evidence |
| `test_ace_linux_1_bridge_renders_0425_with_commit` | intentional stagger remains and installed-command drift becomes detectable |
| `test_transaction_reconciles_catalog_duplicates_but_preserves_external` | exact ownership policy governs replacement/preservation/fail-closed behavior |
| `test_runbook_never_uses_cron_daemon_group_or_automatic_sigkill` | documentation safety invariants remain enforced |

---

## Acceptance Criteria

- [ ] Repository sync cannot execute a second mutating invocation while the first owns its singleton lock.
- [ ] Contention, excessive runtime, stale/reused PID identity, and probe unavailability produce durable, bounded, machine-readable evidence.
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
| Claude | pending | pending first adversarial wave |
| Codex | pending | pending first adversarial wave |
| Gemini | pending | pending first adversarial wave |

**Overall result:** pending — the plan will remain `draft` until all available provider reviews contain no MAJOR findings.

---

## Risks and Open Questions

- **Risk — lock scope:** a lock only protects callers using the runner. Tests and documentation will make direct wrapper invocation behavior explicit, and repository sync will acquire the singleton at the closest mutation boundary.
- **Risk — state spoofing/symlinks:** runtime state is local machine evidence. Controlled repo-relative paths, ownership checks, atomic replacement, and no-follow behavior will reduce local tampering risk.
- **Risk — abrupt power loss:** stale state will remain possible. PID start-token validation will make it visible without blocking a legitimate new run.
- **Risk — compatibility:** JSON consumers may rely on `status`. The plan will add dimensions without removing existing keys and will test precedence.
- **Risk — legacy installer scope:** #3347 may still require separate repair. #3463 will rely on transactional convergence and will not silently broaden into an installer rewrite.
- **Open question resolved for planning:** `ace-linux-1` bridge 04:25 is intentional, not drift; missing `--commit` is drift.
- **Open question resolved for planning:** initial singleton enforcement will target repository sync, while the runtime contract will remain opt-in and reusable.

---

## Complexity: T3

**T3** — the work will change a mutating cron boundary, introduce a runtime-state security contract, extend health-report compatibility, reconcile rendered schedule evidence, and add an operator safety runbook across multiple test surfaces.
