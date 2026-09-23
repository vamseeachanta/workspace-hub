# Plan for #3707: Cron Upkeep Clockwork

> **Status:** adversarial-reviewed
> **Complexity:** T3
> **Date:** 2026-07-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3707
> **Blocker:** https://github.com/vamseeachanta/workspace-hub/issues/3708
> **Client:** N/A
> **Lane:** lane:codex
> **Review artifacts:** scripts/review/results/2026-07-30-plan-3707-codex-r1.md

---

## Resource Intelligence Summary

Execution mode for this plan will be `parallel-readonly` for evidence and review, then `single-lane` for any future approved implementation because the change set will touch shared cron, cleanup, guard, and health surfaces.

### Existing repo code

- `scripts/cron/daily-cleanup.sh` will receive the core cleanup corrections. Current evidence will confirm that it will still resolve non-`workspace-hub` repos as `$WORKSPACE_ROOT/$repo`, will use `git branch --merged origin/main`, will gate branch names through `SAFE_BRANCH_RE='^(chore/auto-|bot/|claude-session/)'`, will only surface aged stashes, and will not write durable semantic-success state.
- `scripts/lib/worktree_guard.py` will remain the ownership authority. Its `.wt-owner` marker contract will be preserved, but future worktree creators will be required to call `mark-owner` so the deny-by-default rule will become effective instead of inert.
- `scripts/readiness/reconcile-ecosystem.sh` will provide reusable detection patterns for sibling-root discovery and squash-merge-aware branch detection, but `#3707` will not delegate daily disposal to `reconcile-ecosystem.sh --apply`.
- `scripts/monitoring/cron-health-check.sh` will consume daily-cleanup semantic outcome state. It will preserve current log/runtime checks and will add a disposal-effectiveness failure when eligible cleanup backlog will persist for N consecutive runs with zero disposal.
- `scripts/cron/cron-audit.py`, `scripts/cron/cron_apply.py`, and `scripts/cron/setup-cron.sh` will be treated as #3708-owned deployment gates. `#3707` will consume the safe apply path after #3708 rather than bypassing it.

### Standards

| Standard | Status | Source |
|---|---|---|
| Issue planning workflow | active | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| Parallel-first execution | active | `docs/standards/PARALLEL_FIRST_EXECUTION.md` |
| Control-plane contract | active | `docs/standards/CONTROL_PLANE_CONTRACT.md` |

### LLM Wiki pages consulted

- No relevant wiki pages will apply; this will be a workspace-hub harness/infra plan.

### Documents Consulted

- GitHub issue `#3707` will define the cleanup defects and required scope.
- GitHub issue `#3708` will define the crontab apply blocker and safe-cutover requirements.
- `docs/plans/2026-06-12-issue-3041-repo-ecosystem-hygiene-audit.md` will supply the known sibling-path mismatch, read-only hygiene signal, cron-health link, and warning that `daily-cleanup --dry-run` will not be treated as a read-only audit.
- `docs/plans/2026-07-11-issue-3463-cron-singleton-runtime-health.md` will supply the runtime-health preservation boundary.
- `docs/plans/2026-07-11-issue-3475-cron-semantic-ownership.md` and `docs/plans/2026-07-11-issue-3347-cron-installer-convergence.md` will supply the cron ownership and cutover context.
- `config/workstations/registry.yaml` will supply machine-specific repo roots. Future tests will include at least Linux sibling roots under `/mnt/local-analysis`, Linux storage/root drift such as dev-secondary, Windows `D:\` sibling roots, and `gpu-claw` style `/home/.../ws` roots.
- Drive-file search for `cron daily cleanup worktree stash` will return no relevant reachable results; all configured drive indexes will be unreachable/stale from this local checkout, so this plan will rely on tracked repo evidence.

### Gaps Identified

- No durable daily-cleanup semantic outcome artifact will exist for cron-health to consume.
- No daily-cleanup fixture harness will exist for hermetic branch/worktree/stash/sibling disposal cases.
- No automatic system-cron schedule for `daily-cleanup` will exist in `schedule-tasks.yaml`.
- No #3707-owned safe crontab regeneration path will exist; #3708 will own that unblocker.
- No automation-wide `.wt-owner` writer policy will be enforced outside the guard CLI.
- No stash disposal or consumed stash-alert policy will exist for unattended upkeep.

### Evidence

**Issue statuses** (verified 2026-07-30 local time via `gh issue view`):
- `#3707` will remain OPEN with `status:needs-plan` until this plan and review will be pushed.
- `#3708` will remain OPEN with `status:needs-plan` and will directly block live system-cron deployment.

