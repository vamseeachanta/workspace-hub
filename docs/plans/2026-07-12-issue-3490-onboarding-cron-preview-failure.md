# Plan for #3490: Surface cron preview failure during new-machine dry-run

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-07-12
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3490
> **Client:** N/A
> **Lane:** lane:codex
> **Review artifacts:** `scripts/review/results/2026-07-12-plan-3490-claude.md` | `scripts/review/results/2026-07-12-plan-3490-codex.md`

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/setup/new-machine-setup.sh:190-202` delegates cron onboarding in four branches. The Linux dry-run branch passes `--dry-run` but appends `|| true`; default Linux already propagates the callee status, and the Windows branch intentionally remains best-effort.
- `scripts/cron/setup-cron.sh:45-70` already propagates its terminal `cron_apply.py` status through `exec`. Dry-run selects `--json` without `--apply`, so the defect is confined to the outer onboarding wrapper.
- `scripts/enforcement/scheduler_mutation_wrapper_attestations.py:23-26,95-107` pins the wrapper bytes and currently requires the swallowing dry-run source shape.
- `scripts/enforcement/scheduler_mutation_delegation.py:14-31` and `config/scheduled-tasks/mutation-surfaces.yaml:219-227` currently declare `dry-run-preview` and Windows skip as `swallow-3490`.
- No direct executable test for `new-machine-setup.sh` exists. Enforcement tests validate source shape but do not prove the wrapper's process exit/result behavior.

### Standards

| Contract | Status | Source |
|---|---|---|
| Transitive scheduler modes must declare exact arguments and exit behavior | Enforced; dry-run debt is explicit | `.claude/rules/scheduler-mutation-safety.md`, `config/scheduled-tasks/mutation-surfaces.yaml` |
| Issue lifecycle and TDD | Required | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| Completeness before closure | Required after approval | `.claude/rules/completeness-before-close.md` |

No engineering standard or domain wiki applies to this infrastructure-only wrapper change.

### Documents consulted

- [Issue #3490](https://github.com/vamseeachanta/workspace-hub/issues/3490) limits the change to dry-run result/exit observability while preserving default Linux and Windows behavior.
- `docs/plans/2026-07-11-issue-3475-cron-semantic-ownership.md` requires the `new-machine-setup.sh` dry-run mode to remain explicit and promotes this failure-swallowing debt to #3490.
- `docs/plans/2026-07-11-issue-3470-scheduler-mutation-safety-contract.md` establishes mode-specific transitive delegation, source attestations, staged provenance, and deterministic HTML parity.
- Drive-index query `cron onboarding dry-run preview` returned only unrelated CAD filename collisions. No relevant operational drive file was found. The `master_document_index` coverage gap reported reason `unreachable`; `cad_readability` was 16 days stale and `master_document_index` was 86 days stale, so repo evidence will remain authoritative.

### Parallel-work check

- Bounded `pgrep`, worktree, and remote-branch checks found no competing #3490 branch or process; the only process match was the probe itself.
- Planning will use `parallel-readonly`; implementation will use `single-lane` because wrapper source, pinned source attestation, registry contract, and generated report form one atomic correctness boundary.

### Gaps identified

- No executable wrapper contract proves that a failed cron preview makes onboarding dry-run nonzero and prevents the later success banner.
- The registry, source attestation, tests, operations documentation, and generated scheduler report currently encode the known debt rather than the resolved contract.
- Windows best-effort behavior is coupled to the #3490 debt label even though the issue will not change that runtime branch.

### Evidence and reproduction proofs

Verified 2026-07-12T09:36Z:

```text
$ gh issue view 3490 --json state,labels,title
OPEN; status:needs-plan; lane:codex

$ git ls-remote --heads origin '*3490*' '*cron*preview*'
<empty>
```

The runtime defect was reproduced with a temporary `HOME` and an exported fake `uv` that returned 42 before `setup-cron.sh` could read or write crontab state. No live scheduler command was invoked.

```text
$ HOME=<temporary> bash -c 'uv(){ echo FAKE_UV_FAILURE >&2; return 42; }; export -f uv; bash scripts/setup/new-machine-setup.sh --dry-run; echo ONBOARDING_RC=$?'
=== 6. Crontab ===
  [dry-run] bash scripts/cron/setup-cron.sh --dry-run
