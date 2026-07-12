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
- No closed parsed identity type exists for destructive cron ownership.
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

The canonical cron reconciler will authorize deletion only through a closed parsed identity contract and will accept a write only when the re-read crontab exactly equals the planned bytes, with CAS-guarded rollback for every mismatch.

---

## Design and Pseudocode

### 1. Closed semantic identity

The implementation will introduce one destructive identity schema, named `command_identity`, which represents an allowlisted normalized top-level shell command structure rather than an adjacent token fragment:

- `segments`: a non-empty ordered list of simple-command segments; each segment will declare its executable token, exact ordered argv, and allowed leading environment assignments;
- `operators`: the exact ordered top-level separators/control operators between segments (`;`, `&&`, `||`, or `|`); redirections will be parsed as structure rather than searched as strings;
- optional `cwd`: either the literal trusted `$WORKSPACE_HUB`/`${WORKSPACE_HUB}` token or a `machine-workspace-root` value resolved from the selected machine context/registry; basename-only matching will be forbidden;
- optional `catalog_task_id`: metadata used only to bind a selected legacy identity to a catalog task.

The parser will never execute or expand shell input. It will reject command substitution, backticks, nested `sh -c`/`bash -c` strings, functions, subshells, unsupported control grammar, malformed quoting, ambiguous/multiple working-directory changes, and any identity whose executable position cannot be proven. Thus `echo python task.py`, `printf '%s' 'python task.py'`, `other | python task.py`, and a matching token sequence on the wrong side of `&&`/`||` will not match an identity unless that entire operator/segment structure is explicitly allowlisted.

`command_contains`, `cwd_contains`, and `script_basename` may remain available only for non-destructive keep-verbatim classification. Schema validation will forbid `catalog_task_id` on any preservation row unless its fingerprint is a valid `command_identity`; this closes the future-promotion inverse, not only the current `notification-purge` fixture. Unknown keys, empty identities, unsupported grammar, arbitrary same-basename directories, or more than one matching catalog task will fail closed.

```text
parse_cron_command(line, trusted_machine_context):
    split the five cron schedule fields from the command without evaluating shell text
    lex punctuation and redirection tokens without expansion
    build a closed top-level list of simple-command segments and operators
    identify executable position after declared environment assignments
    resolve cwd only from trusted workspace tokens or the selected machine registry root
    reject nested strings, substitution, unsupported operators, and ambiguous cd
    return an immutable normalized command structure

matches_command_identity(parsed, identity):
    validate closed identity schema
    require exact normalized segments, executable positions, argv, operators, and cwd
    return true only when the whole allowlisted structure matches

classify_line_detail(...):
    keep comments/env/blank as ignore
    match non-destructive preservation fingerprints as keep-verbatim only
    match selected promotion only through command_identity
    match catalog-owned legacy lines only through command_identity
    never consult catalog substring keys for destructive ownership
    otherwise return uncataloged so cutover aborts
```

Canonical rendered tasks inside the managed marker block will remain structurally owned by the exact begin/end sentinels. Out-of-block legacy lines will be removable only when an explicit or deterministically catalog-derived `command_identity` matches the complete normalized top-level structure. Derivation will parse the rendered catalog command under the same closed grammar; tasks outside that grammar will require explicit allowlisted legacy structures or will fail closed. Collisions will abort rather than select a winner.

### 2. Catalog and selected-promotion migration

- `hermes-claude-bridge` and `repository-sync` will migrate from `command_contains` to complete normalized command structures plus trusted workspace-root identity.
- The `notification-purge` selected-promotion row will migrate to an explicit semantic structure covering the intended `find` executable/argv/operator chain plus trusted workspace-root identity.
- Non-fingerprinted catalog tasks will receive deterministic parsed identities from their rendered catalog command; the old `catalog_command_keys(...)->cmd in line` destructive fallback will be removed from the apply path.
- External/private and machine-local rows without `catalog_task_id` will remain keep-verbatim preservation rules even when their matching language is substring-based; they will never authorize deletion or replacement.

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

All exception results will be nonzero CLI outcomes except a verified exact ordinary apply. The implementation will never claim `applied` without an observed exact B and will never restore A without first observing a CAS value it owns.

### 4. Audit/apply parity

`scripts/cron/cron-audit.py` will consume the same parsed identity builder and classifier inputs as `cron_apply.py`. It will stop building destructive `catalog_commands` substring keys. Shared fixture tests will feed the same lines/context to both consumers and require identical `cataloged`, `preserved_external`, `ignore`, and `uncataloged` decisions. The audit will remain read-only.

### 5. Registry and enforcement

