# Plan for #3475: Make cron deletion identity semantic and verify exact post-write state

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3475
> **Client:** N/A
> **Lane:** lane:codex
> **Review artifacts:** `scripts/review/results/2026-07-11-plan-3475-claude.md` | `scripts/review/results/2026-07-11-plan-3475-codex.md` | `scripts/review/results/2026-07-11-plan-3475-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/cron/cron_apply.py:220-296` will remain the only direct current-user-crontab owner in scope. It already binds the requested machine to the physical host, locks, snapshots baseline A, writes an exclusive fsynced backup, performs a pre-write CAS, and protects rollback with a second CAS.
- `scripts/cron/cron_apply.py:269-296` currently verifies only the multiplicity of pre-existing preserved/ignore lines. It can return `applied` when the observed post-write crontab differs from `plan["new_text"]` in any other way.
- `scripts/cron/cron_transaction.py:140-188,240-277,383-420` currently exposes four ownership routes. `command_tokens` plus `cwd_basename` is parsed; `command_contains`, `cwd_contains`, `script_basename`, and the derived catalog-key fallback are substring mechanisms.
- `scripts/cron/cron_transaction.py:487-548` deletes every out-of-block line classified as `cataloged`, so only destructive routes—not keep-verbatim preservation routes—will be required to use semantic identity.
- `scripts/cron/setup-cron.sh:31-70` and `scripts/setup/new-machine-setup.sh:190-202` are transitive entrypoints. They will retain delegation, physical-host rejection, Windows skip, and dry-run semantics; they will not acquire scheduler ownership.

### Standards and durable contracts

| Contract | Current state | Source |
|---|---|---|
| Destructive identity | Migration required: three substring authority branches remain | `config/scheduled-tasks/mutation-surfaces.yaml`, operation `reconcile-current-user-crontab` |
| Transaction | Migration required: `post_write_exact_state_verify: false` | `config/scheduled-tasks/mutation-surfaces.yaml` |
| Scheduler mutation rule | Parsed/exact destructive identity and exact post-write verification are mandatory | `.claude/rules/scheduler-mutation-safety.md` |
| Completeness closeout | Evidence score, HTML artifact, owner verification, and server gate will precede closure | `.claude/rules/completeness-before-close.md` |

No engineering standard or LLM-wiki source applies to this infrastructure-only change.

### Documents consulted

