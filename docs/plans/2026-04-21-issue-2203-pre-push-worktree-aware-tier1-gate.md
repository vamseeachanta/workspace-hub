# Plan for #2203: Make pre-push tier-1 repo checks worktree-aware for integration branches

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2203
> **Review artifacts:** none yet

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
- `core.hooksPath` is configured in this repo, so install logic must honor the effective hook path contract rather than assume `git-common-dir/hooks`
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
| Plan review — Gemini | `scripts/review/results/2026-04-21-plan-2203-gemini.md` |

---

## Deliverable

A tracked, canonical pre-push hook implementation plus tests that correctly classify workspace-hub-only pushes versus tier-1-repo pushes, so validated worktree/integration branches are not blocked by unrelated sibling-repo failures while genuine cross-repo enforcement remains intact.

---

## Pseudocode

```bash
function resolve_hook_targets():
    common_git_dir = git rev-parse --git-common-dir
    install_target = common_git_dir + "/hooks/pre-push"
    return install_target

function classify_push_scope(push_lines, local_oid, remote_oid):
    if delete_branch(local_oid):
        return SKIP
    changed_files = derive_changed_files(push_lines, local_oid, remote_oid)
    if changed_files include workspace-hub root/docs/scripts/tests only:
        return WORKSPACE_HUB_ONLY
    if changed_files include repo-path signals that require downstream repo checks:
        return CROSS_REPO_VALIDATION(required_repos)
    return WORKSPACE_HUB_ONLY

function derive_changed_files(push_lines, local_oid, remote_oid):
    if remote_oid != ZERO:
        return git diff --name-only remote_oid..local_oid
    merge_base = git merge-base origin/main local_oid
    return git diff --name-only merge_base..local_oid

function determine_repo_checks(scope):
    if scope == CROSS_REPO_VALIDATION:
        run check-all/run-all-tests only for the mapped repos
    else if scope == WORKSPACE_HUB_ONLY:
        skip sibling-repo fanout
        still run review gate, secrets scan, coverage/config drift, and all preserved pre-push guards

function install_pre_push_hook():
    write canonical tracked hook content to the common hooks target
    preserve the full existing gate chain explicitly
    verify no executable hook logic remains after final exit
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/hooks/pre-push.sh` | establish a tracked source-of-truth hook implementation instead of relying only on mutable `.git/hooks/pre-push` |
| Modify | `scripts/enforcement/install-hooks.sh` | install/sync the canonical tracked pre-push hook into the real hooks target for normal repos and linked worktrees, rather than only appending fragments into `.git/hooks/pre-push` |
| Modify | `tests/hooks/test_pre_push.py` | first restore the currently-red suite to green against the tracked hook file, then add regression coverage for workspace-hub-only new-branch pushes, zero-remote first-push classification, multi-ref pushes, and repo-name translation |
| Modify | `tests/enforcement/test_install_hooks_stage_prompt_drift.py` | preserve installer ordering/idempotency coverage and extend it for the new canonical hook sync behavior and full gate-chain preservation |
| Update | `docs/standards/REVIEW_GATE_BYPASS_POLICY.md` and/or `docs/governance/SESSION-GOVERNANCE.md` | document the narrowed bypass/landing behavior and the preserved gate chain after the fix |
| Update | `docs/plans/README.md` | add this plan to the index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_hook_suite_baseline_restored` | existing hook suite is green against the tracked canonical hook source | `uv run --no-project python -m pytest tests/hooks/test_pre_push.py -q` | all currently-intended baseline tests pass |
| `test_workspace_hub_only_new_branch_skips_tier1_repo_fanout` | new branch with only workspace-hub paths does not force all-repo checks | zero remote oid + changed files only under workspace-hub root/docs/scripts/tests with `PRE_PUSH_DRY_RUN=0` and fake downstream scripts | no sibling-repo calls recorded |
| `test_changed_tier1_repo_subset_still_runs_only_affected_repos` | existing changed-only behavior remains | changed files mapped to one downstream repo scope | only that repo’s checks invoked |
| `test_zero_remote_first_push_uses_defined_merge_base_diff` | first-push classification has a deterministic comparison base | zero remote oid + local oid on feature branch | changed files derived from documented merge-base strategy |
| `test_multi_ref_push_classification_is_safe` | multi-ref pushes do not misclassify based only on the first stdin line | multiple push lines on stdin | classification/routing honors a documented safe policy |
| `test_repo_name_translation_for_ogmanufacturing` | downstream repo-name translation is explicit and correct for both helper scripts | push affecting manufacturing scope | `check-all.sh` receives `ogmanufacturing`; `run-all-tests.sh` receives `OGManufacturing` (or equivalent documented adapter contract) |
| `test_bypass_still_logs_jsonl_and_exits_zero` | audited bypass remains intact | `GIT_PRE_PUSH_SKIP=1` | exit 0 + JSONL record |
| `test_hook_file_is_tracked_source_not_only_live_git_hook` | canonical hook exists in repo | repo root | `scripts/hooks/pre-push.sh` exists and is executable/text-valid |
| `test_install_hooks_syncs_tracked_pre_push_hook_for_linked_worktrees` | installer writes/syncs the tracked hook into the real hook target for linked worktrees | temp repo + linked worktree setup | installed hook target matches documented canonical source/chain |
| `test_install_hook_preserves_full_gate_chain_and_reachability` | installer preserves enforcement-env, review gate, stage-prompt drift, state-size, cadence-sync, and no executable logic remains after final exit | temp repo/worktree install | full ordered chain present and reachable |

---

## Acceptance Criteria

- [ ] `scripts/hooks/pre-push.sh` exists as a tracked canonical hook implementation
- [ ] `uv run --no-project python -m pytest tests/hooks/test_pre_push.py -v` passes (restored baseline + new cases)
- [ ] `uv run --no-project python -m pytest tests/enforcement/test_install_hooks_stage_prompt_drift.py -v` passes after installer changes
- [ ] the installed hook target for a linked worktree is correct and executable
- [ ] a workspace-hub-only integration/worktree push is not blocked by unrelated sibling-repo failures
- [ ] first-push (`remote_oid == ZERO`) classification uses an explicit documented diff base
- [ ] multi-ref push handling is covered by tests and does not rely unsafely on only the first stdin line
- [ ] downstream repo-name translation is explicit and correct for `OGManufacturing` / `ogmanufacturing`
- [ ] the full current pre-push gate chain is preserved (review, enforcement-env, stage-prompt drift, state-size, cadence-sync, secrets, coverage/config drift as applicable)
- [ ] audited bypass behavior remains available and documented for true exceptions
- [ ] docs/plans/README.md updated with this plan entry

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Hermes | MAJOR | Draft assumed `.git/hooks/pre-push` install path was worktree-safe; under-specified preservation of existing gate chain; missing multi-ref and broken-test-baseline handling |
| Claude | MAJOR | Dry-run new-branch test would not exercise real classification path; zero-remote compare-base undefined; existing red hook suite must be restored first |
| Codex | MAJOR | Draft missed installer regression test surface, included non-deterministic acceptance wording, and did not fully ground the scope in current hook drift/reachability |

**Overall status:** MAJOR — revise before promotion to `plan-review`.

**Revision note (2026-04-21):** This draft was updated after adversarial review to (a) make worktree/common-hook-dir installation explicit, (b) preserve the full pre-push gate chain, (c) treat the currently-red `tests/hooks/test_pre_push.py` suite as a prerequisite, (d) add first-push and multi-ref classification coverage, and (e) replace non-deterministic acceptance wording with repo-verifiable criteria.

---

## Risks and Open Questions

- **Risk:** narrowing new-branch behavior too aggressively could let real validation-relevant changes escape checks if change detection is wrong; mitigation is explicit first-push and multi-ref regression tests plus a documented merge-base strategy.
- **Risk:** introducing a tracked canonical hook file may overlap with #2128 installer-chain behavior; plan must preserve the full current gate chain, not just review/secrets/coverage/config-drift.
- **Risk:** linked-worktree hook installation is easy to get wrong because `.git` may be a file and hooks resolve through the common git dir; implementation must verify the actual install target in tests.
- **Risk:** the existing `tests/hooks/test_pre_push.py` suite is already red; implementation must restore a runnable baseline before relying on it for incremental regression coverage.
- **Open:** should workspace-hub-only pushes still run a lightweight workspace-hub-local pytest slice in pre-push, or only governance/security gates? Current recommendation: keep current non-tier1 gates, skip sibling-repo fanout.
- **Open:** should tier-1 repo mappings and translation logic be centralized into a shared config to avoid drift across hook/scripts/tests? Current plan keeps scope bounded and defers centralization unless implementation proves it is necessary.

---

## Complexity: T2

**T2** — bounded harness fix across one hook implementation, one installer/sync path, one test file, and a small documentation update, with clear regression coverage and no product-domain logic.