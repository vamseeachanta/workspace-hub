# Plan for #3527: Reconcile scheduler inventory and detect post-merge drift

> **Status:** plan-approved — user approved amendment 2026-07-17
> **Complexity:** T3
> **Date:** 2026-07-14
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3527
> **Client:** N/A
> **Lane:** lane:claude
> **Original review artifacts:** `scripts/review/results/2026-07-14-plan-3527-claude.md` | `scripts/review/results/2026-07-14-plan-3527-codex.md` | `scripts/review/results/2026-07-14-plan-3527-gemini.md`
> **Amendment review artifacts:** `scripts/review/results/2026-07-17-plan-3527-amendment-codex.md` | `scripts/review/results/2026-07-17-plan-3527-amendment-claude.md` | `scripts/review/results/2026-07-17-plan-3527-amendment-gemini.md`

---

## 2026-07-17 Amendment: Cross-machine and staged-blob coherence

The amended implementation will close two defects found by adversarial code review on the Windows repair machine:

1. The cron inventory generator will use POSIX repository-path bytes. Render path flavor will follow the target machine/scheduler contract, never the host Python `os.name`: a Windows host previewing a Linux target such as `/mnt/local-analysis/workspace-hub` will emit the same command bytes as Linux; full-variant logs and `/tmp/workspace-hub-cron.log` will use `/`. A Windows target will retain its declared drive or UNC workspace spelling, but cron inventory will continue to select canonical Linux targets only.
2. Both generated-artifact checks will validate one captured Git index snapshot. The checker will capture a NUL-safe stage-0 manifest of Git path bytes and blob OIDs once, reject unmerged/multi-stage entries, and read exact OIDs thereafter. After successful capture, later index mutation will be irrelevant: execution will complete solely from immutable captured OIDs. Git object transport or materialization failure will return nonzero.

The original approval remains historical evidence for work already performed in the original seven-file scope. Removing its marker will pause all further #3527 implementation, including original-scope repairs, until the user approves the exact amended plan.

### Index-snapshot and path-classification contract

- `scripts/lib/git_index_snapshot.py` will own exact-OID reads, path classification, closure validation, and isolated materialization. Its bytes will be included in the cron inventory source union and scheduler report digest union, and every isolated tree will materialize the captured helper.
- The trusted bootstrap boundary will contain only installed Git/Python/uv and a literal platform command, not working-tree repository code. It will run `git write-tree` once to obtain an immutable tree OID, stream `scripts/lib/git_index_snapshot.py` from that tree OID into Python, and pass the same tree OID to the captured helper. The helper will then materialize and execute captured entrypoints and transitive closures. Working-tree launcher or helper divergence will be irrelevant because neither will execute.
- The final `all` coordinator mode will pass one tree OID to registry, inventory, and HTML validation. Landed CI will use the same single captured-helper `all` invocation against `HEAD^{tree}`; direct working-tree entrypoint commands will remain external-fixture-only.
- Before materialization, the helper will accept only regular Git modes `100644` and `100755` in each required closure; reject symlink/submodule/unknown modes, absolute or traversal paths, case-fold or Unicode-normalization collisions, Windows reserved names, and any non-descendant destination; and verify containment before writing a byte.
- Inventory `--check` with canonical default repo paths will materialize every transitive generator module, catalog, registry, state-class input, and staged output blob from the captured manifest into an isolated temporary tree. It will execute the captured generator there, compare against the captured output blob, and remove the tree on success or failure.
- Canonical default tracked paths always use captured blobs. Custom paths proven outside the repository remain filesystem-based. Any custom path resolving inside the repository—including canonical aliases, `..`, symlinks, case-folded Windows aliases, alternate separators, or same-basename aliases—will fail closed instead of changing modes.
- The exact lexical argument `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` will select tracked `--check-html` mode. An absolute spelling, symlink, `..` form, case variant, or alternate-separator spelling of that same in-repo file will fail as an alias. Proven external temporary outputs will remain filesystem-based.
- Tracked `--check-html` will materialize and execute the captured checker plus `scheduler_mutation_*` transitive Python closure, render from captured blobs, and compare with the captured report blob.
- The captured closure will include `pyproject.toml` and `uv.lock`. After stdlib-only bootstrap, the helper will run `uv sync --frozen` against the isolated captured project and execute children with that isolated environment plus Python `-I`; it will never resolve dependencies or imports from the original checkout. Both dependency files will join the relevant digest unions.
- Missing or staged-deleted required blobs, unmerged entries, Git transport truncation/failure, locked dependency failure, materialization failure, or cleanup failure will return nonzero.

The canonical Linux and Windows Git-Bash bootstrap will be this exact command. The helper bootstrap path will use Python's standard library only; dependency-bearing code will run only after isolated materialization.

