# Plan for #3470: Scheduler Mutation Safety Contract

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3470
> **Client:** N/A
> **Lane:** lane:codex
> **Review artifacts:** `scripts/review/results/2026-07-11-plan-3470-claude.md` | `scripts/review/results/2026-07-11-plan-3470-codex.md` | `scripts/review/results/2026-07-11-plan-3470-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/cron/cron_apply.py` is the reference Linux transaction: it binds the requested canonical machine to the physical host, locks, snapshots, backs up, compares before write, verifies after write, and compare-and-swaps before rollback.
- `scripts/cron/cron_transaction.py` supplies typed `command_tokens` identity and rejects descriptive `owner_repo`; #3470 will preserve those #3347 guarantees rather than redesign them.
- Nine repo-tracked mutation surfaces remain in scope: four Linux crontab writers, one dual systemd-user/crontab installer, and three Windows Task Scheduler writers, plus the canonical `cron_apply.py` reference.
- The legacy Linux writers use sentinel/marker filtering and whole-crontab writes without a shared transaction contract. The Windows writers own fixed task names but do not expose a common backup/CAS/restore contract.

### Standards

| Standard | Status | Source |
|---|---|---|
| Repository scheduler mutation safety | gap | No dedicated `.claude/rules/` contract or complete mutation-surface registry is present. |
| External engineering standards | N/A | This is repository operational governance, not an engineering calculation. |

### LLM Wiki pages consulted

- No relevant wiki pages apply; scheduler mutation policy belongs in the workspace control plane.

### Documents consulted