**File existence** (`ls`/required reads):
- `scripts/cron/daily-cleanup.sh`
- `scripts/cron/setup-cron.sh`
- `scripts/cron/cron-audit.py`
- `scripts/lib/worktree_guard.py`
- `scripts/readiness/reconcile-ecosystem.sh`
- `config/scheduled-tasks/schedule-tasks.yaml`
- `config/workstations/registry.yaml`
- `docs/plans/_template-issue-plan.md`
- `docs/plans/README.md`
- `.claude/skills/coordination/issue-planning-mode/SKILL.md`
- `CLAUDE.md`

**Defect verification results:**

| Defect | Verification result | Evidence and adjustment |
|---|---|---|
| D1 | CONFIRMED | `rg daily-cleanup config/scheduled-tasks/schedule-tasks.yaml` will return no task entry; local `crontab -l` will contain only repository-sync and no `daily-cleanup`. Fleet crontab absence will remain issue-supplied evidence because this plan will not SSH. |
| D2 | CONFIRMED | `daily-cleanup.sh` will define `SAFE_BRANCH_RE` as `^(chore/auto-|bot/|claude-session/)`, and the local branch sample will include `main` plus `plan/3702...` with zero matches. `git branch --merged origin/main` will only report ancestry merges and will not prove squash-merged branches. |
| D3 | CONFIRMED WITH ADJUSTMENT | `daily-cleanup.sh` will define `SIBLING_ROOT=/mnt/local-analysis`, but the per-repo loop will still set non-workspace `REPO_DIR="$WORKSPACE_ROOT/$repo"`. The defect will be "correct root constant present but unused", not total absence of a sibling-root variable. |
| D4 | CONFIRMED | `worktree_guard.py` will require `.wt-owner` for `safe-remove-worktree`; `find . -name .wt-owner` in this checkout will return no markers; `rg` will show only the guard and a repo-housekeeping read path, with no production creator policy beyond `mark-owner`. |
| D5 | CONFIRMED WITH SCOPE CLARIFICATION | `rg "stash (drop|clear)|git stash (drop|clear)" scripts` will return no matches. Broader repo memory/docs will mention `git stash drop`, but no executable under `scripts/` will drop or clear stashes. |

**Reproduction proofs**:

```
$ rg -n "daily-cleanup" config/scheduled-tasks/schedule-tasks.yaml scripts/cron tests scripts/cron/tests
tests/quality/test_tier1_repos_ssot.bats:59:    scripts/cron/daily-cleanup.sh scripts/security/secrets-scan.sh
...
scripts/cron/daily-cleanup.sh:2:# daily-cleanup.sh — 23:00 daily Hermes cron job
```

```
$ crontab -l
# Daily repository sync for workspace-hub
WORKSPACE_HUB=/Users/krishna/Developer/ws/workspace-hub
0 2 * * * mkdir -p $WORKSPACE_HUB/logs && cd $WORKSPACE_HUB && /opt/homebrew/bin/bash scripts/repository_sync >> ...
```

```
$ git branch --format='%(refname:short)' | rg '^(chore/auto-|bot/|claude-session/)' || true
<no output>
```

```
$ rg -n "stash (drop|clear)|git stash (drop|clear)" scripts
<no output>
```