```bash
set -euo pipefail
snapshot_helper="$(mktemp)"
snapshot_entry=""
cleanup_snapshot() {
    prior_status=$?
    trap - EXIT
    cleanup_status=0
    cleanup_targets=("$snapshot_helper")
    [[ -n "$snapshot_entry" ]] && cleanup_targets+=("$snapshot_entry")
    rm -f -- "${cleanup_targets[@]}" || cleanup_status=$?
    if (( prior_status != 0 )); then
        exit "$prior_status"
    fi
    exit "$cleanup_status"
}
trap cleanup_snapshot EXIT
snapshot_entry="$(mktemp)"
tree_oid="$(git write-tree)"
[[ "$tree_oid" =~ ^([0-9a-f]{40}|[0-9a-f]{64})$ ]]
helper_path="scripts/lib/git_index_snapshot.py"
git ls-tree -z "$tree_oid" -- "$helper_path" >"$snapshot_entry"
python -I -S - "$snapshot_entry" <<'PY'
from pathlib import Path
import sys
data = Path(sys.argv[1]).read_bytes()
if not data or not data.endswith(b"\0"):
    raise SystemExit(1)
PY
mapfile -d '' -t helper_entries <"$snapshot_entry"
[[ "${#helper_entries[@]}" -eq 1 ]]
helper_entry="${helper_entries[0]}"
helper_metadata="${helper_entry%%$'\t'*}"
helper_entry_path="${helper_entry#*$'\t'}"
[[ "$helper_entry_path" == "$helper_path" ]]
[[ "$helper_metadata" =~ ^(100644|100755)\ blob\ ([0-9a-f]{40}|[0-9a-f]{64})$ ]]
helper_oid="${BASH_REMATCH[2]}"
git cat-file blob "$helper_oid" >"$snapshot_helper"
[[ -s "$snapshot_helper" ]]
[[ "$(git hash-object "$snapshot_helper")" == "$helper_oid" ]]
python -I -S "$snapshot_helper" --tree-oid "$tree_oid" all
```

`all` will be a subcommand of `scripts/lib/git_index_snapshot.py`. It will pass the single supplied tree OID to registry, inventory, and HTML validation and will never call `git write-tree` itself. The bootstrap will require a nonempty NUL-terminated `ls-tree -z` frame and reject missing, truncated, duplicate, malformed, symlink (`120000`), submodule (`160000`), tree, or non-regular helper entries before `cat-file` or Python execution. Shell failure propagation and `cleanup_snapshot` will preserve a prior validation failure and upgrade successful validation to nonzero when cleanup fails. Command-level tests will execute this literal contract on Linux and Windows Git Bash and assert exactly one `git write-tree` call.

| Captured index | Working tree | Expected tracked check |
|---|---|---|
| staged input changed, staged output stale | output correct | FAIL |
| staged input old, staged output incorrectly advanced | output old/correct | FAIL |
| staged input and output coherent | non-launcher/helper bytes divergent | PASS; unstaged bytes ignored |
| required output missing/deleted or any entry unmerged | any | FAIL CLOSED |
| index changes after manifest capture | any | complete from the already captured immutable OIDs |

Ordinary local final validation and landed-main validation will each use one captured-helper `all` invocation. External fixture checks alone may invoke filesystem entrypoints directly.

Local `git write-tree` may create an unreachable tree object, but it will not change refs, the index, the working tree, or external scheduler state; normal Git maintenance may collect that object. Landed-main validation will use `HEAD^{tree}` and will not call `git write-tree`.

### Amendment tasks

- [ ] Add RED Windows-equivalence tests for POSIX repository digest bytes and exact render fixtures: Linux target `/mnt/local-analysis/workspace-hub` with full log `/mnt/local-analysis/workspace-hub/logs/quality/cron-wrapper.log`; contribute log `/tmp/workspace-hub-cron.log`; preview-only Windows target `D:\workspace-hub` with full log `D:\workspace-hub/logs/quality/cron-wrapper.log`; and UNC target `\\server\share\workspace-hub` with the same `/logs/...` suffix. Windows targets will remain preview-only because cron installation is not authorized there.
- [ ] Add separate RED cases for staged source stale/correct, staged output stale/correct, missing/deleted output, unmerged index, post-capture mutation, and external same-basename/alias handling for both artifact chains.
- [ ] Implement `scripts/lib/git_index_snapshot.py` as the NUL-safe stage-0 path/OID manifest and exact-OID reader shared by tracked checks; bind it into both digest unions and forbid path-based index re-reads after capture.
- [ ] Add literal Git/Python bootstrap commands that capture one tree OID and stream the helper from that OID; materialize and execute captured inventory/HTML entrypoints plus complete transitive closures without importing working-tree repository code.
- [ ] Add `all` coordinator mode, regular-mode/path/collision/containment validation, and cleanup-on-every-exit tests; preserve proven external filesystem fixture behavior.
- [ ] Regenerate inventory, provenance binding, and scheduler HTML only after all implementation and tests reach final staged bytes.
- [ ] Rerun the focused 131-test cross-machine/scheduler suite, legal scan, and T3 adversarial code review after rebasing onto current `origin/main`.