FAKE_UV_FAILURE rc=42 args=run --no-project python .../cron_render.py ...
...
=== Setup complete! ===
ONBOARDING_RC=0
```

- Reproduced at: 2026-07-12T09:38Z
- Failure mode observed matches issue claim: **YES** — preview failure is converted to success and later onboarding output continues.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-12-issue-3490-onboarding-cron-preview-failure.md` |
| Human plan | `docs/reports/2026-07-12-issue-3490-onboarding-cron-preview-failure-plan.html` |
| Wrapper | `scripts/setup/new-machine-setup.sh` |
| Direct wrapper tests | `tests/setup/test_new_machine_setup.py` |
| Registry and source attestations | `config/scheduled-tasks/mutation-surfaces.yaml`, `scripts/enforcement/scheduler_mutation_delegation.py`, `scripts/enforcement/scheduler_mutation_wrapper_attestations.py` |
| Enforcement tests | `tests/enforcement/test_scheduler_mutation_task3.py` |
| Generated scheduler report | `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` |
| Plan reviews | `scripts/review/results/2026-07-12-plan-3490-*.md` |
| Completeness report | `docs/reports/<completion-date>-3490-completeness.html` |

---

## Deliverable

`new-machine-setup.sh --dry-run` will return the cron preview's nonzero status and stop before later onboarding steps, while default Linux apply and Windows best-effort skip behavior will remain unchanged and registry-enforced.

---

## Pseudocode

### Dry-run exit contract

```text
if no_cron:
    report skip and continue
else if dry_run:
    print exact preview command
    invoke setup-cron.sh --dry-run
    if preview fails:
        emit concise cron-preview failure context to stderr
        exit with the callee's exact nonzero status
else if windows:
    print Task Scheduler instructions
    retain existing best-effort setup-cron invocation
else:
    invoke setup-cron.sh and propagate its status
```

The implementation will not aggregate a failed preview into a later zero exit. It will preserve the callee's exact status rather than replacing it with a generic code. The Windows source branch will retain `|| true`; only its registry label will be decoupled from #3490 and described as a platform-specific best-effort skip.

### Hermetic executable test

```text
create temporary repo-shaped fixture
copy new-machine-setup.sh into fixture
write stub scripts/cron/setup-cron.sh that records argv and exits 42
provide temporary HOME and fake uname/hostname/crontab commands
run fixture wrapper --dry-run
assert callee argv is exactly --dry-run
assert wrapper exit is 42
assert failure context is visible
assert Step 7 and Setup complete are absent
assert fake crontab sentinel was never called
```

### Governance transition

```text
change dry-run-preview exit from swallow-3490 to propagate
retain Windows source behavior and rename its exit policy to best-effort-skip
update the pinned staged-blob source attestation
mutation-test removal of --dry-run, reintroduced swallowing, status replacement, and Windows/default drift
regenerate scheduler HTML and require byte parity
remove resolved #3490 debt wording from operations documentation
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/setup/new-machine-setup.sh` | Propagate exact dry-run preview failure and stop later success output |
| Create | `tests/setup/test_new_machine_setup.py` | Hermetic executable wrapper contract with no live scheduler access |
| Modify | `config/scheduled-tasks/mutation-surfaces.yaml` | Record dry-run propagation and decouple unchanged Windows best-effort skip from #3490 |
| Modify | `scripts/enforcement/scheduler_mutation_delegation.py` | Require the revised exact mode contract |
| Modify | `scripts/enforcement/scheduler_mutation_wrapper_attestations.py` | Require reachable propagation source shape and refresh the staged-blob pin |
| Modify | `tests/enforcement/test_scheduler_mutation_task3.py` | Add registry/source mutation regressions and remove active #3490 debt assertions |
| Update | `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` | Refresh deterministic mode rendering |
| Update | `docs/ops/scheduled-tasks.md` | Document resolved dry-run propagation and retained Windows boundary |
| Update | `docs/plans/README.md` | Index this plan and reconcile parent #3475 completion state |