Reproduced at: 2026-07-30 local time. Failure mode observed will match issue claims, with D3 adjusted to note the unused `SIBLING_ROOT` variable.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-30-issue-3707-cron-upkeep-clockwork.md` |
| Plan review | `scripts/review/results/2026-07-30-plan-3707-codex-r1.md` |
| Daily-cleanup tests | `tests/cron/test_daily_cleanup_clockwork.py` or `scripts/cron/tests/test_daily_cleanup_clockwork.sh` |
| Worktree guard tests | `tests/cron/test_worktree_guard.py` |
| Cron render/apply/audit tests | `tests/cron/test_cron_render.py`, `tests/cron/test_cron_apply.py`, `tests/cron/test_cron_audit.py` |
| Cron health tests | `scripts/monitoring/tests/test_cron_health_check.sh` |
| Future implementation surfaces | `scripts/cron/daily-cleanup.sh`, `scripts/lib/worktree_guard.py`, worktree-creating automation, `scripts/monitoring/cron-health-check.sh`, `config/scheduled-tasks/schedule-tasks.yaml` |

---

## Deliverable

A system-cron-backed, fixture-tested daily cleanup flow will dispose of eligible stale branches/worktrees/stashes, will preserve active/user-owned work, and will report semantic cleanup failure through cron-health when it runs but fails to do useful cleanup.

---

## Sequencing Against #3708

#3708 will need to land before #3707 can be deployed as live system cron. The narrower path of adding a `daily-cleanup` YAML task and tests first would only stage metadata; it would not make cleanup clockwork because `cron-audit.py` will still fail closed on uncataloged live lines and `setup-cron.sh --replace` will still reject replacement.

The future #3707 implementation may land code and catalog changes after approval, but acceptance and closeout will require #3708's safe apply path to pass in dry-run and reviewed apply modes. No #3707 step will manually edit crontab, call `setup-cron.sh --replace`, or revive Hermes. Hermes gateway will remain DOWN by owner decision, and `daily-cleanup` will run from system cron only.

---

## Pseudocode

```
function resolve_cleanup_repos(machine_id):
    load registry.yaml
    resolve machine id, hostname, aliases, os, workspace_root, tier1_repo_root, repo_layout
    if os == windows:
        return no system-cron daily-cleanup target for v1
    for each tier1_baseline required/optional repo:
        resolve path under tier1_repo_root for sibling layout
        validate workspace-hub path equals workspace_root
        yield repo path or missing disposition
```

```
function find_branch_disposal_candidates(repo):
    fetch/prune only when live mode and allowed
    list local branches except main/master/current
    classify ancestry-merged branches via merge-base or branch --merged
    classify squash-merged branches via gh pr list --state merged headRefName
    require no open PR, branch not checked out in any worktree, and age/policy match
    return force-delete only for PR-merged squash branches; return -d for ancestry-merged branches
```

```
function find_worktree_disposal_candidates(repo):
    list linked worktrees
    ignore primary worktree
    compute age from worktree HEAD commit and marker metadata
    require .wt-owner owner in allowed cleanup owners
    require branch merged/squash-merged or detached/expired policy
    return remove candidates only when worktree_guard approves
```

```
function find_stash_disposal_candidates(repo):
    parse git stash list --date=iso-strict with stable fields
    inspect stash patch metadata and message
    auto-drop only allowlisted automation-owned stash prefixes older than threshold and content-safe
    otherwise record aged stash count and oldest age
    emit alert when aged stashes exceed threshold
```

```
function write_cleanup_outcome(state):
    record run_id, start/end, repo_count, eligible_count, disposed_count, surfaced_count, errors
    record per-category eligible and disposed counts
    update consecutive_noop_counter only when eligible_count > 0 and disposed_count == 0
    write latest JSON atomically under .claude/state/daily-cleanup/
```

```
function cron_health_daily_cleanup_check(task):
    run normal log freshness/error/runtime checks
    load daily-cleanup latest outcome when task id is daily-cleanup
    if outcome stale or missing: fail via normal MISSING/STALE
    if consecutive_noop_counter >= N and eligible_count > 0: mark CLEANUP_NOOP
    preserve existing repo-ecosystem-hygiene-audit, cron_runtime.py singleton, git-lock-reaper, return-to-main-guard checks
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `tests/cron/test_daily_cleanup_clockwork.py` or `scripts/cron/tests/test_daily_cleanup_clockwork.sh` | Hermetic RED tests for branch, sibling-root, worktree, stash, and outcome-state defects |
| Modify | `scripts/cron/daily-cleanup.sh` | Future implementation will fix repo resolution, squash-aware branch disposal, worktree/stash policy, durable outcome state, and system-cron-safe behavior |
| Modify | `scripts/lib/worktree_guard.py` | Future implementation will keep deny-by-default and add metadata/age policy helpers only if required by marker ownership tests |
| Modify | Worktree-creating automation paths discovered by `rg "git worktree add|worktree add"` | Future implementation will write `.wt-owner` markers for automation-owned worktrees |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | Future implementation will add a first-class `daily-cleanup` system-cron task only after #3708 safe cutover will be available |
| Modify | `scripts/monitoring/cron-health-check.sh` | Future implementation will consume cleanup outcome state and flag semantic no-op failures |
| Modify | `scripts/monitoring/tests/test_cron_health_check.sh` | Future implementation will cover `CLEANUP_NOOP`/semantic-failure health behavior |
| Modify | `tests/cron/test_cron_render.py`, `tests/cron/test_cron_apply.py`, `tests/cron/test_cron_audit.py` | Future implementation will verify schedule rendering/audit/apply behavior for the new task after #3708 |
| Update | `docs/plans/README.md` | This plan will be indexed |

