# Plan for #3470: Scheduler Mutation Safety Contract

> **Status:** plan-review
> **Complexity:** T3
> **Date:** 2026-07-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3470
> **Client:** N/A
> **Lane:** lane:codex
> **Review artifacts:** `scripts/review/results/2026-07-11-plan-3470-claude.md` | `scripts/review/results/2026-07-11-plan-3470-codex.md` | `scripts/review/results/2026-07-11-plan-3470-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/cron/cron_apply.py` is the reference Linux transaction for host binding and CAS: it locks, snapshots, backs up, compares before write, verifies preservation after write, and compare-and-swaps before rollback. It does not prove exact intended-state equality after write, and its mixed substring/token ownership branches will remain explicitly non-compliant.
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
| Human plan view | `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety-plan.html` |
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
    read index bytes with git cat-file --batch-command -Z, never dirty working-tree bytes
    fail closed with a minimum-Git diagnostic when -Z is unavailable
    pass normalized (path, index_bytes) records to a pure scanner
    discover direct primitives and reviewed call edges separately
    honor the forensic sentinel only in the exact checker/test allowlist paths
    reject a sentinel on every production mutation path even when the line is marked
    return normalized direct-owner paths, transitive entrypoints, edges, and primitives

function validate_registry(registry, discovered):
    reject duplicate, missing, or non-existent paths
    require target_kind, execution_host_binding, scheduler_identity, ownership_authority
    require each direct surface to enumerate operations and every authority branch
    require typed enums and booleans for operation target, branch strength, and transaction fields
    reject unknown keys, empty attestations, and descriptive owner/note authority
    for each true guarantee, run a closed checker-owned attestation evaluator
    reject registry-defined regexes, tokens, line numbers, or prose as truth predicates
    run a checker-owned operation/authority-branch-set evaluator for shared classifiers/backends
    derive surface status from the closed worst-case lattice; do not store authored status
    for migration-required, allow false or unknown guarantees but require a distinct disposition issue
    validate offline issue coordinates as this repository + numeric issue + non-self reference
    validate disposition groups cover an exact declared set of migration surfaces
    fail when discovered paths and registered paths differ

function render_audit(registry, discovered, output):
    call the same registry validator before rendering
    group surfaces by scheduler identity and compliance status
    deterministically show every row once with exact gaps and follow-up links
    embed input_digest from the versioned length-framed byte serialization below
    state that registry inclusion is not approval to mutate live scheduler state

command check-scheduler-mutation-surfaces.py:
    default: validate tracked source + registry, emit machine-readable diagnostics
    --render-html PATH: validate, then render deterministic registry-derived HTML
    --check-html PATH: compare regenerated bytes exactly, including input_digest