`scripts/cron/setup-cron.sh` and `cron_apply.py` will remain verification surfaces, not implementation edits.

---

## TDD Test List

| Test name | What it will verify | Expected result |
|---|---|---|
| `test_dry_run_propagates_cron_preview_failure` | Stub preview exits 42 | Wrapper exits 42 |
| `test_dry_run_stops_after_failed_cron_preview` | No later onboarding output follows failure | No Step 7 or completion banner |
| `test_dry_run_invokes_exact_preview_arguments` | Delegation preserves non-mutating mode | Stub records exactly `--dry-run` |
| `test_dry_run_never_invokes_crontab_sentinel` | Fixture cannot touch live scheduler state | Sentinel call count remains zero |
| `test_dry_run_success_continues_to_completion` | Successful preview retains normal dry-run flow | Exit 0 and completion banner |
| `test_no_cron_dry_run_skips_preview` | `--no-cron --dry-run` keeps explicit skip | Stub is not invoked; exit 0 |
| `test_default_linux_source_still_propagates` | Default destructive branch is not weakened | No `|| true` on default Linux call |
| `test_windows_source_remains_best_effort` | Out-of-scope Windows behavior is unchanged | Windows branch retains `|| true` |
| `test_registry_declares_dry_run_propagation` | Governance matches executable contract | `exit: propagate` for dry-run preview |
| `test_attestation_rejects_reintroduced_swallow` | Source-shape checker cannot be bypassed | `|| true` mutation fails attestation |
| `test_attestation_rejects_generic_status_replacement` | Exact callee status remains observable | `exit 1`/masked status mutation fails |
| `test_scheduler_html_has_no_active_3490_debt_link` | Generated report reflects resolution | No `swallow-3490` or active #3490 link |

---

## Acceptance Criteria

- [ ] Hermetic RED proves the current wrapper exits 0 after a fake preview exits 42.
- [ ] GREEN returns the exact fake status 42 and stops before Step 7/completion output.
- [ ] Successful dry-run, `--no-cron --dry-run`, default Linux apply source shape, and Windows best-effort source shape remain covered.
- [ ] No test invokes live `crontab`, process signaling, or scheduler mutation.
- [ ] Registry, source attestation, operations documentation, and deterministic scheduler HTML describe the same mode contract.
- [ ] `uv run pytest -q tests/setup/test_new_machine_setup.py` passes.
- [ ] Relevant scheduler enforcement tests pass, including staged-blob mutation cases.
- [ ] `uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py --json` reports `status=ok`.
- [ ] Scheduler HTML `--check-html` parity passes.
- [ ] Ruff, legal diff scan, file/function size, and required PR checks pass.
- [ ] T2 adversarial plan and code review complete with no MAJOR findings.
- [ ] Completeness score/report is persisted and owner-applied `status:completeness-verified` passes before closure.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Review not yet run |
| Codex | PENDING | Review not yet run |

**Overall result:** PENDING — implementation remains blocked pending adversarial review and user approval.

---

## Risks and Open Questions

- **Risk:** Any wrapper edit invalidates the staged-blob SHA pin; implementation will refresh the pin only after executable behavior and source-shape tests are green.
- **Risk:** A broad removal of `|| true` would change Windows behavior; tests will bind the dry-run and Windows branches separately.
- **Risk:** A test using the real callee could read the live crontab; all executable tests will use a repo-shaped fixture and scheduler sentinel.
- **Risk:** Replacing the callee status with a generic exit code would weaken diagnostics; the contract will require exact propagation.
- **Open question:** None. The issue already selects surfaced nonzero failure, and exact propagation is the narrowest compatible contract.

---

## Complexity: T2

**T2** — the runtime edit is small, but executable behavior, pinned source attestation, registry schema, deterministic report parity, and multiple preservation boundaries must change atomically.
