# Plan for #2203: Make pre-push tier-1 repo checks worktree-aware for integration branches

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2203
> **Review artifacts:** `scripts/review/results/2026-04-21-plan-2203-{claude,codex,hermes}.md` and `scripts/review/results/2026-04-21-plan-2203-{claude,codex,hermes}-r2.md`

---

## Resource Intelligence Summary

### Existing repo code

- Found: `.git/hooks/pre-push` — live pre-push gate reads git push stdin, enables `RUN_ALL=true` on new-branch pushes (`remote_oid == 000...`), then runs `check-all.sh` and `run-all-tests.sh` for every repo in `TIER1_REPOS`. This is the behavior now blocking unrelated workspace-hub work from landing.
- Found: `scripts/testing/run-all-tests.sh` — resolves repo directories from `REPO_ROOT` and executes full pytest suites for `assetutilities`, `digitalmodel`, `worldenergydata`, `assethold`, and `OGManufacturing`; skipped repos only occur when the directory is absent, not when the repo is unrelated to the push.
- Found: `scripts/quality/check-all.sh` — same repo-map pattern (`REPO_ROOT` + relative repo dir), but its accepted repo key for manufacturing is lowercase `ogmanufacturing`, unlike `run-all-tests.sh` which uses `OGManufacturing`.
- Found: `tests/hooks/test_pre_push.py` — intended TDD suite for the canonical hook, but currently red because it points at missing `scripts/hooks/pre-push.sh`; `uv run --no-project python -m pytest tests/hooks/test_pre_push.py -q` currently yields `9 failed, 1 passed`.
- Found: `tests/enforcement/test_install_hooks_stage_prompt_drift.py` — live installer regression suite already covers install-hook ordering/idempotency expectations and must be updated if `install-hooks.sh` changes.
- Found: `scripts/enforcement/install-hooks.sh` — still appends additional gates directly into `.git/hooks/pre-push`; current managed chain includes enforcement-env, review gate, stage-prompt drift, state-file-size, and cadence-sync.
- Found: linked worktrees use a common/effective hooks target that must be resolved via git’s hook-path contract; a worktree-local `.git` may be a file rather than a hook-bearing directory, and `core.hooksPath` can override naive common-dir assumptions.
- Gap: `scripts/hooks/pre-push.sh` does not exist in the repo even though tests and historical references treat it as the canonical hook implementation path.
- Gap: no worktree-aware classification exists for “workspace-hub-only push” vs “cross-repo validation push”, so a new feature branch with no tier-1-relevant changes escalates to full all-repo checks.
- Gap: the current live pre-push file already contains partially unreachable appended sections after `exit "$OVERALL_EXIT"`, so the issue is not just scope classification but also source-of-truth / reachability drift.

### Standards

| Standard | Status | Source |
|---|---|---|
| `docs/standards/HARD-STOP-POLICY.md` | relevant governance context | repo standard |
| `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` | relevant governance context | repo standard |

### LLM Wiki pages consulted

- No relevant wiki pages — this is a harness / git-hook / repo-governance issue.

### Documents consulted

- Issue #2203 body — defines original problem: integration/worktree pushes should not fail because sibling tier-1 repos are absent or unrelated.
- `docs/handoffs/session-2026-04-11-2151-2155-landing-and-followups.md` — records the original reproduction and the `GIT_PRE_PUSH_SKIP=1` workaround used during landing of #2151/#2155.
- Latest issue comment on #2203 (2026-04-21) — fresh reproduction from #2348 shows the blocker persists even when repos are present, because unrelated sibling-repo failures still block a validated workspace-hub-only push.
- `docs/plans/2026-04-11-issue-2128-install-hooks-pre-push-chain-drift.md` — adjacent hook-chain plan proving pre-push governance already has drift/history and that `scripts/hooks/pre-push.sh` was intended as a tracked runtime reference.
- `docs/standards/CONTROL_PLANE_CONTRACT.md` — harness/control-plane contract source relevant to how tracked artifacts and live adapter surfaces should relate.
- `.claude/rules/` and `config/agents/` surfaces were checked for harness-plan retrieval completeness; no stronger alternate hook-path contract was found there than the git-resolved effective hook path.

### Gaps identified