- The registry will replace the three substring destructive branches with parsed identities, remove `catalog-key-fallback`, set `post_write_exact_state_verify: true`, and add checker-owned attestations for parsed destructive identity, exact post-write equality, and verified rollback restoration.
- `scripts/cron/setup-cron.sh` and `scripts/setup/new-machine-setup.sh` will no longer copy `*legacy_current_user_operation`. The registry schema will represent each as a pure transitive delegation edge with `delegates_operation: {callee_path, operation_id}`. The checker will resolve that edge to `scripts/cron/cron_apply.py#reconcile-current-user-crontab`, require a source-attested literal/constant call path and flag propagation, and inherit the callee operation's authority and transaction status rather than duplicating stale substring/false transaction fields.
- Transitive delegation entries will be forbidden from declaring independent `authority_branches` or transaction booleans unless source discovery proves that the wrapper itself invokes a scheduler mutation primitive. A wrapper that gains such a primitive will fail closed as an unregistered direct owner instead of inheriting compliance.
- The enforcement checker will derive those claims from source/config and will continue to fail closed on missing branches, unsupported aliases, stale HTML, or self-disposition coordinates.
- The generated #3470 scheduler-safety HTML will be refreshed deterministically. Every `cron-catalog-migration` member will resolve to the same parsed-identity/exact-state direct-owner contract; no member may retain destructive substring authority or `post_write_exact_state_verify: false`. Only this group may advance to compliant; unrelated #3476–#3479 dispositions will remain migration-required.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/cron/cron_transaction.py` | Add closed parsed identity matching and remove destructive substring fallback |
| Modify | `scripts/cron/cron_apply.py` | Use semantic identities and exact post-write/rollback-restoration verification |
| Modify | `scripts/cron/cron-audit.py` | Consume the same semantic identity context and remove audit-side substring ownership |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | Migrate two installed identities to token-based schema |
| Modify | `config/workstations/harness-state-classes.yaml` | Migrate the selected notification-purge promotion identity |
| Modify | `config/scheduled-tasks/mutation-surfaces.yaml` | Record the new derived authority and transaction guarantees |
| Modify | `scripts/enforcement/scheduler_mutation_attestations.py` | Add closed source attestations required by the registry |
| Modify | `tests/cron/test_cron_transaction.py` | Add semantic identity/collision/grammar regressions |
| Modify | `tests/cron/test_cron_apply.py` | Add exact-state and rollback verification RED/GREEN cases |
| Modify | `tests/cron/test_cron_audit.py` | Prove audit/apply classification parity and retain read-only behavior |
| Modify | `tests/cron/test_setup_cron.py` | Preserve wrapper delegation and nonzero failure propagation |
| Modify | `tests/enforcement/test_scheduler_mutation_surfaces.py` | Prove registry/source/report transition without weakening other groups |
| Update | `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` | Refresh deterministic audit matrix |
| Update | `docs/ops/scheduled-tasks.md` | Document semantic destructive identity and exact-state failure handling |
| Update | `docs/plans/README.md` | Index this plan and reconcile completed #3470 state |

