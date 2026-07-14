# Plan for #3527: Reconcile scheduler inventory and detect post-merge drift

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-07-14
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3527
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** `scripts/review/results/2026-07-14-plan-3527-claude.md` | `scripts/review/results/2026-07-14-plan-3527-codex.md` | `scripts/review/results/2026-07-14-plan-3527-gemini.md`

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

**Reproduction proofs** (fresh `origin/main` `03cc01e0ca4793b7208d449b7310d6a47bd3fe9a`, 2026-07-14):

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

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-14-issue-3527-postmerge-inventory-race.md` |
| Human-readable plan | `docs/plans/2026-07-14-issue-3527-postmerge-inventory-race.html` |
| Post-merge detector | `.github/workflows/scheduler-mutation-main.yml` |
| Delivery tests | `tests/enforcement/test_scheduler_mutation_delivery.py` |
| Digest-union contract | `scripts/enforcement/scheduler_mutation_contract.py` |
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
on every push to main:
    checkout the landed commit with full history
    install Python 3.12 and uv
    run scheduler mutation registry validation
    run exact cron identity inventory --check
    run deterministic scheduler HTML --check-html
    fail the workflow if any command fails

when computing scheduler report digest union:
    include the PR enforcement workflow
    include the main-push scheduler workflow
    include the delivery tests and existing contract inputs

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
- [ ] Require checkout depth 0, Python 3.12, uv, and the exact three fail-closed commands; reject `continue-on-error`, `|| true`, and `set +e`.
- [ ] Extend the digest-union test so mutations to either scheduler workflow will change the report digest.
- [ ] Add a merge-rule assertion that will require `mergeStateStatus==CLEAN`, `scripts/operations/merge-when-clean.sh --merge`, fetch of actual `origin/main`, and changed-domain post-merge validation.
- [ ] Run only the new tests and record the expected RED failures for the missing workflow/digest/rule clauses.

### Task 2: Implement the post-merge detector and durable rule

**Files:** create `.github/workflows/scheduler-mutation-main.yml`; modify `scripts/enforcement/scheduler_mutation_contract.py` and `.claude/rules/merge-authorization.md`.

- [ ] Add the non-mutating `push: branches: [main]` workflow with the exact three checks and no event fields that require a PR payload.
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
- [ ] Obtain adversarial code/artifact review at T2 depth with no unresolved MAJOR findings.
- [ ] Use `scripts/operations/merge-when-clean.sh --merge` only after the user explicitly authorizes that PR merge.
- [ ] Fetch actual `origin/main` and rerun the focused suite plus all three scheduler checks on the landed commit before completeness/closeout.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `.github/workflows/scheduler-mutation-main.yml` | Detect incoherent generated scheduler state on the actual landed commit |
| Modify | `tests/enforcement/test_scheduler_mutation_delivery.py` | Add RED workflow, digest, and merge-rule contracts |
| Modify | `scripts/enforcement/scheduler_mutation_contract.py` | Bind the new detector into the audit digest |
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
| `test_main_push_scheduler_workflow_is_fail_closed` | landed `main` receives all three checks | workflow missing | exact trigger/setup/commands pass |
| `test_delivery_contract_is_in_digest_union` (extend) | both scheduler workflows affect report digest | new workflow absent from union | either workflow mutation changes digest |
| `test_merge_rule_requires_clean_helper_and_landed_validation` | user authorization cannot bypass freshness/closeout | required clauses absent | all clauses present |
| existing `test_cron_authority_is_exact_and_3475_is_resolved` | current inventory digest is coherent | stale digest | no validation errors |
| existing `test_transitive_surfaces_are_closed_delegations_with_visible_gaps` | delegation contract stays intact | stale digest | no validation errors |
| existing `test_renderer_supports_delegate_rows_and_preserves_migration_issues` | report remains deterministic and complete | stale digest | no validation errors |

---

## Acceptance Criteria

- [ ] `uv run pytest tests/enforcement/test_scheduler_mutation_delivery.py tests/enforcement/test_scheduler_mutation_task3.py -q` passes.
- [ ] `uv run python scripts/cron/build-cron-identity-inventory.py --check` exits 0.
- [ ] `uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py` exits 0.
- [ ] `uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py --check-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html` exits 0.
- [ ] The new workflow runs on unfiltered pushes to `main`, contains no mutating command, and is digest-bound.
- [ ] Merge policy requires CLEAN state, the existing merge helper, and actual-landed-tree validation.
- [ ] Current scheduler identity rows, collisions, and unsupported entries do not change unexpectedly.
- [ ] `scripts/legal/legal-sanity-scan.sh --diff-only` passes.
- [ ] Adversarial code/artifact reviews have no unresolved MAJOR findings.
- [ ] A post-merge run on the actual landed `origin/main` commit passes before issue close.
- [ ] No live scheduler state changes.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE | Three bounded CLI attempts failed to return a verdict. |
| Codex | APPROVE | Revision 2 resolves invalid ownership, merge-helper behavior, and false digest coupling. |
| Gemini | UNAVAILABLE | CLI exit 41: noninteractive authentication unavailable. |

**Overall result:** PASS (provider coverage degraded) — final Codex review APPROVE; Claude/Gemini unavailability is explicit. Implementation remains blocked pending user approval.

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

## Complexity: T2

Seven implementation artifacts form one scheduler-coherence chain. The work is multi-file and CI-facing, but the runtime behavior is bounded, non-mutating, and covered by existing deterministic generators and focused tests.