```

### Registry and source-attestation contract

Each registry surface will use this closed structure; unknown keys will fail:

| Level | Required fields / closed values |
|---|---|
| Surface | `path`, `kind: direct-owner|transitive-entrypoint`, `operations`; authored status is forbidden because status is derived |
| Operation | `id`, `primitive: crontab-replace|systemd-user-unit-write|systemd-user-enable-disable|windows-task-set|windows-task-unregister-register`, `target_kind: current-user-cron|root-cron|systemd-user|windows-current-user-task`, `scheduler_identity`, `execution_host_binding: physical-local|explicit-remote-transport`, optional closed `selection_condition`, `destructive`, `authority_branches`, `transaction` |
| Authority branch | `id`, `mechanism: managed-block-exact|exact-sentinel|command-tokens-adjacent|command-substring|catalog-key-substring|fixed-task-path-name|unknown`, `config_source`, `destructive`, `strength: exact|parsed|substring|unknown` |
| Transaction | booleans for `lock`, `baseline_snapshot`, `backup`, `pre_write_cas`, `post_write_preservation_verify`, `post_write_exact_state_verify`, `rollback_cas`; every `true` field requires one checker-owned attestation ID |
| Transitive edge | `callee`, `call_form: literal-exec|literal-bash|constant-path-exec`, `mutation_mode: default|flag-gated`, `target_guard_attestation` |
| Disposition group | `group_id`, one GitHub issue coordinate, exact member paths, and one defect-class enum; issue reuse is allowed only within that exact group |

Closed attestation IDs will be implemented in checker code, not configured as regexes. Initial evaluators will be exactly: `python-physical-host-equality-guard-v1`, `python-prewrite-baseline-cas-v1`, `python-postwrite-preservation-multiset-v1`, `python-postwrite-exact-state-v1`, `python-rollback-after-cas-v1`, `cron-command-tokens-adjacent-v1`, `managed-block-exact-v1`, `shell-exact-sentinel-v1`, `cron-classifier-destructive-branches-v1`, `kanban-backend-operation-set-v1`, `crontab-current-user-target-v1`, `crontab-root-target-v1`, `systemd-user-unit-name-v1`, `systemd-user-enable-disable-v1`, `windows-task-path-name-v1`, `windows-current-user-principal-v1`, `windows-task-set-operation-v1`, and `windows-task-unregister-register-v1`. Unknown IDs fail. Each evaluator will parse its fixed source/config shape conservatively and return `unknown` on unsupported syntax. Mutation tests will alter the required source shape and prove the attestation fails. The classifier/backend set evaluators will derive the complete destructive branch or operation IDs; registry equality with that derived set will be mandatory, so a future fourth branch cannot be omitted. `cron_apply.py` will enumerate separate authority branches for preserved-entry promotion, installed fingerprints, and catalog-key fallback; substring branches will force its destructive-identity status to `migration-required`. Its preservation verifier will not be mislabeled as exact intended-state verification.

The kanban surface will remain one unique direct-owner path with at least three distinct operations: systemd unit-file write, systemd enable/disable, and current-user crontab replacement. Each operation will carry its own target and selection condition, and `kanban-backend-operation-set-v1` will prove neither capability branch is omitted.

The derived status lattice will be deterministic:

1. `migration-required` when any destructive authority branch has `substring|unknown` strength, any target/branch-set attestation is false/unknown, or any required transaction guarantee is false/unknown.
2. `compliant` only when every destructive branch is `exact|parsed`, all target and completeness attestations pass, and every required transaction guarantee passes.
3. Non-destructive preservation-only substring branches will be reported as warnings but will not alone downgrade status.

There will be no authored `computed_status`; the checker and HTML renderer will use only the derived value.

### Canonical provenance serialization

The report digest preimage will be versioned and collision-free at record boundaries:

```text
ASCII "scheduler-mutation-input-v1\0"
u64be(registry_length) || registry_bytes
u64be(record_count)
for each record sorted by raw path bytes:
    u64be(path_length) || raw_path_bytes || u64be(blob_length) || index_blob_bytes