The RED checkpoint will run:

```text
uv run pytest tests/cron/test_cron_identity_inventory.py tests/cron/test_cron_render.py -q
uv run pytest tests/enforcement/test_scheduler_mutation_delivery.py -k "captured_staged" -q
uv run pytest tests/cron/test_cron_identity_inventory.py -k "captured_staged" -q
uv run pytest tests/cron/test_cron_identity_inventory.py -k "bootstrap or materialization or coordinator or locked_dependency or host_python" -q
```

The named tests will be written before these commands run. RED will require assertion failures with tests collected; exit 5/no-tests-collected will not count. Before implementation, the first command will expose host-dependent path/log bytes on Windows; the captured-staged selections will expose mixed snapshots; and the last command will expose working-code bootstrap, unsafe materialization, and multi-capture coordinator defects.

---

## Resource Intelligence Summary

### Existing repo code

- `.github/workflows/enforcement-gate.yml` will remain the PR gate; its scheduler job currently runs only for `pull_request` events, so it cannot validate the landed `main` tree.
- `scripts/cron/build-cron-identity-inventory.py` deterministically derives the inventory from the catalog, workstation registry, harness state classes, and cron implementation modules.
- `scripts/enforcement/scheduler_mutation_contract.py` defines the scheduler report digest union. The new post-merge workflow will need to join that union or its drift could evade the report.
- `tests/enforcement/test_scheduler_mutation_delivery.py` already owns workflow, digest-union, and deterministic-report delivery contracts; new RED coverage will stay there.
- `scripts/operations/merge-when-clean.sh` already waits through `UNKNOWN`, `BLOCKED`, and `BEHIND` until `CLEAN`, and refuses `DIRTY`; `.claude/rules/merge-authorization.md` does not yet require that helper or landed-tree domain revalidation. Without strict required checks, observing `CLEAN` is a best available landing discipline rather than atomic latest-base protection.

### Standards

| Standard | Status | Source |
|---|---|---|
| Scheduler mutation safety | applicable; fail-closed validation required | `.claude/rules/scheduler-mutation-safety.md` |
| Merge authorization | gap; CLEAN/helper/landed-tree requirements are incomplete | `.claude/rules/merge-authorization.md` |
| TDD and user approval | mandatory | `AGENTS.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md` |

### LLM Wiki pages consulted

- No relevant wiki pages apply; this is repository CI/governance work.

### Documents consulted