- No authoritative tracked hook file exists at `scripts/hooks/pre-push.sh`, yet tests assume one.
- New-branch pushes are treated as `RUN_ALL`, which is too broad for workspace-hub-only branches and integration worktrees.
- The live hook conflates “cannot diff changed files yet” with “must run unrelated sibling-repo suites”.
- Repo-name normalization is inconsistent between the live hook (`OGManufacturing`) and other tooling (`ogmanufacturing` mapping in `check-all.sh`).
- No regression test explicitly captures the #2203 / #2348 failure mode: a workspace-hub-only new branch push should not be blocked by unrelated red sibling repos.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-21 via `gh issue view` / `gh issue list`):
- `#2203` — OPEN — `fix(harness): make pre-push tier-1 repo checks worktree-aware for integration branches`
- `#2348` — OPEN — latest progress comment reports local implementation is ready but push is blocked by the same pre-push coupling class

**File existence**:
- EXISTS: `.git/hooks/pre-push`
- EXISTS: `tests/hooks/test_pre_push.py`
- EXISTS: `tests/enforcement/test_install_hooks_stage_prompt_drift.py`
- EXISTS: `scripts/quality/check-all.sh`
- EXISTS: `scripts/testing/run-all-tests.sh`
- EXISTS: `scripts/enforcement/install-hooks.sh`
- MISSING: `scripts/hooks/pre-push.sh`

**Command evidence**:
```bash
$ uv run --no-project python -m pytest tests/hooks/test_pre_push.py -q
FFFFFF.FFF
9 failed, 1 passed
```

**Worktree topology evidence**:
```bash
- linked worktrees exist under /mnt/local-analysis/worktrees/
- in linked worktrees, `.git` may be a file and the effective hook target must be resolved by git
- `core.hooksPath` resolves in this repo to `/mnt/local-analysis/workspace-hub/.git/hooks`, so install logic must honor the effective hook path contract rather than assume `git-common-dir/hooks`.
```

**Line excerpts**:
```bash
# .git/hooks/pre-push
94|if [[ "$FIRST_REMOTE_OID" == "$ZERO_OID" ]]; then
95|    echo "[pre-push] New branch — running all tier-1 repo checks." >&2
96|    RUN_ALL=true
97|fi
102|if [[ "$RUN_ALL" == "true" ]]; then
103|    REPOS_TO_CHECK=("${TIER1_REPOS[@]}")
```

```bash
# tests/hooks/test_pre_push.py
21|REPO_ROOT = Path(__file__).resolve().parents[2]
22|HOOK_SCRIPT = REPO_ROOT / "scripts" / "hooks" / "pre-push.sh"
```

```bash
# scripts/testing/run-all-tests.sh
23|REPO_CONFIGS=(
24|    "assetutilities:assetutilities::tests/ --noconftest"
25|    "digitalmodel:digitalmodel:src:"
26|    "worldenergydata:worldenergydata:src:--noconftest"
27|    "assethold:assethold::tests/ --noconftest --tb=short -q"
28|    "OGManufacturing:OGManufacturing::tests/"
29|)
```

```bash
# docs/handoffs/session-2026-04-11-2151-2155-landing-and-followups.md
68|### #2203
69|- Link: https://github.com/vamseeachanta/workspace-hub/issues/2203
70|- Title: fix(harness): make pre-push tier-1 repo checks worktree-aware for integration branches
79|The push of `integration-2151-2155` required the documented soft bypass:
80|- `GIT_PRE_PUSH_SKIP=1 git push -u origin integration-2151-2155`
82|Reason:
83|- the pre-push hook attempted tier-1 repo checks using sibling repo paths under the integration worktree and failed because those repos were not present there.
```

**Gap proofs**:
- `read_file("/mnt/local-analysis/workspace-hub/scripts/hooks/pre-push.sh")` → file not found.
- `gh issue list --state open --search 'pre-push tier-1 gate sibling repo failures unrelated push OR worldenergydata assethold pre-push gate'` returned `#2203`, confirming no narrower existing fix issue was already open for the same landing-blocker class.

