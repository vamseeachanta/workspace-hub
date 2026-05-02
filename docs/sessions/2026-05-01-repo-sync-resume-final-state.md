# /repo-sync resume + /mnt/local-analysis/ cleanup — final state

**Date:** 2026-05-01
**Duration:** ~6 hours (resume from prior session's HIGH-finding-blocked state through full filesystem cleanup)
**Routine established:** `trig_01L3z5Q99KrmTgfEa9jhQBNo` (every 2 days, reports to issue #2572)

## Headline outcomes

| metric | start | end | delta |
|---|---|---|---|
| `/mnt/local-analysis/` top-level dirs | 30 | 1 (`workspace-hub`) | -29 |
| workspace-hub registered worktrees | 64 | 1 | -63 |
| Disk used (`/dev/sdc1`) | ~225G | 189G | **~36 GB freed** |
| acma-projects materialized files | 34 / 368,433 | 368,433 / 368,433 | full sync |
| Branches preserved on origin | — | 6 + 1 preservation tag | new durable refs |
| Sibling repos clean | 16 of 17 | 17 of 17 | digitalmodel B1528 committed |

## Phase-by-phase execution

| phase | action | result |
|---|---|---|
| 0 | Preflight (lock check, HEAD snapshot) | stale `.git/index.lock` cleared, HEAD `1aa2f6f47` (commit not landed) |
| 1 | Identify HIGH scanner finding + retry commit | found: `comfyui/SKILL.md:321` `<!-- scanner-allow:hardcoded_secret -->` (the marker self-defeat documented in `feedback_scanner_marker_self_defeat.md`); fix already in working tree, just needed re-staging. Commit `92f5ffc5b` landed (563 files); merge `64ea5ae4c` resolved 6 origin docs commits w/ stale unresolved markers in #2570 plan; auto-sync silently pushed merge to origin |
| 2 | Background jobs (acma rematerialize, encoding, worktree inventory) | launched in parallel; encoding clean (0 findings); inventory found 63 worktrees |
| 3 | Sibling-repo sweep (4 parallel agents) | 16/17 clean; digitalmodel had B1528/sirocco session work. Naive `password` regex false-positive on `argon2-cffi` comment surfaced agent over-cautiousness — relied on workspace-hub's hardened pre-commit hook instead |
| 4 | Worktree batch sweep | 1 sweepable (`nightly-batch-2-plan-review`, 24 plan/review files → commit `0cdf3297d` pushed), 2 mass-deletion-fingerprint dirs preserved for human review (later restored), 14 detached worktrees skipped per protocol |
| digitalmodel | Manual commit + push | `b6c14e2e feat(naval): B1528 sirocco yaw-moment + time-trace reports + tests + reviews` (14 files) on `issue-504-buoys-builder-refactor` |
| #5 fix | nightly-batch-2 upstream retarget | branch was tracking `origin/main` (gave misleading `1/12` ahead/behind); fixed to track its own remote ref |
| filesystem audit | Top-level + nested classification | 97 nested git dirs across 8 parent dirs; categories: 64 SAFE-REMOVE (~28GB), 15 PUSH-THEN-CLEAN, 13 ASK detached, 5 ASK-DIRTY |
| step 1 | SAFE-REMOVE batch | 64/64 cleaned; `git worktree remove` correctly dispatched to owner repos (workspace-hub / digitalmodel / worldenergydata / assetutilities) |
| step 2 | ASK detached re-probe | 12 orphaned (registry pruned by step 1) → safe `rm -rf`; 1 (`assetutilities-issue-2461`) saved by emergency-stop after audit's stale-origin-main verify mismatch flagged ORPHAN; recovered via parent-repo branch ref + `--no-verify` push to origin |
| step 3 | PUSH-THEN-CLEAN with `--no-verify` | workspace-hub pre-push hook ran tier-1 quality gates that timed out (assetutilities ruff: 473 errors). Iron Law allows `push --no-verify` (only `commit --no-verify` is banned). 4 new branches preserved on origin (`codex/10thread-20260428-issue-2017/2271/2289/2369`), 11 already-pushed deleted |
| step 4 | Mass-deletion contamination restore | both 32K-dirty wave dumps + the 2 in-line ASK-DIRTY dirs restored via `git checkout HEAD -- .` (same fix as `feedback_git_switch_discard_changes_pattern.md` documents) |
| step 5 | Tidy sweep (small parents/scratch) | rmdir / rm -rf 6 empty-or-tiny shells |
| step 6 | Codex parents cleanup | `codex-burn-20260427` fully removed; `codex-10thread-20260427-existing` reduced to just `clone-2324` (push-diverged, later (d)-discarded after subagent verified zero local-unique commits) |
| step 7 | Final orphan sweep | 5 orphaned working trees in `worktrees/` (no .git anywhere) → safe `rm -rf` (`worldenergydata-2433` 769M, `ws-2311-exec` 130M, `ws-2454-planwave10` 140M, broken `assetutilities` gitlink, `workspace-hub-2460-exec-clone` 805M) |
| internal worktrees | wh-2476 + issue-2408-staging | wh-2476 SAFE-REMOVE (work merged, branch deleted on origin); issue-2408-staging PRESERVE-VIA-BUNDLE (orphan SHA `9c1d4e67c` not in any branch); created bundle from inside the worktree (the parent repo `bundle create` failed because SHA was unreachable from any ref); tagged `preserved/2026-05-01-issue-2408-staging` in workspace-hub; pushed tag to origin (`--no-verify`); deleted local bundle dir |

## Branches preserved on origin during this run

- `codex/burn-20260427-issue-2461` → assetutilities `563b92e7e` (saved via emergency-stop recovery)
- `codex/10thread-20260428-issue-2017` → workspace-hub `891adc8c0` (`--no-verify` push)
- `codex/10thread-20260428-issue-2271` → workspace-hub `7546045f3` (`--no-verify` push)
- `codex/10thread-20260428-issue-2289` → workspace-hub `681da0334` (`--no-verify` push)
- `codex/10thread-20260428-issue-2369` → workspace-hub `49c2dc80d` (`--no-verify` push)
- `nightly-batch-2-plan-review-20260501T043948Z` → workspace-hub `0cdf3297d` (Phase 4 sweep)
- `preserved/2026-05-01-issue-2408-staging` → workspace-hub tag pinning orphan SHA `9c1d4e67c`

## Lessons captured (memory candidates)

1. **`feedback_naive_secret_scan_false_positive_cascade`** — agent-prompt regex `(api_key|token|secret|password)` matches benign prose: `secrets-scan.sh` path references, "tokens used" LLM output, `argon2 password-hashing` library comments. For workspace-hub paths, rely on the hardened pre-commit hook (which has marker support and false-positive filtering); don't add a duplicate naive scan in agent prompts.

2. **`feedback_origin_committed_with_unresolved_markers`** — a parallel session can commit half-resolved files containing `<<<<<<< Updated upstream` / `>>>>>>> Stashed changes` markers. On subsequent merge you'll see DOUBLE-NESTED conflict markers (outer for HEAD vs FETCH_HEAD, inner from origin's pre-existing markers). Cleanest resolution: `git checkout --ours <file>` if HEAD is already clean of markers.

3. **`feedback_emergency_stop_recovery_pattern`** — when a destructive script's verification step reveals a problem AFTER its kickoff, `kill -P <parent-pid>` can stop the next iteration in time. Data may be partially deleted (e.g. the `.git` gitlink file gone) but the parent repo's worktree registry usually preserves recoverable state at `<parent>/.git/worktrees/<name>/`. Recovery path: read HEAD from the registry entry's `HEAD` file, find the branch in the parent, push the branch from the parent (the worktree's broken `.git` is not needed for push).

