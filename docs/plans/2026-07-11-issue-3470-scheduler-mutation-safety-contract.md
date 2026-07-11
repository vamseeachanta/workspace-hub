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
- Eight direct primitive owners remain in scope: `cron_apply.py`, three legacy Linux crontab writers, the dual systemd-user/crontab kanban installer, and three Windows Task Scheduler writers.
- Three transitive mutation entrypoints will be modeled separately: `setup-cron.sh`, `new-machine-setup.sh`, and `harness-update.sh`. Their registry rows will name the direct writer they invoke; wrapper identity checks will not be confused with scheduler IO ownership.
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

- No canonical registry enumerates the eight direct primitive owners, three reviewed transitive entrypoints, their call edges, and exact local target identities (`current-user cron`, `root cron`, `systemd --user`, or Windows current-user Task Scheduler).
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

This is the exact eight-path direct-owner set. Bounded call-edge inspection adds exactly three transitive entrypoints: `scripts/cron/setup-cron.sh` → `cron_apply.py`, `scripts/setup/new-machine-setup.sh` → `setup-cron.sh`, and `scripts/cron/harness-update.sh` → `setup-cron.sh`. Read-only/status helper matches are excluded after direct inspection; implementation tests will encode both reviewed sets rather than trusting regex alone.

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
| Automatic gate | `.github/workflows/enforcement-gate.yml` |
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
    obtain NUL-delimited tracked paths from git ls-files -z
    pass normalized (path, bytes) records to a pure scanner
    discover direct primitives and reviewed call edges separately
    ignore a matching forensic line only when it carries the exact per-line sentinel
    return normalized direct-owner paths, transitive entrypoints, edges, and primitives

function validate_registry(registry, discovered):
    reject duplicate, missing, or non-existent paths
    require target_kind, execution_host_binding, scheduler_identity, ownership_authority
    require typed enums and booleans for target, authority, and transaction fields
    reject unknown keys, empty evidence, and descriptive owner/note authority
    for reference/compliant, verify each claimed guarantee against named source attestations
    for migration-required, allow false or unknown guarantees but require a distinct disposition issue
    validate offline issue coordinates as this repository + numeric issue + non-self reference
    fail when discovered paths and registered paths differ

function render_audit(registry, output, evidence_commit):
    call the same registry validator before rendering
    group surfaces by scheduler identity and compliance status
    deterministically show every row once with exact gaps and follow-up links
    state that registry inclusion is not approval to mutate live scheduler state

command check-scheduler-mutation-surfaces.py:
    default: validate tracked source + registry, emit machine-readable diagnostics
    --render-html PATH: validate, then render deterministic registry-derived HTML
    --check-html PATH: compare regenerated bytes after normalizing the explicit commit field
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
| Modify | `.github/workflows/enforcement-gate.yml` | Invoke the checker automatically and verify the committed HTML is current. |
| Modify | `docs/ops/scheduled-tasks.md` | Link the registry/check and explain scheduler identities and audit-only usage. |
| Modify | `docs/plans/README.md` | Index this plan and its lifecycle state. |