No future #3707 implementation will modify `repo-ecosystem-hygiene-audit.sh`, `cron_runtime.py`, `git-lock-reaper`, or `return-to-main-guard` beyond consuming their existing output.

---

## TDD Test List

Every row will be written and run RED before implementation. The fixture suite will build a temporary multi-repo ecosystem with one squash-merged branch, one sibling repo at the real root, one live linked worktree, and one aged stash. The current no-op behavior must fail these tests before code changes.

| Test name | What it will verify | Expected input | Expected output |
|---|---|---|---|
| `test_schedule_catalog_requires_daily_cleanup_task` | D1 schedule absence will fail RED | current `schedule-tasks.yaml` | missing `daily-cleanup` task will fail |
| `test_cron_render_daily_cleanup_targets_linux_only` | system cron task will render on Linux and skip Windows Task Scheduler | registry fixtures for dev-primary, dev-secondary, Windows, gpu-claw | Linux render will include task; Windows render will exclude it |
| `test_cron_audit_blocks_until_3708_equivalent_lines_classify` | #3708 gate will remain respected | drifted-but-equivalent line and unknown line | equivalent will classify cataloged after #3708; unknown will still block |
| `test_squash_merged_branch_candidate_detected` | D2 squash-merged branch will be detected without ancestry | temp repo branch with PR-merged head from `gh` fixture and no merge-base ancestry | branch will be eligible for guarded `branch -D` |
| `test_safe_branch_regex_no_longer_vacuous` | branch policy will match real fleet prefixes only through explicit policy, not empty legacy regex | branches `feat/x`, `fix/y`, `worktree-agent-z`, `chore/auto-x` | policy will classify intended candidates; legacy empty-match behavior will fail RED |
| `test_open_pr_branch_never_deleted` | open PR will protect branches even if stale/safe-named | `gh pr list --state open` fixture | candidate will be surfaced, not deleted |
| `test_branch_checked_out_in_worktree_never_deleted` | worktree guard will protect live branch | linked worktree on branch | branch delete candidate will be blocked |
| `test_sibling_repo_resolves_from_registry_tier1_root` | D3 sibling path will use real root | workspace at `<root>/workspace-hub`, sibling at `<root>/digitalmodel` | sibling will be scanned, not reported missing |
| `test_machine_layouts_resolve_without_hardcoded_mnt` | registry path differences will not break other machines | dev-primary, dev-secondary, Windows `D:\`, gpu-claw path fixtures | POSIX paths and Windows exclusions will resolve deterministically |
| `test_worktree_without_owner_marker_is_not_removed_and_counts_as_blocked_backlog` | D4 no marker will be safe but visible | live worktree with no `.wt-owner` | no remove; backlog/outcome will record blocked unowned worktree |
| `test_automation_owned_aged_merged_worktree_is_removable` | recommended ownership policy will be effective | live worktree with `.wt-owner=daily-cleanup` or automation owner, old HEAD, merged branch | guard-approved removal candidate will be emitted |
| `test_worktree_creators_write_owner_marker` | future worktree automation will write `.wt-owner` | discovered worktree creator fixture | marker will be written with owner and timestamp/policy fields |
| `test_aged_allowlisted_automation_stash_can_drop` | D5 controlled stash disposal will exist | aged stash with allowlisted automation prefix and content-safe patch | specific `stash@{N}` drop candidate will be emitted |
| `test_human_or_unknown_aged_stash_only_alerts` | repo-wide human stash will not be swept | aged stash without allowlisted prefix | no drop; alert/backlog threshold will increment |
| `test_never_uses_stash_clear_or_drop_all_loop` | destructive broad stash cleanup will stay forbidden | source scan | no `git stash clear`; no unfiltered drop loop |
| `test_daily_cleanup_writes_semantic_outcome_json` | cron-health will receive semantic evidence | fixture cleanup run | `.claude/state/daily-cleanup/latest.json` will include eligible/disposed/surfaced/errors |
| `test_noop_with_eligible_backlog_fails_after_n_runs` | health check will catch "ran but did nothing" | N consecutive outcome fixtures with eligible backlog and zero disposal | cron-health will report `CLEANUP_NOOP` and nonzero exit |
| `test_true_empty_backlog_noop_stays_healthy` | no-op will not fail when nothing will need disposal | N outcomes with eligible count zero | cron-health will remain OK |
| `test_windows_reconcile_wrapper_still_delegates` | Windows/PowerShell path will not break | `scripts/windows/reconcile-ecosystem.ps1` fixture | wrapper will continue to call `scripts/readiness/reconcile-ecosystem.sh`; no daily-cleanup system cron path will be assumed on Windows |
| `test_dry_run_does_not_mutate_repos_or_crontab` | future dry-run will be read-only | temp repo and crontab shim | no branch/worktree/stash/crontab mutation will occur |

---

## Acceptance Criteria

- [ ] #3708 will have landed, and its tests will prove drifted-but-equivalent live lines classify as cataloged while genuinely unknown lines still block.
- [ ] `daily-cleanup` will be declared as a system-cron task in `schedule-tasks.yaml` and rendered/applied only through the #3708-reviewed safe crontab path.
- [ ] Hermes gateway will remain out of scope and down; no `daily-cleanup` execution path will depend on Hermes.
- [ ] Fixture tests will fail RED on the current no-op behavior for D1-D5 before implementation.
- [ ] Sibling repo resolution will come from `registry.yaml` and will cover Linux sibling roots, Windows `D:\` roots, and non-`/mnt/local-analysis` Linux roots without hardcoding one layout.
- [ ] Branch disposal will detect squash-merged PR heads and ancestry-merged branches, will protect open PRs/current branches/worktree-checked-out branches, and will avoid a vacuous naming regex.
- [ ] Worktree disposal will require `.wt-owner` markers written by worktree-creating automation; unmarked worktrees will remain protected but will count as blocked backlog.
- [ ] Stash handling will either drop only specific allowlisted automation-owned stashes after age/content checks or will raise a consumed alert threshold; it will never use `git stash clear` or an unfiltered drop loop.
- [ ] `daily-cleanup` will write durable semantic outcome state, and cron-health will fail when eligible backlog persists through N consecutive zero-disposal runs.
- [ ] Existing working surfaces will remain preserved: `repo-ecosystem-hygiene-audit.sh`, `cron-health-check.sh` baseline log/runtime checks, `cron_runtime.py` singleton, `git-lock-reaper`, and `return-to-main-guard`.
- [ ] No implementation will occur before user approval and `status:plan-approved`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Codex self-review r1 | MINOR | Review will find no remaining blocker after revisions; residual risks will be #3708 live apply dependency and fleet-only crontab evidence limits. |

**Overall result:** PASS after revision.

Revisions made based on review:
- The plan will sequence live deployment behind #3708 rather than implying YAML alone will make system cron work.
- The plan will include Windows/PowerShell wrapper protection and non-`/mnt/local-analysis` registry layouts.
- The plan will require RED tests for the current no-op cases, including true empty-backlog no-op versus failed cleanup no-op.
- The plan will recommend worktree creator `.wt-owner` markers instead of weakening the guard into age-only deletion.
- The stash policy will forbid broad cleanup and will require specific stash refs plus owner/content thresholds or consumed health alerts.

---

## Risks and Open Questions

- **Risk:** #3708 may take longer than #3707 code changes. #3707 may merge code/config only after approval, but live clockwork acceptance will remain blocked until #3708 will provide safe crontab apply.
- **Risk:** GitHub PR-head detection may hit API limits or auth failures. The implementation will need bounded calls, cached results per repo, and a fail-closed surface-only fallback.
- **Risk:** Worktree owner markers may not cover historical worktrees. Historical unmarked worktrees will be surfaced and counted as blocked backlog, not removed.
- **Risk:** Stash content classification may be too conservative. Unknown/human stashes will alert through cron-health rather than auto-drop.
- **Risk:** Local planning could not verify remote fleet crontabs without SSH. The implementation gate will require on-box read-only audit evidence before live apply.
- **Open:** N for cleanup no-op health failure will default to 3 consecutive runs unless the owner chooses a different fleet threshold during approval.

---

## Complexity: T3

**T3** — this will span cron scheduling, repo-disposal semantics, guard policy, fixture-driven destructive-action tests, machine-path contracts, and health monitoring. It will also depend on #3708 for live crontab deployment.