Distinct sources consulted: 8.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-21-issue-2203-pre-push-worktree-aware-tier1-gate.md` |
| Canonical tracked hook source | `scripts/hooks/pre-push.sh` |
| Hook installer / synchronizer | `scripts/enforcement/install-hooks.sh` |
| Existing live hook reference | `.git/hooks/pre-push` |
| Existing installer regression tests | `tests/enforcement/test_install_hooks_stage_prompt_drift.py` |
| Hook behavior tests | `tests/hooks/test_pre_push.py` |
| Follow-up docs / policy note | `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` or `docs/governance/SESSION-GOVERNANCE.md` |
| Plan review — Claude | `scripts/review/results/2026-04-21-plan-2203-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-21-plan-2203-codex.md` |
| Plan review — Hermes | `scripts/review/results/2026-04-21-plan-2203-hermes.md` |
| Plan review — Claude (r2) | `scripts/review/results/2026-04-21-plan-2203-claude-r2.md` |
| Plan review — Codex (r2) | `scripts/review/results/2026-04-21-plan-2203-codex-r2.md` |
| Plan review — Hermes (r2) | `scripts/review/results/2026-04-21-plan-2203-hermes-r2.md` |

---

## Deliverable

A tracked, canonical pre-push hook implementation plus tests that correctly classify workspace-hub-only pushes versus tier-1-repo pushes, so validated worktree/integration branches are not blocked by unrelated sibling-repo failures while genuine cross-repo enforcement remains intact.

---

## Pseudocode

```bash
function resolve_hook_targets():
    hook_target = git rev-parse --git-path hooks/pre-push
    enforcement_env_target = git rev-parse --git-path hooks/enforcement-env
    return hook_target, enforcement_env_target

function classify_push_scope(push_lines, local_oid, remote_oid):
    if delete_branch(local_oid):
        return SKIP
    changed_files = derive_changed_files(push_lines, local_oid, remote_oid)
    if touches_harness_sensitive_workspace_hub_paths(changed_files):
        return CROSS_REPO_VALIDATION(all_or_mapped_repos)
    if changed_files include only docs/plans/docs/reports/issue comments and other non-execution docs:
        return WORKSPACE_HUB_ONLY
    if changed_files include workspace-hub code/config paths that do not alter cross-repo fanout semantics:
        return WORKSPACE_HUB_ONLY
    if changed_files include explicit repo-path signals that require downstream repo checks:
        return CROSS_REPO_VALIDATION(required_repos)
    return WORKSPACE_HUB_ONLY

function derive_changed_files(push_lines, local_oid, remote_oid):
    if remote_oid != ZERO:
        return git diff --name-only remote_oid..local_oid
    return commits_not_on_any_remote(local_oid) projected to changed file paths

function determine_repo_checks(scope):
    if scope == CROSS_REPO_VALIDATION:
        run check-all/run-all-tests only for the mapped repos
    else if scope == WORKSPACE_HUB_ONLY:
        skip sibling-repo fanout, including the current all-repo coverage fanout path
        run only preserved non-fanout governance/security guards on this path

function run_preserved_guards(push_lines):
    buffer stdin push_lines once
    replay required ref/range data to downstream guards that depend on push stdin
    especially preserve correctness for state-size pre-push guard