No production scheduler writer will be behaviorally modified in this issue. Before the registry lands, implementation will create one or more non-self follow-up issues that cover every `migration-required` surface; if issue creation partially fails, the registry/commit will not proceed. The offline checker will validate repository, numeric issue, non-self reference, and declared reuse policy without network access. HTML generation may enrich live state during an explicit operator run, but CI will not depend on GitHub availability.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_current_mutation_inventory_is_registered` | Every reviewed executable mutation surface is represented exactly once. | Current tracked source tree | Registry and discovery sets are equal. |
| `test_new_unregistered_crontab_writer_fails` | A new whole-crontab writer cannot bypass review. | Temporary tracked-style shell fixture | Non-zero with the unregistered path. |
| `test_new_unregistered_windows_writer_fails` | Register/Set/Unregister Task Scheduler calls require registration. | Temporary PowerShell fixture | Non-zero with the unregistered path. |
| `test_transitive_wrapper_and_call_edge_are_registered` | A wrapper that invokes an approved direct writer remains a mutation entrypoint. | Wrapper fixture and current three-edge inventory | Missing wrapper/edge fails. |
| `test_read_only_crontab_helpers_are_not_mutators` | Status/audit helpers do not create false positives. | Reviewed read-only fixtures | No discovered mutation surface. |
| `test_git_adapter_is_nul_safe_and_pure_scanner_is_hermetic` | Discovery handles odd tracked names and index-sourced content. | NUL-delimited path/content fixtures | Deterministic records with no working-tree globbing. |
| `test_registry_requires_exact_local_target_identity` | Execution host and scheduler identity cannot be inferred from `--machine` or workspace path. | Entry missing required target fields | Schema failure. |
| `test_descriptive_metadata_cannot_authorize_ownership` | `owner`, `note`, and substring-only description fields cannot be destructive authority. | Invalid ownership block | Schema failure. |
| `test_transaction_contract_is_complete` | Every surface declares all lock/snapshot/backup/CAS/verify/rollback fields. | Entry missing rollback CAS | Schema failure. |
| `test_compliant_claims_require_source_attestation` | Registry booleans cannot certify behavior without matching source evidence. | Truthy guarantee with absent/mismatched evidence | Schema/attestation failure. |
| `test_migration_required_has_traced_follow_up` | Grandfathered gaps cannot become permanent anonymous exceptions. | Migration entry without issue URL | Schema failure. |
| `test_follow_up_coordinates_reject_self_wrong_repo_and_duplicates` | Offline issue references cannot point to #3470, another repo, or violate reuse policy. | Adversarial disposition fixtures | Schema failure. |
| `test_reference_cron_apply_contract_matches_source` | #3347 host binding and CAS guarantees remain represented; semantic identity is claimed only for fingerprints using `command_tokens`. | `scripts/cron/cron_apply.py`, `cron_transaction.py`, catalog | Source attestations validate precisely. |
| `test_checker_does_not_block_its_forensic_artifacts` | Pattern literals in the checker/tests require narrow per-line sentinels and do not self-register. | Real checker and test files | Neither appears as a mutator; unsentinelled executable fixture fails. |
| `test_html_is_deterministic_and_registry_complete` | Every registry row/status/link appears once and regeneration is stable. | Registry + fixed evidence commit | Byte-stable HTML and exact row parity. |
| `test_enforcement_workflow_invokes_checker` | The new check cannot remain an unused script. | `.github/workflows/enforcement-gate.yml` | Exact checker and `--check-html` invocation present. |
| `test_cli_reports_machine_readable_failures` | CI and operators receive deterministic diagnostics. | Invalid registry fixture | Stable JSON/text error and non-zero exit. |

---

## Acceptance Criteria

- [ ] Tests will be written first and will fail before the registry/check exists.
- [ ] The registry will enumerate exactly eight direct primitive owners plus three transitive entrypoints/call edges with exact scheduler identities and no broad filesystem scan.
- [ ] The enforcement check will fail on unregistered mutation primitives and invalid/incomplete safety contracts.
- [ ] Reference/compliant guarantees will require source attestations; `cron_apply.py` will claim physical-host binding, pre-write CAS, post-verify, and rollback CAS, while semantic identity will be claimed only for catalog fingerprints actually using `command_tokens`.
- [ ] Every non-compliant surface will have `migration-required` status plus a linked GitHub follow-up issue; registry inclusion alone will not waive the gap.
- [ ] The durable rule will forbid descriptive metadata or arbitrary substring matches from authorizing deletion/replacement.
- [ ] The HTML report will show the complete matrix, evidence timestamp/commit, limitations, and follow-up links.
- [ ] The enforcement workflow will invoke the checker and deterministic HTML parity check on pull requests.
- [ ] `uv run pytest tests/enforcement/test_scheduler_mutation_surfaces.py -v` will pass.
- [ ] Existing focused cron and setup tests will pass.
- [ ] `bash scripts/legal/legal-sanity-scan.sh --diff-only` will pass.
- [ ] Code-stage adversarial review will complete before merge.
- [ ] No live crontab, systemd unit, Windows scheduled task, or process will be mutated during implementation or verification.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE | Fresh-clone trust dialog blocked non-interactive review. |
| Codex | UNAVAILABLE | CLI stdin regression produced no verdict. |
| Gemini | UNAVAILABLE | Non-interactive authentication was not configured. |
| Fallback governance audit r1 | MAJOR → patched | Required source attestations, correct identity claims, direct/transitive inventory, automatic gate wiring, hermetic discovery, and explicit issue-creation boundary. |
| Fallback schedule audit r1 | MAJOR → patched | Required exact inventory, wrapper detection, self-block regression, deterministic HTML parity, offline follow-up validation, and typed schema. |

**Overall result:** FAIL — fallback r1 reviews returned MAJOR; revisions above require fresh re-review.

Revisions made based on r1:

- The plan separates eight direct primitive owners from three transitive entrypoints and models call edges.
- Typed source-attested guarantees replace self-asserted compliance booleans.
- NUL-safe tracked-file discovery, narrow forensic sentinels, real-file self-block tests, and automatic workflow wiring are explicit.
- HTML becomes deterministic checker output with parity verification.
- Follow-up issue creation and offline validation boundaries are explicit.

---

## Risks and Open Questions

- **Inventory evasion:** Regex discovery alone can miss indirection; the check will combine direct primitives, reviewed call edges, exact inventories, and adversarial wrapper fixtures.
- **Grandfathering risk:** `migration-required` could become a permanent waiver; each such entry will require a linked open issue and the report will keep gaps visible.
- **Cross-platform verification:** Linux CI cannot prove Windows runtime rollback behavior; this issue will register that gap and route behavioral changes to Windows-capable follow-ups.
- **Self-blocking enforcement:** Executable checker/test files may quote mutation signatures. Only exact per-line forensic sentinels will suppress those lines; a real-file regression will prohibit blanket directory exemptions.
- **Scope boundary:** This issue will enforce inventory/governance only. It will not silently refactor the eight direct owners or three transitive entrypoints, and it will not authorize live scheduler changes.

---

## Complexity: T3

**T3** — the contract spans Linux cron, systemd user timers, Windows Task Scheduler, schema enforcement, CI tests, operator documentation, and multiple follow-up migration boundaries.