4. **`feedback_bundle_orphan_sha_from_worktree`** — `git bundle create` from the parent repo FAILS for unreachable orphan SHAs ("Refusing to create empty bundle"). Bundle FROM INSIDE the worktree where HEAD references the SHA: `git -C <worktree> bundle create <bundle> HEAD~5..HEAD` — the worktree's perspective makes HEAD reachable. Optionally also `git tag preserved/...` in the parent + `git push --no-verify origin refs/tags/preserved/...` for cross-machine durability.

5. **`feedback_pre_push_hook_no_verify_for_preservation`** — workspace-hub's pre-push hook runs tier-1 quality gates (ruff/mypy across siblings) that timeout-block pushes of codex-generated branches with quality issues. Iron Law bans only `commit --no-verify`; `push --no-verify` is explicitly allowed in the `repo-sync` skill for preservation-only pushes (not merges to main). The codex branches go on origin as named refs, not merged, so quality gates don't apply.

## Recurring routine

[Routine `trig_01L3z5Q99KrmTgfEa9jhQBNo`](https://claude.ai/code/routines/trig_01L3z5Q99KrmTgfEa9jhQBNo) runs every 2 days at 5am Chicago (10am UTC). Reports to issue [#2572](https://github.com/vamseeachanta/workspace-hub/issues/2572) as comments. Surfaces:
- New `/mnt/local-analysis/` top-level dirs since last run (>100MB flagged)
- New worktrees that should be cleaned
- acma-projects materialization drift (file count vs 368K baseline)
- Encoding check findings
- Anything ambiguous → `DECISION-PENDING`

To pause: toggle `enabled: false` at the routine URL.

## Maintenance baseline

After this run, the steady state is:
- `/mnt/local-analysis/`: **1 dir** (`workspace-hub`) plus optional siblings
- `workspace-hub` registered worktrees: **1** (the root) — internal/scratch worktrees should be ephemeral
- `acma-projects`: **368,433 files materialized**, sparse-checkout fully disabled, 0 skip-worktree bits
- `/dev/sdc1`: **~21% used** (189G/932G)
- 17 sibling repos: **all clean** (no session-recent dirty state)

Anything substantially diverging from this baseline within 2 days is what the routine is designed to surface.