- Issue [#3470](https://github.com/vamseeachanta/workspace-hub/issues/3470) defines local-target binding, semantic ownership, rollback CAS, bounded inventory, and audit-first safety.
- `docs/plans/2026-07-11-issue-3347-cron-installer-convergence.md` defines the already-landed reference behavior that this issue will generalize without reopening its implementation.
- `docs/ops/cron-process-response.md` requires explicit ownership evidence before replacement but does not define a typed cross-scheduler mutation contract.
- `docs/ops/scheduled-tasks.md` documents multiple scheduler paths but does not enumerate their execution host, scheduler identity, transaction guarantees, or migration disposition.
- Drive-index query `scheduler cron ownership rollback compare-and-swap` returned unrelated external scheduler files; no relevant drive document will inform implementation. The `master_document_index` adapter was unreachable and three indexes reported stale coverage, so the repo evidence remains authoritative for this operational issue.

### Gaps identified

- No canonical registry enumerates every scheduler mutation surface and its exact local target identity (`current-user cron`, `root cron`, `systemd --user`, or Windows current-user Task Scheduler).
- No enforcement check fails when a new mutation surface bypasses review or when a registry entry omits ownership and transaction guarantees.
- No durable rule states that descriptive metadata and arbitrary substrings cannot authorize scheduler deletion or replacement.
- Existing non-reference writers need separately planned migrations; this issue will produce explicit dispositions and follow-up issues instead of hiding a multi-platform refactor inside an audit ticket.

### Evidence (embedded verification)

**Issue status** (verified 2026-07-11):

- `#3470` — OPEN, `status:needs-plan`, `lane:codex`.

**Fresh-tree proofs** (`0ca3697c9f9b45fe36b0216a62258d3aa8328e5d`):

```text
$ rg -n 'command_tokens|owner_repo|rollback-aborted|refusing local crontab' scripts/cron tests/cron
scripts/cron/cron_transaction.py:42:    "command_tokens",
scripts/cron/cron_apply.py:287:                        "status": "rollback-aborted",
scripts/cron/cron_apply.py:315:            "reason": "refusing local crontab reconciliation ...",
tests/cron/test_cron_transaction.py:145:def test_match_fingerprint_rejects_descriptive_owner_repo_field():
```

```text
$ rg -l 'crontab\s+-|Register-ScheduledTask|Unregister-ScheduledTask|Set-ScheduledTask|systemctl --user (enable|disable)' scripts --glob '*.sh' --glob '*.py' --glob '*.ps1'
scripts/cron/cron_apply.py
scripts/coordination/context/setup_cron.sh
scripts/operations/maintenance/setup_maintenance_cron.sh
scripts/setup/setup-engineering-update-cron.sh
scripts/install/setup-kanban-loader-timer.sh
scripts/windows/setup-scheduler-tasks.ps1
scripts/coordination/context/setup_scheduled_task.ps1
scripts/solver/setup-scheduler.ps1
```

Read-only/status helper matches were excluded after direct inspection; the implementation test will encode the reviewed executable inventory rather than trusting regex alone.

**Reproduction proofs:** N/A — this is an audit/governance issue. The bounded inventory above verifies the live repository premise; no scheduler mutation will be used as reproduction.

Distinct sources consulted: issue body, #3347 plan, current mutation code, cron operations documentation, drive-file index.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-11-issue-3470-scheduler-mutation-safety-contract.md` |
| Human audit report | `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` |
| Machine-readable registry | `config/scheduled-tasks/mutation-surfaces.yaml` |
| Enforcement script | `scripts/enforcement/check-scheduler-mutation-surfaces.py` |
| Enforcement tests | `tests/enforcement/test_scheduler_mutation_surfaces.py` |
| Durable policy | `.claude/rules/scheduler-mutation-safety.md` |
| Operator documentation | `docs/ops/scheduled-tasks.md` |
| Review artifacts | `scripts/review/results/2026-07-11-plan-3470-*.md` |

---

## Deliverable

A fail-closed registry, enforcement check, policy, and HTML audit report will enumerate every repo-tracked scheduler mutation surface, define its local target and ownership authority, and force unsafe existing surfaces into explicit follow-up dispositions.

---

## Pseudocode

```text
function discover_mutation_surfaces(repo):
    scan only tracked scheduler-capable source files with reviewed mutation signatures
    exclude read-only helpers through exact reviewed exclusions
    return normalized repo-relative paths and detected scheduler primitives

function validate_registry(registry, discovered):
    reject duplicate, missing, or non-existent paths
    require target_kind, execution_host_binding, scheduler_identity, ownership_authority
    require transaction fields: lock, baseline, backup, pre-write CAS, post-verify, rollback CAS
    reject descriptive owner/note fields inside ownership_authority
    require status reference | compliant | migration-required and a traced disposition
    fail when discovered paths and registered paths differ

function render_audit(registry):
    group surfaces by scheduler identity and compliance status
    show exact gaps and follow-up issue links without machine-private data
    state that registry inclusion is not approval to mutate live scheduler state
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `config/scheduled-tasks/mutation-surfaces.yaml` | Record the exact reviewed mutation inventory, local target identity, guarantees, and disposition. |
| Create | `scripts/enforcement/check-scheduler-mutation-surfaces.py` | Fail closed on unregistered mutators or invalid safety metadata. |
| Create | `tests/enforcement/test_scheduler_mutation_surfaces.py` | Drive implementation with discovery, schema, adversarial near-match, and drift tests. |
| Create | `.claude/rules/scheduler-mutation-safety.md` | Make semantic ownership, local-target binding, and transaction requirements durable. |
| Create | `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` | Publish the human-readable audit and migration matrix. |
| Modify | `docs/ops/scheduled-tasks.md` | Link the registry/check and explain scheduler identities and audit-only usage. |
| Modify | `docs/plans/README.md` | Index this plan and its lifecycle state. |

No production scheduler writer will be behaviorally modified in this issue. Each `migration-required` surface will receive a linked follow-up issue with its own plan, TDD, review, and approval gate.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_current_mutation_inventory_is_registered` | Every reviewed executable mutation surface is represented exactly once. | Current tracked source tree | Registry and discovery sets are equal. |
| `test_new_unregistered_crontab_writer_fails` | A new whole-crontab writer cannot bypass review. | Temporary tracked-style shell fixture | Non-zero with the unregistered path. |
| `test_new_unregistered_windows_writer_fails` | Register/Set/Unregister Task Scheduler calls require registration. | Temporary PowerShell fixture | Non-zero with the unregistered path. |
| `test_read_only_crontab_helpers_are_not_mutators` | Status/audit helpers do not create false positives. | Reviewed read-only fixtures | No discovered mutation surface. |
| `test_registry_requires_exact_local_target_identity` | Execution host and scheduler identity cannot be inferred from `--machine` or workspace path. | Entry missing required target fields | Schema failure. |
| `test_descriptive_metadata_cannot_authorize_ownership` | `owner`, `note`, and substring-only description fields cannot be destructive authority. | Invalid ownership block | Schema failure. |
| `test_transaction_contract_is_complete` | Every surface declares all lock/snapshot/backup/CAS/verify/rollback fields. | Entry missing rollback CAS | Schema failure. |
| `test_migration_required_has_traced_follow_up` | Grandfathered gaps cannot become permanent anonymous exceptions. | Migration entry without issue URL | Schema failure. |
| `test_reference_cron_apply_contract_matches_source` | #3347 guarantees remain represented and regression-protected. | `scripts/cron/cron_apply.py` | Reference entry validates. |
| `test_cli_reports_machine_readable_failures` | CI and operators receive deterministic diagnostics. | Invalid registry fixture | Stable JSON/text error and non-zero exit. |

---

## Acceptance Criteria

- [ ] Tests will be written first and will fail before the registry/check exists.
- [ ] The registry will enumerate the fresh tracked mutation set with exact scheduler identities and no broad filesystem scan.
- [ ] The enforcement check will fail on unregistered mutation primitives and invalid/incomplete safety contracts.
- [ ] The reference `cron_apply.py` entry will reflect physical-host binding, semantic token identity, pre-write CAS, post-verify, and rollback CAS already delivered by #3347.
- [ ] Every non-compliant surface will have `migration-required` status plus a linked GitHub follow-up issue; registry inclusion alone will not waive the gap.
- [ ] The durable rule will forbid descriptive metadata or arbitrary substring matches from authorizing deletion/replacement.
- [ ] The HTML report will show the complete matrix, evidence timestamp/commit, limitations, and follow-up links.
- [ ] `uv run pytest tests/enforcement/test_scheduler_mutation_surfaces.py -v` will pass.
- [ ] Existing focused cron and setup tests will pass.
- [ ] `bash scripts/legal/legal-sanity-scan.sh --diff-only` will pass.
- [ ] Code-stage adversarial review will complete before merge.
- [ ] No live crontab, systemd unit, Windows scheduled task, or process will be mutated during implementation or verification.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Adversarial review not yet run. |
| Codex | PENDING | Adversarial review not yet run. |
| Gemini | PENDING | Adversarial review not yet run. |

**Overall result:** PENDING

---

## Risks and Open Questions

- **Inventory evasion:** Regex discovery alone can miss indirection; the check will combine reviewed mutation primitives with an explicit inventory and adversarial fixtures.
- **Grandfathering risk:** `migration-required` could become a permanent waiver; each such entry will require a linked open issue and the report will keep gaps visible.
- **Cross-platform verification:** Linux CI cannot prove Windows runtime rollback behavior; this issue will register that gap and route behavioral changes to Windows-capable follow-ups.
- **Self-blocking enforcement:** Tests, plans, and documentation may quote mutation signatures. Discovery will be restricted to executable source paths and reviewed primitives so its own forensic artifacts do not fail the check.
- **Scope boundary:** This issue will enforce inventory/governance only. It will not silently refactor nine mutation paths or authorize live scheduler changes.

---

## Complexity: T3

**T3** — the contract spans Linux cron, systemd user timers, Windows Task Scheduler, schema enforcement, CI tests, operator documentation, and multiple follow-up migration boundaries.