- [Issue #3527](https://github.com/vamseeachanta/workspace-hub/issues/3527) defines the incident and prohibits live cron/daemon mutation.
- `docs/plans/2026-07-11-issue-3475-cron-semantic-ownership.md` defines the inventory, resolved-disposition source digest, dependent HTML, and three-check verification chain.
- `docs/plans/2026-05-06-issue-2551-security-audit-public-repos-branch-protection.md` supplies the branch/ruleset audit baseline but explicitly routes protection changes to follow-up work.
- [Issue #3534](https://github.com/vamseeachanta/workspace-hub/issues/3534) will own the separately planned owner/admin rollout of strict latest-base required checks and direct-push protection.
- GitHub repository API evidence shows classic `main` protection is absent (HTTP 404) and the active ruleset contains deletion/non-fast-forward rules but no required status checks.
- Drive-file index search for `scheduler identity inventory merge race generated artifact` queried six indexes on 2026-07-14. Returned documents are unrelated engineering/project files; no relevant drive files will be used.
- `.claude/memory/topics/feedback_strict_uptodate_ruleset_no_admin_bypass.md` and `.claude/memory/topics/feedback_verify_generated_state_against_origin_not_working_copy.md` already encode related lessons. A separate [#3532](https://github.com/vamseeachanta/workspace-hub/issues/3532) will repair cross-provider retrieval rather than duplicate memory prose here.

### Gaps identified

- No workflow validates scheduler generated-state coherence after a push lands on `main`.
- The new workflow is not in the scheduler report digest union.
- Merge authorization does not require the existing CLEAN-only helper or post-merge domain checks.
- Current generated inventory, resolved-disposition source digest, and HTML are stale on `origin/main`.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-14):

- [#3527](https://github.com/vamseeachanta/workspace-hub/issues/3527) — OPEN, `status:needs-plan`, `lane:claude`.
- [#2551](https://github.com/vamseeachanta/workspace-hub/issues/2551) — OPEN, `status:plan-approved`; audits branch/ruleset protection and requires separate implementation follow-ups.
- [#3534](https://github.com/vamseeachanta/workspace-hub/issues/3534) — OPEN, `status:needs-plan`; owns strict latest-base/direct-push protection rollout.
- [#3532](https://github.com/vamseeachanta/workspace-hub/issues/3532) — OPEN, `status:needs-plan`; owns cross-provider memory budget allocation.

**Merge-race proof:** PR #3517 checks used synthetic merge `4dd33921ad48032e6724aca7720dacd46431f72a` with base `2cd741f8`. The actual merge `26c19cbb3b03abdd5180760adc16ab29b182a912` used first parent `5980b3063`, which changed `config/scheduled-tasks/schedule-tasks.yaml` 24 seconds before merge. The three intervening commits have zero associated PRs.

**Digest proof:** a current-main regeneration yields `106d1d1b6cd4758ed42060292bed6fc1fd57711eab887fe84caf3ec41f4785a3`; the tracked inventory carries `d5b4fbc4508bf58d8ce0b4c47186204be298bf2586e93b5ab19f375f465b07fb`. Parsed JSON objects are equal after removing `input_digest`.

**Historical reproduction proofs** (fresh `origin/main` `03cc01e0ca4793b7208d449b7310d6a47bd3fe9a`, 2026-07-14; issue/label state below is historical):

```text
$ uv run pytest tests/enforcement/test_scheduler_mutation_task3.py -q
3 failed, 86 passed in 55.97s
AssertionError: ['identity inventory input digest is stale'] == []

$ uv run python scripts/cron/build-cron-identity-inventory.py --check
ERROR: stale identity inventory: docs/reports/issue-3475-command-identity-inventory.json

$ uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py
ERROR: identity inventory input digest is stale
```

Failure mode observed matches issue claim: **YES**.

**Amendment evidence (2026-07-17, Windows):** the initial repair produced 2 failures in the 131-test focused suite because `$LOG` used host-native `\\`; both adversarial code reviews also proved that working-tree-correct/staged-stale HTML and inventory states could pass their standalone checks. The amended plan will treat these as RED requirements, not as baseline exceptions.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-14-issue-3527-postmerge-inventory-race.md` |
| Human-readable plan | `docs/plans/2026-07-14-issue-3527-postmerge-inventory-race.html` |
| Post-merge detector | `.github/workflows/scheduler-mutation-main.yml` |
| Delivery tests | `tests/enforcement/test_scheduler_mutation_delivery.py` |
| Digest-union contract | `scripts/enforcement/scheduler_mutation_contract.py` |
| Captured-index helper | `scripts/lib/git_index_snapshot.py` |
| Tracked HTML checker | `scripts/enforcement/check-scheduler-mutation-surfaces.py` |
| Inventory generator/checker | `scripts/cron/build-cron-identity-inventory.py` |
| Cross-target renderer | `scripts/cron/cron_render.py` |
| Inventory equivalence/index tests | `tests/cron/test_cron_identity_inventory.py` |
| Cross-target renderer tests | `tests/cron/test_cron_render.py` |
| Merge rule | `.claude/rules/merge-authorization.md` |
| Generated inventory | `docs/reports/issue-3475-command-identity-inventory.json` |
| Registry source binding | `config/scheduled-tasks/mutation-surfaces.yaml` |
| Generated audit | `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` |

---

## Deliverable

`main` will regain scheduler generated-state coherence, every future push to `main` will run the three scheduler coherence checks, and merge closeout will require CLEAN-only merging plus validation of the actual landed tree.

---

## Pseudocode

```text
on every landed push to main (immutable checkout; working tree equals HEAD):
    checkout the landed commit with full history
    install Python 3.12
    run the canonical bootstrap above as one shell step, replacing only:
        tree_oid="$(git rev-parse 'HEAD^{tree}')"
    captured helper validates its own regular mode/OID and runs all once
    fail the workflow if bootstrap, any child, or cleanup fails

when computing scheduler report digest union:
    include the PR enforcement workflow
    include the main-push scheduler workflow
    include the delivery tests and existing contract inputs

when validating a tracked generated artifact:
    installed Git writes one immutable index tree OID
    installed Git streams git_index_snapshot.py from that tree OID into installed Python
    captured helper reads the tree manifest and exact blobs from the same tree OID
    reject unmerged, missing, deleted, duplicated, or malformed entries
    reject non-regular modes, unsafe/reserved paths, collisions, and non-descendants
    read every tracked input and output by captured blob OID
    if validating inventory:
        materialize all captured transitive modules and inputs in a temporary tree
        execute the captured generator inside that tree
        compare generated bytes with the captured inventory blob
        remove the temporary tree on every exit; cleanup failure is fatal
    if validating scheduler HTML:
        materialize the captured checker and complete scheduler_mutation helper closure
        execute captured checker code, render from captured blobs, compare captured HTML blob
    ignore divergent working-tree bytes for tracked paths
    ignore later index mutation and finish exclusively from captured immutable OIDs

when regenerating in dependency order:
    stage final runtime, test, rule, and workflow sources
    generate and stage inventory (inventory output is excluded from its own digest)
    copy its digest into the registry and stage the registry
    render and stage scheduler HTML (HTML output is excluded from its render digest)
    run all checks against one newly captured final index snapshot

when merging an authorized PR:
    require mergeStateStatus CLEAN
    call merge-when-clean.sh --merge
    fetch the actual origin/main commit
    rerun changed-domain generated-artifact checks before issue close
```

---

## Implementation Tasks

### Task 1: Add RED delivery and merge-policy contracts

**Files:** modify `tests/enforcement/test_scheduler_mutation_delivery.py`.

- [ ] Add a test that will require `.github/workflows/scheduler-mutation-main.yml` to trigger on every `push` to `main` without a path filter.
- [ ] Require checkout depth 0, Python 3.12, uv, and one exact fail-closed captured-helper `all` bootstrap; reject `continue-on-error`, `|| true`, and `set +e`.
- [ ] Extend the digest-union test so mutations to either scheduler workflow will change the report digest.
- [ ] Add a merge-rule assertion that will require `mergeStateStatus==CLEAN`, `scripts/operations/merge-when-clean.sh --merge`, fetch of actual `origin/main`, and changed-domain post-merge validation.
- [ ] Run only the new tests and record the expected RED failures for the missing workflow/digest/rule clauses.

### Task 2: Implement the post-merge detector and durable rule

**Files:** create `.github/workflows/scheduler-mutation-main.yml`; modify `scripts/enforcement/scheduler_mutation_contract.py` and `.claude/rules/merge-authorization.md`.

- [ ] Add the `push: branches: [main]` workflow with the exact captured-helper `all` check and no event fields that require a PR payload.
- [ ] Add the workflow to `digest_record_union()` so audit regeneration is mandatory after detector changes.
- [ ] Tighten merge authorization so explicit user authorization will not waive CLEAN state, the existing merge helper will be mandatory, and the actual landed tree will be revalidated before close.
- [ ] Run the Task 1 tests and require GREEN before generated files change.

### Task 3: Reconcile generated state in dependency order

**Files:** update `docs/reports/issue-3475-command-identity-inventory.json`, `config/scheduled-tasks/mutation-surfaces.yaml`, and `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html`.

- [ ] Regenerate the inventory from the implementation branch after Tasks 1–2 are complete.
- [ ] Copy the resulting inventory `input_digest` into only the #3475 `resolved_dispositions[].source_digest` field.
- [ ] Regenerate the scheduler HTML after the inventory, registry, workflow, test, and contract reach final bytes. The merge rule is intentionally outside the scheduler report digest union.
- [ ] Prove the inventory differs from the previous artifact only in fields deterministically affected by the declared input union; unexpected identity/collision changes will stop implementation for review.

### Task 4: Verify, review, and land without repeating the race

- [ ] Run focused delivery and Task 3 suites, the inventory check, scheduler guard, and HTML check.
- [ ] Run the legal scan and any workflow syntax validation available in the repo.
- [ ] Obtain adversarial code/artifact review at T3 depth with no unresolved MAJOR findings; document provider unavailability under the degradation convention.
- [ ] Use `scripts/operations/merge-when-clean.sh --merge` only after the user explicitly authorizes that PR merge.
- [ ] Fetch actual `origin/main` and rerun the focused suite plus all three scheduler checks on the landed commit before completeness/closeout.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `.github/workflows/scheduler-mutation-main.yml` | Detect incoherent generated scheduler state on the actual landed commit |
| Modify | `tests/enforcement/test_scheduler_mutation_delivery.py` | Add RED workflow, digest, and merge-rule contracts |
| Modify | `scripts/enforcement/scheduler_mutation_contract.py` | Bind the new detector into the audit digest |
| Create | `scripts/lib/git_index_snapshot.py` | Capture the stage-0 path/OID manifest, classify paths, read exact blobs, and materialize isolated trees |
| Modify | `scripts/enforcement/check-scheduler-mutation-surfaces.py` | Compare tracked HTML against its staged blob during index validation |
| Modify | `scripts/cron/build-cron-identity-inventory.py` | Use POSIX logical path bytes and provide index-coherent `--check` behavior |
| Modify | `scripts/cron/cron_render.py` | Preserve canonical POSIX Linux render paths and shell log separators on Windows |
| Modify | `tests/cron/test_cron_identity_inventory.py` | Add cross-machine digest, identity, and staged-snapshot RED contracts |
| Modify | `tests/cron/test_cron_render.py` | Bind POSIX shell-log rendering on Windows and native workspace spelling |
| Modify | `.claude/rules/merge-authorization.md` | Require CLEAN helper-based merge and landed-tree checks |
| Regenerate | `docs/reports/issue-3475-command-identity-inventory.json` | Reconcile current declared input digest |
| Modify | `config/scheduled-tasks/mutation-surfaces.yaml` | Rebind resolved #3475 provenance to the regenerated inventory |
| Regenerate | `docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` | Reconcile the final digest union |
| Update | `docs/plans/README.md` | Index this plan |

No live cron, crontab, daemon, systemd timer, or scheduled-task mutation will occur.

---

## TDD Test List

| Test name | What it will verify | Expected RED | Expected GREEN |
|---|---|---|---|
| `test_main_push_scheduler_workflow_is_fail_closed` | landed `main` receives one captured-tree coordinator check | workflow missing | exact trigger/bootstrap/`all` command passes |
| `test_delivery_contract_is_in_digest_union` (extend) | both scheduler workflows affect report digest | new workflow absent from union | either workflow mutation changes digest |
| `test_merge_rule_requires_clean_helper_and_landed_validation` | user authorization cannot bypass freshness/closeout | required clauses absent | all clauses present |
| `test_input_digest_uses_posix_repository_paths` | repository logical names are host invariant | Windows backslashes change digest | POSIX logical bytes on all hosts |
| `test_inventory_uses_registry_workspace_not_checkout_environment` | Linux preview identities are host invariant | Windows path semantics change hashes | Linux canonical hash matches on Windows/Linux |
| `test_render_logs_follow_target_scheduler_path_contract` | full and contribute logs use scheduler-safe separators | Windows host injects `\\` | full log and `/tmp` bytes match Linux fixtures; Windows workspace spelling remains declared |
| `test_check_html_uses_captured_staged_blobs` | source/output mismatch matrix, missing/deleted output, unmerged state, and aliases fail closed; later index mutation cannot alter the result | mixed state passes | coherent captured tree passes regardless of working-tree divergence |
| `test_inventory_check_uses_captured_staged_tree` | transitive Python, inputs, and output execute from one snapshot with the same fail-closed matrix | working-tree imports hide staged drift | isolated captured execution and exact output comparison |
| `test_bootstrap_ignores_working_entrypoint_and_helper` | working-tree repository code cannot control capture or validation | mutable helper/entrypoint executes before isolation | both divergence directions produce the captured-tree result |
| `test_materialization_rejects_unsafe_modes_paths_and_collisions` | temp tree cannot escape or alias on Windows/Linux | unsafe Git entries materialize | modes, traversal, reserved names, collisions, and non-descendants fail before writes |
| `test_bootstrap_rejects_non_regular_helper_before_execution` | helper trust starts only after installed Git verifies its complete frame | valid-Python symlink or unterminated record executes | empty/unterminated/duplicate/120000/160000/wrong-type entries fail before `cat-file`/Python |
| `test_post_capture_index_mutation_uses_captured_oids` | later index changes cannot mix the snapshot | path re-read changes behavior | result derives only from originally captured OIDs |
| `test_all_coordinator_passes_one_tree_oid_to_every_child` | final local validation cannot recapture between registry/inventory/HTML | children capture independently | one `git write-tree`; identical OID; any child failure returns nonzero |
| `test_git_bash_bootstrap_propagates_transport_and_cleanup_failures` | literal bootstrap is portable and fail closed | allocation/empty/truncated/helper/Python/cleanup failures can pass | Linux and Windows Git Bash tests include second-`mktemp` and cleanup failure |
| `test_bootstrap_and_children_ignore_host_python_customization` | original checkout/environment cannot inject code | `sitecustomize`, `PYTHONPATH`, or `.pth` executes | `-I -S` bootstrap and isolated locked child environment ignore hostile fixtures |
| `test_all_materializes_locked_dependency_project` | PyYAML children execute reproducibly without checkout imports | plain Python lacks dependency or uv reads working project | captured `pyproject.toml`/`uv.lock`, frozen sync, isolated child Python |
| existing `test_cron_authority_is_exact_and_3475_is_resolved` | current inventory digest is coherent | stale digest | no validation errors |
| existing `test_transitive_surfaces_are_closed_delegations_with_visible_gaps` | delegation contract stays intact | stale digest | no validation errors |
| existing `test_renderer_supports_delegate_rows_and_preserves_migration_issues` | report remains deterministic and complete | stale digest | no validation errors |

---

## Acceptance Criteria

- [ ] `uv run pytest tests/enforcement/test_scheduler_mutation_delivery.py tests/enforcement/test_scheduler_mutation_task3.py -q` passes.
- [ ] The exact Git-Bash bootstrap block above exits 0 in `all` mode locally, calls `git write-tree` exactly once, and passes one tree OID to registry, inventory, and HTML child validation with nonzero child-exit aggregation.
- [ ] On immutable landed-main, one shell step runs the same helper mode/type/OID/hash bootstrap with `git rev-parse 'HEAD^{tree}'` substituted for `git write-tree`, invokes captured-helper `all` once using installed Python (not `uv`), and propagates child/cleanup failure.
- [ ] The new workflow runs on unfiltered pushes to `main`, resolves immutable `HEAD^{tree}`, changes no refs/index/worktree/external scheduler state, and is digest-bound. Local final validation may create an unreachable `git write-tree` object but no durable Git state.
- [ ] Merge policy requires CLEAN state, the existing merge helper, and actual-landed-tree validation.
- [ ] Current scheduler identity rows, collisions, and unsupported entries do not change unexpectedly.
- [ ] `scripts/legal/legal-sanity-scan.sh --diff-only` passes.
- [ ] `uv run pytest tests/cron/test_cron_identity_inventory.py tests/cron/test_cron_render.py tests/enforcement/test_scheduler_mutation_delivery.py tests/enforcement/test_scheduler_mutation_task3.py -q` passes on Windows (131 or more tests).
- [ ] The same canonical Linux-target fixtures and focused suite pass on Linux CI; Windows-target drive and UNC fixtures pass without depending on the host OS.
- [ ] For both artifact chains, staged source/output incoherence fails even when working bytes are correct; a coherent captured index passes even when working bytes diverge.
- [ ] Missing/deleted outputs, unmerged entries, unsafe modes/paths/collisions, Git/materialization/cleanup failure, and tracked-path alias ambiguity fail closed.
- [ ] Working-tree entrypoint/helper divergence does not affect tracked results because no working repository code executes before captured re-exec.
- [ ] Hostile `PYTHONPATH`, working-tree `sitecustomize.py`, `usercustomize.py`, and project `.pth` fixtures cannot execute before bootstrap or influence isolated captured children.
- [ ] Captured `pyproject.toml` and `uv.lock` drive `uv sync --frozen` in the isolated tree; dependency resolution never reads the original checkout.
- [ ] Post-capture index mutation does not affect the result; exact captured OIDs remain authoritative.
- [ ] Custom external fixture paths remain filesystem-based and cannot be mistaken for tracked aliases.
- [ ] `scripts/lib/git_index_snapshot.py`, `pyproject.toml`, and `uv.lock` are present in the inventory `SOURCE_PATHS`/dependency closure and scheduler `digest_record_union()` as applicable; mutating captured helper/dependency bytes changes declared digests.
- [ ] The regenerated identity rows match canonical Linux `main`; only declared digest/provenance fields may change.
- [ ] Adversarial code/artifact reviews have no unresolved MAJOR findings.
- [ ] A post-merge run on the actual landed `origin/main` commit passes before issue close.
- [ ] No live scheduler state changes.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| 2026-07-14 Claude | UNAVAILABLE | Original seven-file detector review only; superseded for amendment scope. |
| 2026-07-14 Codex | APPROVE | Original seven-file detector review only; does not approve amendment scope. |
| 2026-07-14 Gemini | UNAVAILABLE | Original review unavailable. |
| 2026-07-17 Codex amendment r1 | MAJOR | Required captured path/OID manifest, complete mismatch matrix, exact tracked-path classification, acyclic regeneration, target-based path semantics, and gate rollback. |
| 2026-07-17 Claude amendment r1 | MAJOR | Required consistent index truth table, isolated staged generator execution, explicit cross-target examples, rollback, and removal of stale PASS state. |
| 2026-07-17 Codex amendment r2 | MAJOR | Required launcher boundary, named digest-bound helper, explicit path precedence, durable gate rollback, and T3 classification. |
| 2026-07-17 Claude amendment r2 | MAJOR | Required captured HTML code execution, deterministic post-capture behavior, literal fixtures, narrow rollback, and collected-test RED evidence. |
| 2026-07-17 Codex amendment r3 | MAJOR | Required non-self-referential installed-tool bootstrap, uniform T3 governance, third-provider evidence, and suspension of further work. |
| 2026-07-17 Claude amendment r3 | MAJOR | Required safe helper bootstrap, consistent immutable-OID tests, and amendment rollback preserving the durable main guard. |
| 2026-07-17 Gemini amendment r4 | UNAVAILABLE | CLI 0.51.0 exited 41 because no auth method was configured; degradation evidence is preserved. |
| 2026-07-17 Codex amendment r4 | MAJOR | Required literal bootstrap, owned coordinator/acceptance, truthful object-creation semantics, live gate rollback, and final synthesis. |
| 2026-07-17 Claude amendment r4 | MAJOR | Required one executable staged-local boundary and RED bootstrap/coordinator/materialization coverage. |
| 2026-07-17 Codex amendment r5 | MAJOR | Required helper mode/type validation before execution, cleanup propagation, exact landed tree commands, and gate/synthesis closeout. |
| 2026-07-17 Claude amendment r5 | MAJOR | Independently proved cleanup-success masking and pre-validation symlink-helper execution. |
| 2026-07-17 Codex amendment r6 | MAJOR | Required immediate cleanup trap, complete NUL frame, captured landed helper, exact OID lengths, and gate/synthesis closeout. |
| 2026-07-17 Claude amendment r6 | MAJOR | Independently required second-allocation cleanup, final-NUL rejection, and captured landed execution. |
| 2026-07-17 Codex amendment r7 | MAJOR | Required isolated Python startup, one captured landed `all`, consistent child scope, and live gate rollback. |
| 2026-07-17 Claude amendment r7 | MAJOR | Required one workflow shape and captured locked dependencies for PyYAML children. |

**Overall amendment result:** USER DISPOSITION — review cap reached after concordant MAJOR verdicts through r7 and Gemini was unavailable. Final inline revision absorbed r7 findings; the user explicitly accepted this disclosed review posture and applied `status:plan-approved` on 2026-07-17. TDD implementation is authorized; code-stage T3 review remains mandatory.

Revisions made after round 1:

- Filed [#3534](https://github.com/vamseeachanta/workspace-hub/issues/3534) as the concrete owner/admin protection rollout and restored #2551 to audit-only ownership.
- Corrected the helper contract to wait for CLEAN and refuse DIRTY, without claiming atomic protection.
- Removed the false claim that merge-rule bytes participate in the scheduler report digest.

---

## Risks and Open Questions

- **Broken-main window:** the new workflow will detect but cannot atomically prevent a bad merge. [#3534](https://github.com/vamseeachanta/workspace-hub/issues/3534) will own separately approved strict required-check/ruleset rollout and direct-push policy; [#2551](https://github.com/vamseeachanta/workspace-hub/issues/2551) remains its audit baseline.
- **Workflow visibility:** a failing post-merge check needs operational monitoring. The implementation issue will remain open until the actual landed run is observed.
- **Digest coupling:** delivery-test, scheduler-workflow, contract, registry, and report bytes intentionally affect deterministic output. The merge authorization rule is enforced by its delivery assertion but is not part of the scheduler report digest. Regeneration will happen last.
- **Self-blocking risk:** the workflow and tests will be checked against their own guard patterns; no blanket file exemption will be introduced.
- **Main churn:** landing will use the CLEAN-only helper and actual landed-tree revalidation; stale synthetic-merge evidence will not be accepted.

---

## Rollback

- Amendment rollback will preserve the original `.github/workflows/scheduler-mutation-main.yml`, CLEAN merge rule, and main-workflow scheduler digest binding. Removing that landed-main detector would recreate the original incident and will require a separately approved emergency action plus explicit broken-main monitoring.
- The snapshot helper, its two digest-union bindings, renderer normalization, captured checker/generator behavior, and amendment tests will be reverted as one transaction; no orphan helper/binding and no partial runtime-only or generated-only rollback will be allowed.
- After reverting amendment source bytes, rollback will regenerate and stage the inventory, copy its digest into the #3475 registry binding, regenerate and stage scheduler HTML, and run the exact `all` bootstrap block so registry, inventory, and HTML receive one captured tree OID. Landed verification will repeat captured-helper `all` against `HEAD^{tree}`.
- Rollback will verify that identity rows again match the declared canonical fixture and that no live cron, crontab, daemon, systemd timer, or Windows scheduled task was mutated.

---

## Complexity: T3

Fourteen implementation surfaces form one systemic scheduler-coherence chain, including security-sensitive staged-index execution and cross-target path rendering. T3 requires three-provider plan and code review; provider unavailability will be documented under the established degradation rule rather than silently reducing review depth.