`scripts/cron/setup-cron.sh` and `scripts/setup/new-machine-setup.sh` are verification surfaces, not expected implementation edits. Any required behavior change in `new-machine-setup.sh` failure reporting will be deferred to [issue #3479](https://github.com/vamseeachanta/workspace-hub/issues/3479) unless a test proves #3475 cannot be made safe without it.

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
| `test_command_identity_rejects_unknown_or_substring_fields` | Destructive schema is closed | Validation error/fail closed |
| `test_command_identity_requires_executable_segment_and_exact_structure` | Tokens used as `echo`/`printf` data, wrong pipeline/control side, or nested shell strings cannot authorize deletion | Unrelated lines remain uncataloged |
| `test_command_identity_binds_trusted_workspace_root` | Trusted workspace token and selected-machine registry root work; arbitrary `/tmp/workspace-hub` and same-basename paths fail | Only intended legacy variants match |
| `test_malformed_or_ambiguous_shell_command_fails_closed` | Quoting, substitutions, nested shells, multiple `cd`, and unsupported grammar do not silently match | Uncataloged/explicit error |
| `test_catalog_key_substring_no_longer_deletes` | The old `cmd in line` route is absent | Collision aborts cutover |
| `test_selected_promotion_requires_semantic_identity` | `notification-purge` promotion cannot use `command_contains` | Exact variant cataloged; collisions not cataloged |
| `test_catalog_task_id_rejected_on_substring_preservation_identity` | Future metadata cannot reactivate destructive substring promotion | Config validation fails closed |
| `test_non_destructive_preservation_substrings_never_promote` | Keep-verbatim rows without catalog identity remain safe | Always `preserved_external` |
| `test_all_selected_cron_tasks_have_unique_destructive_identity` | Derived/explicit identities are non-empty and collision-free per machine context | No duplicate owner for fixture matrix |
| `test_audit_and_apply_share_semantic_classification` | Read-only audit and mutator cannot drift on ownership | Identical classifications for adversarial fixture matrix |
| `test_write_and_post_write_read_exception_contract` | Partial writes and indeterminate reads never claim success or blind-rollback | Exact state-machine statuses and nonzero CLI |
| `test_rollback_write_and_read_exception_contract` | Rollback exceptions preserve concurrent state and report verification truthfully | `rolled-back-with-write-error`, `rollback-failed`, `rollback-aborted`, or `rollback-indeterminate` as observed |
| `test_registry_advances_only_cron_catalog_group` | Checker derives new guarantees without waiving unrelated gaps | cron group compliant; #3476–#3479 remain migration-required |
| `test_transitive_cron_members_inherit_one_direct_owner_contract` | setup/onboarding wrappers cannot retain copied legacy authority/transaction fields | Both edges resolve to cron_apply operation; no substring/false exact-state member remains |
| `test_transitive_delegate_with_direct_primitive_fails_closed` | A wrapper cannot hide a new scheduler write behind inherited compliance | Discovery reports unregistered direct ownership |
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
- [ ] No destructive ownership branch will use substring matching. Complete normalized top-level command structure, exact marker ownership, or fail-closed unknown classification will be the only outcomes.
- [ ] Catalog-key substring fallback will be absent from the destructive apply path.
- [ ] `hermes-claude-bridge`, `repository-sync`, and selected `notification-purge` legacy identity will be migrated without broadening ownership or accepting arbitrary same-basename working directories.
- [ ] Audit and apply will share the semantic classifier and will produce identical ownership decisions for the same machine context.
- [ ] `catalog_task_id` will be invalid on substring-based preservation identities, preventing future promotion bypasses.
- [ ] Non-destructive external/local preservation rules will remain keep-verbatim and will not be treated as proof of destructive ownership.
- [ ] Ambiguous, malformed, colliding, or unknown live lines will abort before backup/write.
- [ ] Physical-local host binding, lock, exclusive fsynced backup, pre-write CAS, preservation behavior, rollback CAS, daemon guard, dry-run default, Windows skip, and transitive delegation will remain covered.
- [ ] The registry checker will derive compliance for the cron catalog group and will retain exact follow-up coordinates for [#3476](https://github.com/vamseeachanta/workspace-hub/issues/3476), [#3477](https://github.com/vamseeachanta/workspace-hub/issues/3477), [#3478](https://github.com/vamseeachanta/workspace-hub/issues/3478), and [#3479](https://github.com/vamseeachanta/workspace-hub/issues/3479).
- [ ] `setup-cron.sh` and `new-machine-setup.sh` registry rows will be attested pure delegation edges resolving to the direct-owner operation; they will carry no copied legacy substring branch or false exact-state transaction field, and any future direct primitive will fail discovery.
- [ ] Focused cron and enforcement suites, Ruff, shell syntax/ShellCheck where touched, deterministic HTML parity, and `scripts/legal/legal-sanity-scan.sh --diff-only` will pass.
- [ ] T3 code-stage adversarial review will complete before merge.
- [ ] A completeness record and HTML report will reach the configured threshold and await owner-only `status:completeness-verified` before closure.
- [ ] No test or verification command will read, write, or enumerate the live user crontab; no scheduler/process mutation or destructive cleanup will occur.

---

## Risks and Open Questions

- **Shell grammar risk:** a lexer is not a full shell parser. The implementation will accept only an explicit top-level simple-command/operator grammar, prove executable positions, and fail closed on nested or unsupported constructs rather than pretending to understand arbitrary shell.
- **Migration compatibility risk:** old absolute-path invocations may differ from catalog rendering. Only explicit semantic legacy identities will cover known variants; unknown variants will abort and require operator review.
- **Identity collision risk:** token sequences such as `python script.py` may be shared. Machine-context validation will require unique matches after optional exact cwd identity; ambiguity will block the cutover.
- **Preservation inversion risk:** converting every substring preservation row would conflate keep-verbatim recognition with destructive authority. This plan will migrate only rows that can promote to selected catalog ownership.
- **Rollback diagnostics risk:** full crontab content may contain sensitive command arguments. Results will use bounded hashes/counts and existing backup coordinates rather than embedding content.
- **Downstream dependency:** [issue #3476](https://github.com/vamseeachanta/workspace-hub/issues/3476) should consume this hardened transaction only after #3475 lands. #3477 and #3478 are independent backends; #3479 remains the failure-reporting follow-up.

No unresolved product decision blocks plan review. The supported grammar and legacy identity set remain correctness-critical review targets.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE | Fresh-clone trust dialog blocked non-interactive review |
| Codex | MAJOR | Required actual reproduction, full command-structure semantics, trusted cwd identity, audit/apply parity, exception state machine, and promotion-schema closure |
| Gemini | UNAVAILABLE | Non-interactive authentication was not configured |

**Overall result:** MAJOR — patched for focused r2 review; implementation remains blocked.

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