```

The included record set will be the union of all registered direct/transitive paths, every registry-referenced config/source path, the checker, its test, and `.github/workflows/enforcement-gate.yml`. Paths will remain raw bytes through `git ls-files -z`, `git cat-file --batch-command -Z`, bytewise sorting, and framing; decoding is presentation-only. `-Z` support is mandatory and absence fails closed. Tests will cover newline, tab, leading dash, non-UTF-8 path bytes, record-order stability, and adversarial boundary-collision pairs.

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

No production scheduler writer will be behaviorally modified in this issue. Before the registry lands, implementation will create one or more non-self follow-up issues that cover every `migration-required` surface; if issue creation partially fails, the registry/commit will not proceed. One issue may cover several surfaces only through a disposition group whose exact members share one defect class. The offline checker will validate repository, numeric issue, non-self reference, and group coverage without asserting issue existence or open state. Optional operator live-state enrichment will be timestamped and non-authoritative; CI will not depend on GitHub availability. Closing a disposition issue without removing or changing its `migration-required` rows will remain visible as governance debt, not silently certify compliance.

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
| `test_index_bytes_win_over_dirty_worktree` | Attestation authority is the staged/index blob. | Different index and working-tree bytes | Scanner evaluates index bytes only. |
| `test_registry_requires_exact_local_target_identity` | Execution host and scheduler identity cannot be inferred from `--machine` or workspace path. | Entry missing required target fields | Schema failure. |
| `test_descriptive_metadata_cannot_authorize_ownership` | `owner`, `note`, and substring-only description fields cannot be destructive authority. | Invalid ownership block | Schema failure. |
| `test_transaction_contract_is_complete` | Every surface declares lock/snapshot/backup/CAS, preservation verification, exact-state verification, and rollback fields separately. | Entry missing rollback CAS | Schema failure. |
| `test_compliant_claims_require_source_attestation` | Registry booleans cannot certify behavior without matching source evidence. | Truthy guarantee with absent/mismatched evidence | Schema/attestation failure. |
| `test_closed_attestation_evaluators_reject_mutated_source_shapes` | Registry prose/regex cannot define truth and each supported guarantee has an executable checker-owned predicate. | Wrong path, comment-only token, stale shape, reused unrelated attestation | Attestation returns unknown/failure. |
| `test_mixed_authority_branches_compute_worst_case_status` | Safe CAS cannot hide substring-based destructive identity. | `cron_apply.py` branch matrix | Surface becomes `migration-required` until every destructive branch is semantic. |
| `test_classifier_branch_set_is_complete` | A new destructive classifier route cannot be omitted from the registry. | Mutated classifier with fourth route | Derived branch-set mismatch/unknown failure. |
| `test_dual_backend_owner_has_all_operation_targets` | One kanban owner represents systemd file/state and crontab branches without duplicate path rows. | Current kanban source + registry | Three operations and both target kinds required. |
| `test_status_lattice_is_deterministic` | Worst-case status has one closed result for branch/target/transaction combinations. | Parametrized exact/substring/unknown and true/false matrix | Expected `compliant|migration-required`. |
| `test_preservation_verification_is_not_exact_state_verification` | A multiset preservation check cannot certify the rendered intended state. | Current `cron_apply.py` evaluator | Preservation true; exact-state false/unknown. |
| `test_migration_required_has_traced_follow_up` | Grandfathered gaps cannot become permanent anonymous exceptions. | Migration entry without issue URL | Schema failure. |
| `test_follow_up_coordinates_reject_self_wrong_repo_and_duplicates` | Offline issue references cannot point to #3470, another repo, or violate reuse policy. | Adversarial disposition fixtures | Schema failure. |
| `test_reference_cron_apply_contract_matches_source` | #3347 host binding and CAS guarantees remain represented; semantic identity is claimed only for fingerprints using `command_tokens`. | `scripts/cron/cron_apply.py`, `cron_transaction.py`, catalog | Source attestations validate precisely. |
| `test_checker_does_not_block_its_forensic_artifacts` | Pattern literals in the checker/tests require narrow per-line sentinels and do not self-register. | Real checker and test files | Neither appears as a mutator; unsentinelled executable fixture fails. |
| `test_forensic_sentinel_cannot_suppress_production_mutator` | The narrow sentinel cannot become a production bypass. | Sentinelled mutation line outside exact checker/test allowlist | Mutation is still discovered. |
| `test_html_is_deterministic_and_registry_complete` | Every registry row/status/link appears once and exact source provenance remains current. | Registry + index records | Byte-stable HTML, exact row parity, exact input digest. |
| `test_stale_html_input_digest_fails` | CI cannot normalize away stale evidence. | HTML with prior digest | Parity failure. |
| `test_digest_framing_is_unambiguous_and_byte_sorted` | Distinct record boundaries/order cannot share a preimage. | Collision-pair, path-order, odd-byte fixtures | Distinct/stable digests. |
| `test_cat_file_transport_requires_nul_mode` | Newline/non-UTF-8 paths cannot corrupt index reads. | Fake Git with/without `-Z` support | Correct bytes or fail-closed version diagnostic. |
| `test_enforcement_workflow_is_failure_propagating` | The new check cannot remain unused/advisory/commented out. | Parsed `.github/workflows/enforcement-gate.yml` | Active PR job runs validation and parity; no `continue-on-error`, `|| true`, or swallowed nonzero. |
| `test_recognized_call_grammar_and_unknown_indirection` | Literal/constant wrapper calls are modeled and unsupported scheduler indirection fails for review. | Direct and variable-indirection wrapper fixtures | Known edge or explicit unknown-edge failure, never silent omission. |
| `test_cli_reports_machine_readable_failures` | CI and operators receive deterministic diagnostics. | Invalid registry fixture | Stable JSON/text error and non-zero exit. |

---

## Acceptance Criteria

- [ ] Tests will be written first and will fail before the registry/check exists.
- [ ] The registry will enumerate exactly eight unique direct-owner paths plus three transitive entrypoints/call edges; multi-backend owners will carry operation-level targets and complete backend operations without duplicate path rows.
- [ ] The enforcement check will fail on unregistered mutation primitives and invalid/incomplete safety contracts.
- [ ] Reference/compliant guarantees will require closed checker-owned source attestations. `cron_apply.py` will enumerate every destructive authority branch; substring catalog/fingerprint branches will force worst-case identity status to `migration-required` while host/CAS guarantees remain independently attested.
- [ ] Every non-compliant surface will have `migration-required` status plus a linked GitHub follow-up issue; registry inclusion alone will not waive the gap.
- [ ] The durable rule will forbid descriptive metadata or arbitrary substring matches from certifying a surface as compliant for deletion/replacement; existing occurrences will remain explicitly `migration-required` until separately changed.
- [ ] The HTML report will show the complete matrix, exact deterministic input digest, limitations, and follow-up coordinates; optional live issue state will be clearly timestamped and non-authoritative.
- [ ] A parsed active PR workflow job will invoke validation and deterministic HTML parity with failure propagation and no advisory/error-swallowing flags. Branch-protection registration remains external and will not be claimed by this issue.
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
| Fallback governance audit r2 | MAJOR → patched | Required operation/authority-branch modeling, worst-case status, and closed checker-owned evaluators. |
| Fallback schedule audit r2 | MAJOR → patched | Required path-restricted sentinels, exact input provenance, parsed blocking-workflow semantics, and offline-only issue claims. |
| Codex r2 | MAJOR → patched | Required substring branches to remain migration-required and split preservation verification from exact-state verification. |
| Codex r3 | APPROVE | Verified both Codex r2 blockers against source at revision `89a3ef860`. |
| Fallback governance audit r4 | APPROVE | Verified operation-level targets, branch-set completeness, closed evaluator IDs, and status lattice at `1779e930e`. |
| Fallback schedule audit r4 | APPROVE | Verified dual targets, framed provenance, NUL-safe index transport, and derived-only status at `1779e930e`. |

**Overall result:** PASS — Codex r3 and both focused fallback r4 reviews returned APPROVE. Claude and Gemini are documented unavailable; no implementation is authorized before user approval.

Revisions made based on r1:

- The plan separates eight direct primitive owners from three transitive entrypoints and models call edges.
- Typed source-attested guarantees replace self-asserted compliance booleans.
- NUL-safe tracked-file discovery, narrow forensic sentinels, real-file self-block tests, and automatic workflow wiring are explicit.
- HTML becomes deterministic checker output with parity verification.
- Follow-up issue creation and offline validation boundaries are explicit.
- R2 replaces path-level certification with operation/authority-branch modeling and worst-case status.
- R2 defines closed checker-owned attestation IDs, exact index-byte authority, path-restricted forensic sentinels, exact input-digest provenance, and parsed failure-propagating workflow semantics.
- R3 moves target identity to operations, adds classifier/backend completeness evaluators, closes Windows/systemd IDs and the status lattice, and defines `cat-file -Z` plus length-framed byte provenance.

---

## Risks and Open Questions

- **Inventory evasion:** Regex discovery alone can miss indirection; the check will combine direct primitives, reviewed call edges, exact inventories, and adversarial wrapper fixtures.
- **Grandfathering risk:** `migration-required` could become a permanent waiver; each such entry will require a syntactically valid non-self disposition coordinate and remain visibly non-compliant until the row itself changes. Live issue state is report enrichment, not an offline enforcement claim.
- **Cross-platform verification:** Linux CI cannot prove Windows runtime rollback behavior; this issue will register that gap and route behavioral changes to Windows-capable follow-ups.
- **Self-blocking enforcement:** Executable checker/test files may quote mutation signatures. Only exact per-line forensic sentinels in the two explicit forensic paths will suppress non-executed literals; production paths remain unsuppressible and a dedicated bypass regression will enforce that boundary.
- **Scope boundary:** This issue will enforce inventory/governance only. It will not silently refactor the eight direct owners or three transitive entrypoints, and it will not authorize live scheduler changes.

---

## Complexity: T3

**T3** — the contract spans Linux cron, systemd user timers, Windows Task Scheduler, schema enforcement, CI tests, operator documentation, and multiple follow-up migration boundaries.