function install_pre_push_hook():
    write canonical tracked hook content to the effective git hook target
    preserve the full existing gate chain explicitly
    verify no executable hook logic remains after final exit
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/hooks/pre-push.sh` | establish a tracked source-of-truth hook implementation instead of relying only on mutable `.git/hooks/pre-push` |
| Modify | `scripts/enforcement/install-hooks.sh` | install/sync the canonical tracked pre-push hook into the effective git hook target for normal repos and linked worktrees (`git rev-parse --git-path hooks/...`), rather than only appending fragments into `.git/hooks/pre-push` |
| Modify | `tests/hooks/test_pre_push.py` | first restore the currently-red suite to green against the tracked hook file, then add regression coverage for workspace-hub-only new-branch pushes, zero-remote first-push classification, multi-ref pushes, and repo-name translation |
| Modify | `tests/enforcement/test_install_hooks_stage_prompt_drift.py` | preserve installer ordering/idempotency coverage and extend it for the new canonical hook sync behavior and full gate-chain preservation |
| Update | `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` and/or `docs/governance/SESSION-GOVERNANCE.md` | document the narrowed bypass/landing behavior and the preserved gate chain after the fix |
| Update | `docs/plans/README.md` | add this plan to the index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_hook_suite_baseline_restored` | existing hook suite is green against the tracked canonical hook source | `uv run --no-project python -m pytest tests/hooks/test_pre_push.py -q` | all currently-intended baseline tests pass |
| `test_workspace_hub_only_new_branch_skips_tier1_repo_fanout` | new branch with only non-execution workspace-hub paths does not force all-repo checks | zero remote oid + changed files only under docs/plans/docs/reports/non-execution docs with `PRE_PUSH_DRY_RUN=0` and fake downstream scripts | no sibling-repo calls recorded |
| `test_harness_sensitive_workspace_hub_paths_force_cross_repo_validation` | changes to fanout-controlling harness files do not get misclassified as workspace-hub-only | changes under `scripts/testing/run-all-tests.sh`, `scripts/quality/check-all.sh`, `scripts/enforcement/install-hooks.sh`, or equivalent harness-sensitive paths | scope escalates to `CROSS_REPO_VALIDATION` |
| `test_changed_tier1_repo_subset_still_runs_only_affected_repos` | existing changed-only behavior remains | changed files mapped to one downstream repo scope | only that repo’s checks invoked |
| `test_zero_remote_first_push_uses_defined_remote-agnostic_diff_base` | first-push classification has a deterministic comparison base that does not rely on `origin/main` | zero remote oid + local oid on feature/integration branch | changed files derived from commits not yet on any remote |
| `test_multi_ref_push_classification_uses_union_or_fail_closed_policy` | multi-ref pushes do not misclassify based only on the first stdin line | multiple push lines on stdin | routing follows the documented union-of-changes policy or explicit fail-closed cross-repo validation fallback |
| `test_repo_name_translation_for_ogmanufacturing` | downstream repo-name translation is explicit and correct for both helper scripts | push affecting manufacturing scope | `check-all.sh` receives `ogmanufacturing`; `run-all-tests.sh` receives `OGManufacturing` (or equivalent documented adapter contract) |
| `test_bypass_still_logs_jsonl_and_exits_zero` | audited bypass remains intact | `GIT_PRE_PUSH_SKIP=1` | exit 0 + JSONL record |
| `test_hook_file_is_tracked_source_not_only_live_git_hook` | canonical hook exists in repo | repo root | `scripts/hooks/pre-push.sh` exists and is executable/text-valid |
| `test_install_hooks_syncs_tracked_pre_push_hook_for_linked_worktrees` | installer writes/syncs the tracked hook into the effective git hook target for linked worktrees and hooksPath-aware repos | temp repo + linked worktree setup | installed hook target matches documented canonical source/chain |
| `test_install_hook_preserves_full_gate_chain_and_reachability` | installer preserves enforcement-env, review gate, stage-prompt drift, state-size, cadence-sync, mypy/complexity opt-in gate stubs, and no executable logic remains after final exit | temp repo/worktree install | full ordered intended chain present and reachable |
| `test_workspace_hub_only_path_still_runs_non_fanout_guards` | workspace-hub-only push skips sibling fanout but still executes preserved non-fanout guards | workspace-hub-only changed files + fake downstream guard scripts + buffered stdin | no sibling-repo fanout, but preserved guards are invoked with correct inputs |
| `test_installer_fixture_sync_includes_canonical_hook_source` | installer tests stage the tracked canonical hook source so sync/install behavior is exercised realistically | temp repo fixture setup | `scripts/hooks/pre-push.sh` is present in the temp fixture before installer sync assertions run |

---

## Acceptance Criteria