- [Issue #3475](https://github.com/vamseeachanta/workspace-hub/issues/3475) defines the three exact transitive/direct surfaces and requires semantic destructive identity plus exact intended-state verification.
- `docs/plans/2026-07-11-issue-3347-cron-installer-convergence.md` established the lock/backup/CAS transaction and the fail-closed unknown-line boundary that this plan will preserve.
- `docs/plans/2026-07-11-issue-3470-scheduler-mutation-safety-contract.md` established operation-level authority branches, derived status, and source attestations. This issue will change only the `cron-catalog-migration` disposition group.
- `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` records the audited baseline: `cron_apply.py` is migration-required because destructive substring branches and exact-state verification remain.
- Drive-index query `cron semantic ownership exact post-write state scheduler transaction` (2026-07-12T03:29:08Z) returned no relevant operational document; returned CAD/engineering-title token collisions were discarded. The master document index was unreachable and three indexes were stale, so repository evidence will be authoritative for this repo-local behavior.

### Parallel-work check

- Bounded `pgrep`, remote-branch, worktree, and local-artifact checks found no competing #3475 implementation or plan branch. The only matching process was the probe itself.
- Planning execution mode is `parallel-readonly`; implementation will be `single-lane` because classifier, catalog data, transaction behavior, registry attestations, and generated HTML share one correctness boundary.

### Gaps identified

- No exact post-write equality check exists.
- No closed exact identity map exists for destructive cron ownership.
- Two catalog-installed fingerprints still use `command_contains`; selected `notification-purge` promotion still uses substring fields; non-fingerprinted catalog tasks still reach destructive ownership through a substring-derived catalog key.
- Existing tests do not corrupt the write while preserving the old keep-verbatim multiset, and they do not prove that substring collisions cannot authorize deletion.

### Evidence and reproduction proofs

Verified 2026-07-12T03:28Z:

```text
$ gh issue view 3475 --json state,labels,title
OPEN; status:needs-plan; lane:codex

$ git ls-remote --heads origin '*3475*' '*cron*semantic*'
<empty>

$ uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py --json
status=ok; direct includes scripts/cron/cron_apply.py; transitive includes
scripts/cron/setup-cron.sh and scripts/setup/new-machine-setup.sh
```

Runtime defect reproduced hermetically at 2026-07-12T03:35Z. The command imported `cron_apply`, replaced `_read`, `_write`, `_load`, `_selection_context`, `_flock`, `create_backup`, and `plan_cutover` with in-memory seams, then made `_write` store `plan["new_text"] + unexpected_line` while retaining the required `# keep` line. No live crontab command was invoked.

```text
$ PYTHONPATH=scripts/cron uv run python - <<'PY'
from contextlib import contextmanager
from pathlib import Path
import cron_apply as ca

state = {"text": "# keep\n", "writes": []}
planned = "# keep\n# workspace-hub managed begin roles=control-plane\n0 1 * * * run-managed\n# workspace-hub managed end\n"

def read():
    return state["text"]

def write(text):
    state["writes"].append(text)
    state["text"] = text + "0 9 * * * unexpected-injected-line\n"

@contextmanager
def no_lock(_path):
    yield

ca._load = lambda _path: {}
ca._selection_context = lambda *_a, **_k: {
    "machine_id": "dev-primary", "roles": ["control-plane"],
    "selected_raw": [], "selected": [], "selected_task_ids": set(), "conflicts": []
}
ca.ct.catalog_command_keys = lambda *_a, **_k: []
ca.catalog_fingerprints = lambda *_a, **_k: []
ca.external_fingerprints = lambda *_a, **_k: []
ca.ct.plan_cutover = lambda *_a, **_k: {
    "new_text": planned, "preserved": ["# keep"], "uncataloged": [],
    "conflicts": [], "abort_reason": None
}
ca._flock = no_lock
ca.create_backup = lambda *_a, **_k: Path("/tmp/hermetic-backup")
result = ca.run_cutover("dev-primary", apply=True, ts="repro",
                        _read=read, _write=write, _daemons=[])
print({"status": result["status"],
       "planned_equals_observed": planned == state["text"],
       "write_count": len(state["writes"])})
PY
{'status': 'applied', 'planned_equals_observed': False, 'write_count': 1}
```

Failure mode observed matches issue claim: **YES** — current code reports success for a non-exact post-write state.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-11-issue-3475-cron-semantic-ownership.md` |
| Human plan | `docs/reports/2026-07-11-issue-3475-cron-semantic-ownership-plan.html` |
| Transaction and classifier | `scripts/cron/cron_apply.py`, `scripts/cron/cron_transaction.py` |
| Read-only audit consumer | `scripts/cron/cron-audit.py` |
| Catalog identities | `config/scheduled-tasks/schedule-tasks.yaml`, `config/workstations/harness-state-classes.yaml` |
| Registry contract | `config/scheduled-tasks/mutation-surfaces.yaml` |
| Tests | `tests/cron/test_cron_apply.py`, `tests/cron/test_cron_transaction.py`, `tests/cron/test_cron_audit.py`, `tests/cron/test_setup_cron.py`, `tests/enforcement/test_scheduler_mutation_surfaces.py` |
| Generated audit | `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` |
| Plan reviews | `scripts/review/results/2026-07-11-plan-3475-*.md` |
| Code reviews | `scripts/review/results/2026-07-11-code-3475-*.md` |
| Completeness report | `docs/reports/<completion-date>-3475-completeness.html` |

---

## Deliverable

The canonical cron reconciler will authorize deletion only through a closed exact rendered/legacy line identity contract and will accept a write only when the re-read crontab exactly equals the planned bytes, with CAS-guarded rollback for every mismatch.

---

## Design and Pseudocode

### 1. Exact destructive identity (no shell interpretation)

The implementation will not create a custom shell parser. Destructive ownership will use exact bytes already produced by the canonical renderer:

- `canonical_exact_lines`: a task-id keyed set of complete rendered cron lines (`schedule + single space + rendered command`) for the selected machine context;
- `legacy_exact_lines`: an explicit task-id keyed allowlist of complete historical line variants that are known to exist outside the managed block;
- managed-block ownership: exact begin/end sentinels will continue to own every line structurally inside the block.

Exact comparison will include schedule, environment assignments, cwd spelling, operators, quoting, substitutions, glob text, redirects, redirect targets, and trailing command text. It will perform no shell evaluation, expansion, normalization, substring search, basename match, token-fragment match, or nested-string interpretation. Two lines will be the same destructive identity only when their complete line bytes are equal to one allowlisted rendered/legacy line for exactly one selected task.

`command_contains`, `command_tokens`, `cwd_contains`, `cwd_basename`, and `script_basename` may remain available only for non-destructive keep-verbatim classification. Schema validation will forbid `catalog_task_id` on all such preservation fingerprints; a promotable row must instead carry `legacy_exact_lines`. This closes the future-promotion inverse, not only the current `notification-purge` fixture.

```text
build_ownership_context(catalog, registry, machine_id):
    select and render tasks using the canonical machine context
    map each selected task id to its complete canonical cron line bytes
    add only schema-validated complete legacy line variants for that task id
    fail if a line is empty, belongs to multiple selected tasks, or has unknown metadata
    return selected ids, exact line->task map, and preservation-only fingerprints

classify_line_detail(line, ownership_context):
    keep comments/env/blank as ignore
    match preservation fingerprints only as keep-verbatim
    if complete line bytes equal exactly one selected task identity: cataloged
    if exact line is ambiguous: explicit classification error
    otherwise: uncataloged, so cutover aborts before backup/write
```

### 2. Catalog-wide migration inventory

Planning has selected exact-line identity precisely because every canonical catalog task is already renderable as complete bytes, regardless of shell complexity. Implementation will first produce `docs/reports/issue-3475-command-identity-inventory.json` by rendering every cron-scheduler task for every Linux machine context in `config/machines/registry.yaml`. The inventory will record task id, machine id, canonical line digest, uniqueness result, and any explicit historical variant id; it will not contain live crontab data.

The supported canonical set will therefore be **all successfully rendered selected cron tasks**. The unsupported set will be named in the inventory and must be empty before classifier changes proceed; render failures or duplicate exact lines will stop implementation and force plan revision. Unknown live out-of-block lines are intentionally unsupported and will continue to abort.

- `hermes-claude-bridge` and `repository-sync` will drop substring installed fingerprints because their canonical complete rendered lines provide exact identity.
- The known absolute-workspace `notification-purge` historical variant will move from selected substring promotion to one explicit complete `legacy_exact_lines` variant bound to that task id.
- Any additional historical variant discovered only from repo-tracked fixtures/prior audit evidence will require its own full-line allowlist entry and test. Implementation will not scan the live crontab to populate this list.
- The old `catalog_command_keys(...)->cmd in line` destructive fallback will be removed from both apply and audit.
- External/private and machine-local rows without `catalog_task_id` will remain keep-verbatim preservation rules even when their recognition is substring-based; they will never authorize deletion or replacement.

### 3. Exact post-write transaction verification

```text
with exclusive lock:
    current = read()
    abort unless current == baseline_A
    backup = durable_exclusive_backup(baseline_A)
    write(planned_B)
    observed_C = read()

if observed_C != planned_B:
    with exclusive lock:
        current = read()
        if current != observed_C:
            return rollback-aborted without overwriting concurrent state
        write(baseline_A)
        restored = read()
        if restored != baseline_A:
            return rollback-failed with backup path and observed diagnostics
    return rolled-back with bounded mismatch diagnostics

return applied only when observed_C == planned_B
```

The equality contract will be byte-for-byte text equality, including ordering, multiplicity, comments, environment lines, and trailing newline. The result will not emit full crontab content; diagnostics will report bounded hashes/counts and the backup path. Rollback restoration will be re-read and verified before reporting `rolled-back`.

Post-backup exceptions will use a fail-closed state machine:

| Failure | Safe observation | Result/action |
|---|---|---|
| Initial write raises | Re-read equals A | `write-failed-no-change`; retain backup; no rollback write |
| Initial write raises | Re-read equals B | non-success `write-error-state-exact`; retain backup for operator review |
| Initial write raises | Re-read returns other C | CAS-guarded rollback from C |
| Initial write raises | Re-read also raises | `verification-indeterminate`; never blind-rollback |
| Post-write verification read raises | State cannot be established | `verification-indeterminate`; never blind-rollback |
| Rollback write raises | Re-read equals A | `rolled-back-with-write-error`, preserving diagnostic |
| Rollback write raises | Re-read equals original C | `rollback-failed`; A was not restored |
| Rollback write raises | Re-read is third state | `rollback-aborted`; concurrent state is preserved |
| Rollback verification read raises | Restoration cannot be established | `rollback-indeterminate` |
| Rollback-CAS read raises before restore | Ownership of C cannot be established | `rollback-indeterminate`; retain backup; perform no rollback write |

All exception results will be nonzero CLI outcomes except a verified exact ordinary apply. The implementation will never claim `applied` without an observed exact B and will never restore A without first observing a CAS value it owns.

### 4. Audit/apply parity

`scripts/cron/cron-audit.py` and `cron_apply.py` will call the same `build_ownership_context()` with the same selected task ids, canonical machine/workspace render context, exact canonical/legacy line map, and preservation fingerprints. Shared fixture tests will require equality of each full `classify_line_detail()` result—including class, reason, task id, ambiguity/error state, selected/non-selected promotion, and parser-free exact-line source—not merely the four class labels. The audit will remain read-only.

### 5. Registry and enforcement

- The registry will replace the three substring destructive branches with `canonical-exact-line` and `legacy-exact-line` branches, remove `catalog-key-fallback`, set `post_write_exact_state_verify: true`, and add checker-owned attestations for exact destructive identity, exact post-write equality, and verified rollback restoration.
- The closed registry schema will gain a `delegation` object for transitive rows: `immediate_callee`, `terminal: {path, operation_id}`, and a closed `modes` map. Each mode will declare `mutation_mode`, exact argument transformation, target/host mapping, exit policy, and source attestation. Resolution will follow immediate-callee edges, reject cycles, missing/ambiguous terminals, cross-operation mismatches, and unbounded chains, then inherit authority/transaction status only for destructive modes whose exit/argument mapping is proven.
- `setup-cron.sh` modes will cover default apply, explicit dry-run, allow-live-reload, remote-host rejection, and Windows skip. `new-machine-setup.sh` modes will cover default Linux delegation, dry-run preview, and Windows skip. Its dry-run `|| true` observability debt will remain explicitly linked to [#3490](https://github.com/vamseeachanta/workspace-hub/issues/3490); because that mode is non-mutating it will not falsify the inherited destructive contract, but it may not be omitted or labeled as propagated success.
- `harness-update.sh -> setup-cron.sh -> cron_apply.py` will resolve to the same terminal operation while retaining its own `harness-update` disposition and [#3479](https://github.com/vamseeachanta/workspace-hub/issues/3479) exit-policy gap. Cross-disposition resolution will inherit only the terminal mutation guarantees, never the wrapper's overall compliance status.
- Transitive entries will be forbidden from declaring independent authority/transaction fields unless discovery proves a scheduler primitive. A wrapper that gains such a primitive will fail closed as an unregistered direct owner.
- `scripts/enforcement/scheduler_mutation_contract.py`, `check-scheduler-mutation-surfaces.py`, the HTML renderer, delivery tests, and hardening tests will all migrate to this closed multi-hop schema; renderer and status derivation will not assume every transitive row owns an operation.
- The enforcement checker will derive those claims from source/config and will continue to fail closed on missing branches, unsupported aliases, stale HTML, or self-disposition coordinates.
- On compliance, active `cron-catalog-migration` will be removed from `disposition_groups` and its three rows will drop active disposition references. A separate non-authoritative `resolved_dispositions` ledger entry will preserve issue #3475, the three members, resolution date, and merged commit; schema validation will forbid active disposition coordinates on compliant rows. Unrelated #3476–#3479 dispositions will remain active and exact.
- The generated #3470 scheduler-safety HTML will be refreshed deterministically. Every #3475 member will resolve to the same exact-identity/exact-state direct-owner contract; no member may retain destructive substring authority or `post_write_exact_state_verify: false`.
- Before completeness closeout, automation or the operator will verify that `gate:completeness` has been auto-applied when the issue reaches `status:plan-approved`; if absent, closeout will stop and request owner/repository action rather than claiming server enforcement.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/cron/cron_transaction.py` | Add shared exact-line ownership context and remove destructive substring fallback |
| Modify | `scripts/cron/cron_apply.py` | Use exact identities and exact post-write/rollback-restoration verification |
| Modify | `scripts/cron/cron-audit.py` | Consume the same exact identity context and remove audit-side substring ownership |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | Remove two substring installed fingerprints; canonical rendering becomes exact identity |
| Modify | `config/workstations/harness-state-classes.yaml` | Replace selected notification-purge promotion with explicit exact legacy line |
| Modify | `config/scheduled-tasks/mutation-surfaces.yaml` | Record the new derived authority and transaction guarantees |
| Modify | `scripts/enforcement/scheduler_mutation_attestations.py` | Add closed source attestations required by the registry |
| Modify | `scripts/enforcement/scheduler_mutation_contract.py` | Validate exact identities, multi-hop delegation, resolved dispositions, cycles, and terminal operations |
| Modify | `scripts/enforcement/check-scheduler-mutation-surfaces.py` | Derive and render direct operations/transitive delegation modes without assuming operations on every row |
| Modify | `scripts/cron/validate-schedule.py` | Validate exact legacy identity schema and forbid promotable substring rows |
| Modify | `tests/cron/test_cron_transaction.py` | Add exact identity/collision/near-match regressions |
| Modify | `tests/cron/test_cron_apply.py` | Add exact-state and rollback verification RED/GREEN cases |
| Modify | `tests/cron/test_cron_audit.py` | Prove audit/apply classification parity and retain read-only behavior |
| Modify | `scripts/cron/tests/test_validate_schedule.py` | Test closed exact identity and catalog-wide uniqueness validation |
| Modify | `tests/cron/test_setup_cron.py` | Preserve wrapper delegation and nonzero failure propagation |
| Modify | `tests/enforcement/test_scheduler_mutation_surfaces.py` | Prove registry/source/report transition without weakening other groups |
| Modify | `tests/enforcement/test_scheduler_mutation_delivery.py` | Prove delegated rows render and workflow parity remains failure-propagating |
| Modify | `tests/enforcement/test_scheduler_mutation_hardening.py` | Test chain/cycle/terminal/disposition and source-attestation bypasses |
| Create | `docs/reports/issue-3475-command-identity-inventory.json` | Record catalog-wide render/uniqueness coverage without live state |
| Update | `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` | Refresh deterministic audit matrix |
| Update | `docs/ops/scheduled-tasks.md` | Document semantic destructive identity and exact-state failure handling |
| Update | `docs/plans/README.md` | Index this plan and reconcile completed #3470 state |

`scripts/cron/setup-cron.sh` and `scripts/setup/new-machine-setup.sh` are verification surfaces, not expected implementation edits. `new-machine-setup.sh` dry-run failure reporting is promoted to [issue #3490](https://github.com/vamseeachanta/workspace-hub/issues/3490); #3475 will model that non-mutating exit-policy gap without implementing it.

---

## TDD Test List

Tests will be committed in RED state before implementation and split into two GREEN increments.

| Test name | What it will verify | Expected result |
|---|---|---|
| `test_post_write_append_mismatch_rolls_back_exact_baseline` | Unexpected appended line cannot pass preserved-only verification | `rolled-back`; writes planned B then A |
| `test_post_write_drop_or_mutation_rolls_back` | Missing/mutated managed task cannot report applied | Parametrized exact mismatch rolls back |
| `test_post_write_stale_duplicate_rolls_back` | Retained legacy duplicate violates intended state | Exact mismatch rolls back |
| `test_exact_mismatch_concurrent_change_aborts_rollback` | Rollback CAS protects a third-party update | `rollback-aborted`; A is not written |
| `test_rollback_restore_is_reread_and_verified` | A failed restore is not reported as successful rollback | `rollback-failed` with backup evidence |
| `test_exact_post_write_match_applies_once` | Exact B succeeds without extra writes | `applied`; one write |
| `test_exact_identity_requires_complete_line_bytes` | Token-as-data, operator, quoting, cwd, redirect, schedule, and newline near-misses cannot authorize deletion | Only complete allowlisted line matches |
| `test_catalog_identity_inventory_covers_every_linux_context` | Every selected cron task renders uniquely for every Linux machine context | Empty unsupported/collision sets |
| `test_known_legacy_identity_is_exact_and_task_bound` | Notification-purge absolute-path variant is supported without matching near variants | Exact variant cataloged; all near misses uncataloged |
| `test_catalog_key_substring_no_longer_deletes` | The old `cmd in line` route is absent | Collision aborts cutover |
| `test_selected_promotion_requires_exact_identity` | `notification-purge` promotion cannot use `command_contains` | Exact variant cataloged; collisions not cataloged |
| `test_catalog_task_id_rejected_on_substring_preservation_identity` | Future metadata cannot reactivate destructive substring promotion | Config validation fails closed |
| `test_non_destructive_preservation_substrings_never_promote` | Keep-verbatim rows without catalog identity remain safe | Always `preserved_external` |
| `test_all_selected_cron_tasks_have_unique_destructive_identity` | Derived/explicit identities are non-empty and collision-free per machine context | No duplicate owner for fixture matrix |
| `test_audit_and_apply_share_exact_classification` | Read-only audit and mutator cannot drift on ownership | Identical detailed classifications for adversarial fixture matrix |
| `test_write_and_post_write_read_exception_contract` | Partial writes and indeterminate reads never claim success or blind-rollback | Exact state-machine statuses and nonzero CLI |
| `test_rollback_write_and_read_exception_contract` | Rollback exceptions preserve concurrent state and report verification truthfully | `rolled-back-with-write-error`, `rollback-failed`, `rollback-aborted`, or `rollback-indeterminate` as observed |
| `test_registry_advances_only_cron_catalog_group` | Checker derives new guarantees without waiving unrelated gaps | cron group compliant; #3476–#3479 remain migration-required |
| `test_transitive_cron_members_inherit_one_direct_owner_contract` | setup/onboarding wrappers cannot retain copied legacy authority/transaction fields | Both edges resolve to cron_apply operation; no substring/false exact-state member remains |
| `test_transitive_delegate_with_direct_primitive_fails_closed` | A wrapper cannot hide a new scheduler write behind inherited compliance | Discovery reports unregistered direct ownership |
| `test_delegation_chain_cycle_terminal_and_mode_contract` | Immediate/terminal edges, cycles, missing/ambiguous targets, argument maps, and exit policies are closed | Valid chains resolve; every malformed chain fails |
| `test_harness_update_retains_3479_wrapper_gap` | Terminal mutation safety cannot erase wrapper failure-swallowing disposition | Terminal inherited; wrapper remains migration-required |
| `test_resolved_disposition_transition_is_exact` | #3475 leaves active disposition coverage without losing traceability | Active group removed; resolved ledger exact; compliant rows have no active coordinate |
| `test_rollback_cas_read_exception_is_indeterminate` | Failure to establish ownership of observed C cannot trigger blind restore | `rollback-indeterminate`; no rollback write; backup retained |
| `test_initial_corruption_fixtures_distinguish_restore_outcomes` | One-shot, persistent, and concurrent corruption are not conflated | rolled-back / rollback-failed / rollback-aborted respectively |
| `test_setup_cron_surfaces_exact_state_failure` | Wrapper preserves nonzero status from direct owner | Fake-only invocation exits nonzero |

Focused commands:

```bash
uv run pytest tests/cron/test_cron_transaction.py tests/cron/test_cron_apply.py tests/cron/test_cron_audit.py tests/cron/test_setup_cron.py -v
uv run pytest tests/enforcement/test_scheduler_mutation_surfaces.py -v
uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py
uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py --check-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html
```

---

## Acceptance Criteria

- [ ] RED evidence will show the current code reports `applied` for at least one exact-state corruption while every preserved line survives.
- [ ] `applied` will require byte-for-byte equality between the observed post-write crontab and `plan["new_text"]`.
- [ ] Every observed mismatch C will enter CAS-guarded rollback; indeterminate reads will never trigger a blind restore, and restoration success will require re-read equality with baseline A.
- [ ] Initial-write, post-write-read, rollback-write, and rollback-read exceptions will follow the documented non-success state machine and retain bounded backup diagnostics.
- [ ] No destructive ownership branch will use substring matching. Complete exact rendered/legacy line identity, exact marker ownership, or fail-closed unknown classification will be the only outcomes.
- [ ] Catalog-key substring fallback will be absent from the destructive apply path.
- [ ] A repo-tracked catalog inventory will prove every selected cron task renders to one unique exact identity in every Linux context; unsupported and collision sets will be empty before classifier migration.
- [ ] `hermes-claude-bridge`, `repository-sync`, and selected `notification-purge` legacy identity will be migrated without broadening ownership or accepting any non-exact line.
- [ ] Audit and apply will share the exact-line classifier and will produce identical detailed ownership decisions for the same machine context.
- [ ] `catalog_task_id` will be invalid on substring-based preservation identities, preventing future promotion bypasses.
- [ ] Non-destructive external/local preservation rules will remain keep-verbatim and will not be treated as proof of destructive ownership.
- [ ] Ambiguous, malformed, colliding, or unknown live lines will abort before backup/write.
- [ ] Physical-local host binding, lock, exclusive fsynced backup, pre-write CAS, preservation behavior, rollback CAS, daemon guard, dry-run default, Windows skip, and transitive delegation will remain covered.
- [ ] The registry checker will derive compliance for the cron catalog group and will retain exact follow-up coordinates for [#3476](https://github.com/vamseeachanta/workspace-hub/issues/3476), [#3477](https://github.com/vamseeachanta/workspace-hub/issues/3477), [#3478](https://github.com/vamseeachanta/workspace-hub/issues/3478), and [#3479](https://github.com/vamseeachanta/workspace-hub/issues/3479).
- [ ] `setup-cron.sh` and `new-machine-setup.sh` registry rows will be attested pure delegation edges resolving to the direct-owner operation; they will carry no copied legacy substring branch or false exact-state transaction field, and any future direct primitive will fail discovery.
- [ ] Delegation resolution will be immediate-callee/multi-hop/mode aware, cycle-safe, terminal-operation exact, and will preserve the #3479 and #3490 wrapper observability gaps rather than inheriting blanket compliance.
- [ ] The active #3475 disposition group will be removed only after all members comply; historical issue/member/commit traceability will move to the validated resolved-disposition ledger.
- [ ] Focused cron and enforcement suites, Ruff, shell syntax/ShellCheck where touched, deterministic HTML parity, and `scripts/legal/legal-sanity-scan.sh --diff-only` will pass.
- [ ] T3 code-stage adversarial review will complete before merge.
- [ ] `gate:completeness` presence will be verified after plan approval; a completeness record and HTML report will reach the configured threshold and await owner-only `status:completeness-verified` before closure.
- [ ] No test or verification command will read, write, or enumerate the live user crontab; no scheduler/process mutation or destructive cleanup will occur.

---

## Risks and Open Questions

- **Exact-line drift risk:** harmless manual formatting changes will no longer count as owned legacy lines. This is intentional fail-closed behavior; a reviewed full-line variant must be added rather than weakening identity.
- **Migration compatibility risk:** old absolute-path invocations may differ from catalog rendering. Only explicit complete legacy lines will cover known variants; unknown variants will abort and require operator review.
- **Identity collision risk:** two tasks could render the same line. The catalog-wide machine-context inventory will require one-to-one task identity and block implementation on any collision.
- **Preservation inversion risk:** converting every substring preservation row would conflate keep-verbatim recognition with destructive authority. This plan will migrate only rows that can promote to selected catalog ownership.
- **Rollback diagnostics risk:** full crontab content may contain sensitive command arguments. Results will use bounded hashes/counts and existing backup coordinates rather than embedding content.
- **Downstream dependency:** [issue #3476](https://github.com/vamseeachanta/workspace-hub/issues/3476) should consume this hardened transaction only after #3475 lands. #3477 and #3478 are independent backends; #3479 and [#3490](https://github.com/vamseeachanta/workspace-hub/issues/3490) remain wrapper observability follow-ups.

No unresolved product decision blocks plan review. The supported grammar and legacy identity set remain correctness-critical review targets.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE | Fresh-clone trust dialog blocked non-interactive review |
| Codex | APPROVE r3 | Verified both r2 blockers: full reproduction and wrapper primitive-safe delegation plan |
| Gemini | UNAVAILABLE | Non-interactive authentication was not configured |
| Fallback cron audit | MAJOR | Required catalog-wide feasibility, closed grammar, rollback-CAS exception, and mode-aware delegation; plan pivoted from parsing to exact-line identity |
| Fallback governance audit | MAJOR | Required full enforcement schema/file scope, multi-hop edges, validators, disposition resolution, gate activation, detailed parity, and distinct rollback fixtures |

**Overall result:** MAJOR — r3 exact-line/schema revisions require focused fallback re-review; implementation remains blocked.

Revisions made after r1:

- Added the actual hermetic false-`applied` reproduction and output.
- Replaced adjacent-token/basename matching with a complete normalized top-level command structure and trusted machine-context workspace root.
- Added executable-position, operator, nested-shell, cwd-spoof, and ambiguity tests.
- Added `cron-audit.py` migration plus audit/apply parity tests.
- Defined non-success behavior for initial-write, verification-read, rollback-write, and rollback-read exceptions.
- Forbade `catalog_task_id` on substring preservation identities.

R2 corrections:

- Embedded the full replayable in-memory reproduction command instead of an elided fixture.
- Replaced copied legacy operations on both #3475 transitive members with a proposed attested `delegates_operation` relation that inherits exactly one direct-owner contract and fails closed if a wrapper gains a scheduler primitive.

R3 corrections after fallback review:

- Replaced the proposed custom shell grammar with complete exact rendered/legacy line identity and a catalog-wide per-machine uniqueness inventory.
- Added the missing rollback-CAS-read exception and separated one-shot, persistent, and concurrent corruption fixtures.
- Defined a closed immediate/terminal/multi-hop/mode-aware delegation contract, cycle/terminal checks, and explicit #3479/#3490 observability retention.
- Added enforcement contract/checker/renderer/delivery/hardening files and schedule/state-class validators to implementation scope.
- Defined active-to-resolved disposition transition and explicit completeness-label verification.
- Tightened audit/apply parity to full shared context and detailed result equality.