- [ ] `scripts/hooks/pre-push.sh` exists as a tracked canonical hook implementation
- [ ] `uv run --no-project python -m pytest tests/hooks/test_pre_push.py -v` passes (restored baseline + new cases)
- [ ] `uv run --no-project python -m pytest tests/enforcement/test_install_hooks_stage_prompt_drift.py -v` passes after installer changes
- [ ] the installed hook target for a linked worktree / hooksPath-aware repo is correct and executable
- [ ] a workspace-hub-only integration/worktree push is not blocked by unrelated sibling-repo failures
- [ ] harness-sensitive workspace-hub changes that alter cross-repo validation behavior escalate to `CROSS_REPO_VALIDATION`
- [ ] first-push (`remote_oid == ZERO`) classification uses an explicit remote-agnostic diff base
- [ ] multi-ref push handling follows an explicit documented union-of-changes or fail-closed policy
- [ ] downstream repo-name translation is explicit and correct for `OGManufacturing` / `ogmanufacturing`
- [ ] the full intended pre-push gate chain is preserved, including opt-in mypy/complexity ratchet hooks and correct stdin replay for downstream guards that require push ref data
- [ ] workspace-hub-only non-fanout paths still execute preserved governance/security guards
- [ ] installer fixture/test setup includes the canonical tracked hook source when validating sync/install behavior
- [ ] audited bypass behavior remains available and documented for true exceptions

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Hermes (round 1) | MAJOR | Draft assumed `.git/hooks/pre-push` install path was worktree-safe; under-specified preservation of existing gate chain; missing multi-ref and broken-test-baseline handling |
| Claude (round 1) | MAJOR | Dry-run new-branch test would not exercise real classification path; zero-remote compare-base undefined; existing red hook suite must be restored first |
| Codex (round 1) | MAJOR | Draft missed installer regression test surface, included non-deterministic acceptance wording, and did not fully ground the scope in current hook drift/reachability |
| Hermes (round 2) | MAJOR | Revised draft still used `git-common-dir` rather than effective hooks path, omitted opt-in ratchet gates from explicit preservation, and had stale metadata |
| Claude (round 2) | MAJOR | Revised draft still failed to anchor on hook-path resolution and lacked runtime proof that workspace-hub-only paths skip fanout while still running preserved guards |
| Codex (round 2) | MAJOR | Revised draft still needed remote-agnostic first-push diff strategy, stdin replay requirements for downstream guards, and tighter grounding of intended-vs-live gate-chain preservation |
| Hermes (round 3) | MAJOR | Workspace-hub-only path still needed explicit exclusion of the current all-repo coverage fanout path and clearer handling of obsolete tests |
| Claude (round 3) | MAJOR | Harness-sensitive path escalation and concrete multi-ref policy still needed to be made explicit |
| Codex (round 3) | MAJOR | Harness-sensitive classification and cadence-sync contract still needed to be settled explicitly |

**Overall status:** MAJOR after third review pass — the draft improved again, but it is still not ready for `plan-review` promotion.

**Revision notes (2026-04-21):**
- Round 1 revisions added worktree-aware installation, full-gate-chain preservation, broken-test-baseline handling, first-push and multi-ref coverage, and deterministic acceptance language.
- Round 2 revisions replaced naive `git-common-dir` targeting with effective hook-path resolution, switched first-push diffing to a remote-agnostic strategy, added stdin replay requirements for downstream guards, expanded explicit gate preservation to include opt-in ratchet hooks, and removed stale metadata/acceptance items.
- Round 3 revisions narrowed workspace-hub-only classification so harness-sensitive workspace-hub paths escalate to cross-repo validation, defined multi-ref handling as union-of-changes or fail-closed, clarified that workspace-hub-only paths skip the current all-repo coverage fanout path, and settled cadence-sync as part of the intended installer-managed chain.

**Next gate:** the plan should be refreshed once more and then re-reviewed before any `status:plan-review` promotion.

---

## Risks and Open Questions

- **Risk:** narrowing new-branch behavior too aggressively could let real validation-relevant changes escape checks if change detection is wrong; mitigation is explicit first-push and multi-ref regression tests plus a documented remote-agnostic diff strategy.
- **Risk:** introducing a tracked canonical hook file may overlap with #2128 installer-chain behavior; plan must preserve the full intended gate chain, including opt-in ratchet hooks and correct stdin replay for downstream guards.
- **Risk:** linked-worktree hook installation is easy to get wrong because `.git` may be a file and `core.hooksPath` can redirect hook resolution; implementation must verify the effective hook target in tests using git-resolved hook paths.
- **Risk:** the existing `tests/hooks/test_pre_push.py` suite is already red; implementation must restore a runnable baseline before relying on it for incremental regression coverage.
- **Open:** should workspace-hub-only pushes still run a lightweight workspace-hub-local pytest slice in pre-push, or only governance/security gates? Current recommendation: keep current non-tier1 gates, skip sibling-repo fanout.
- **Open:** should cadence-sync be treated as part of the intended installer-managed chain even though it is not present in the current live hook snapshot? The implementation should choose one contract explicitly and test against that contract.
- **Open:** should tier-1 repo mappings and translation logic be centralized into a shared config to avoid drift across hook/scripts/tests? Current plan keeps scope bounded and defers centralization unless implementation proves it is necessary.

---

## Complexity: T2

**T2** — bounded harness fix across one hook implementation, one installer/sync path, one test file, and a small documentation update, with clear regression coverage and no product-domain logic.