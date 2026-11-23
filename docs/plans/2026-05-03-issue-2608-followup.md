# Plan: Issue [#2608](https://github.com/vamseeachanta/workspace-hub/issues/2608) — Rebase or close `fix/triage-punch-list-2026-05-02`

**Repo:** `digitalmodel` (separate git repo at `/mnt/local-analysis/workspace-hub/digitalmodel`)
**Branch:** `fix/triage-punch-list-2026-05-02`
**Branch tip:** `0faf6416` ("chore(sync): auto-sync 2026-05-02")
**Origin/main HEAD (at planning time):** `205b85b0`
**Status:** PLAN-DRAFT (planning-only; no git ops authorized)

## Issue Summary

A stale local branch in `digitalmodel` carries two commits not on `origin/main` by SHA. The substantive fix on the branch landed on main via squashed PR (#543) the next morning, leaving the branch ahead-by-2 / behind-by-10 with no useful divergence. Issue #2608 asks: rebase, close-as-superseded, or cherry-pick.

## Resource Intel — What's actually on the branch

### Commits unique to branch vs `origin/main` (`git log origin/main..fix/triage-punch-list-2026-05-02`)

| SHA | Subject | Classification | Evidence |
|---|---|---|---|
| `15d57451` | fix(ci): triage punch list — economics importorskip, curves.py deletion, drilling_riser CSV vendor, maxfail bump | **Already-on-main (squashed)** | Subject duplicate on main as `60d59565` (PR #543, merged 2026-05-02 05:57 CT). Per-file blob hashes for **all 6 files** the branch commit touches MATCH `origin/main` byte-for-byte: `test_economics.py` (5bbe205e), `quality-gates.yaml` (3db2b1f9), `drilling_riser/conftest.py` (1e371b63), `drilling_riser/fixtures/drilling_riser_components.csv` (ff82f5a7), `pyproject.toml` (81fda805); `naval_architecture/curves.py` deleted on both. Patch-id differs (`b92cf542` vs `fd921b8a`) only because PR #543 squashed in #2580 citation-fixture vendoring on top, not because the branch fix differs from what main now has. |
| `0faf6416` | chore(sync): auto-sync 2026-05-02 | **Superseded by main's seaborn commits** | Touches `uv.lock` only (4±2). The blob hash `0561238d` of `0faf6416:uv.lock` IS IDENTICAL to `origin/main:uv.lock`. Main reached the same lockfile via `4515cd01` ("fix(ci): unblock Quality Gates on seaborn + dev-machine paths (#2574)") and follow-on commits. |

### Commits on main missing from the branch (`git log fix/...~..origin/main`, 10 total)

`b1346acb` (#2580 citation fixture vendor), `60d59565` (#543, the merged twin), `48ab6457` (yml-utilities print→logger), `2dfa61e6` (FIXTURE_PROVENANCE.md), `08e9c333` (#2603 rudder_stock_torque re-export), `66b01f19` (#2614 Cat A solver imports), `d5fe5df8` (#2614 Cat B mock alignment), `d6a42770` (#2614 Cat C AQWA reconcile), `abeea542` (full pytest log artifact), `205b85b0` (#2614 Cat D output writers).

### Worktree dirty state

Per task scope: do not interpret. Caller's cleanup script may have produced uncommitted edits, but they are out of scope for branch-disposition decision.

## Decision: Close-as-superseded (delete branch)

**Recommendation:** Confirm equivalence one final time on a clean checkout, then delete `fix/triage-punch-list-2026-05-02` locally and on `origin` if it was ever pushed.

### Rationale

1. Every byte the branch's `15d57451` was supposed to introduce IS on `origin/main` today, verified by per-file blob-hash equality on all 6 touched files. PR #543 is the canonical landing.
2. The auto-sync commit's `uv.lock` blob is identical to `origin/main`'s. There is no lockfile-state delta to recover.
3. Rebasing produces an empty rebase (every commit drops as already-applied) — wasted ceremony.
4. Cherry-picking is moot: nothing remains to pick.

### Why NOT rebase

`git rebase origin/main` would mark both branch commits as already-applied (patch-equivalent by file content even though patch-id differs by a single fixture stanza). Result is an empty branch pointing at `origin/main`. No PR to open.

### Why NOT cherry-pick

There is no "novel" work on the branch. Cherry-picking would re-introduce changes already on main and create no-op commits.

## Files To Change

**None in any repo.** This is a git-state hygiene issue. The deliverable is a deleted ref, not a code change.

Side-effect (out of plan scope): the `digitalmodel` worktree may need `git switch main && git pull --ff-only` after branch deletion if the user is currently checked out on the stale branch.

## Acceptance Criteria

1. Final equivalence check passes on a clean checkout: `git log origin/main..fix/triage-punch-list-2026-05-02` lists exactly `0faf6416` and `15d57451`, and per-file blob diff vs `origin/main` for the 6 files the branch touches is empty.
2. Branch deleted locally: `git branch -D fix/triage-punch-list-2026-05-02` (force flag required because the branch is not merged by SHA).
3. Branch deleted on remote IF it was ever pushed: `git push origin :fix/triage-punch-list-2026-05-02`. (Verify with `git ls-remote origin 'refs/heads/fix/triage-punch-list-2026-05-02'` first.)
4. Issue [#2608](https://github.com/vamseeachanta/workspace-hub/issues/2608) closed with a comment linking PR #543 as the canonical landing for the fix and citing the per-file blob-hash evidence above.
5. Reflog of the deleted branch retained for the default 90 days as the rollback path.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| The "superseded" judgment is wrong on a file we didn't enumerate. | Low | Branch's tree drift is fully bounded by `git log origin/main..fix/...` (only 2 commits) and the 6 files in their union. We checked all 6. | Add one more pre-deletion gate: `git diff origin/main fix/triage-punch-list-2026-05-02 -- .` should be empty or trivial. If non-empty, halt. |
| Branch was pushed to origin and another machine has work pending against this ref. | Low | Lost work | Check `git ls-remote origin` before deletion. If remote ref exists, post advance notice on issue #2608 with 24h delay before push-delete. |
| Reflog rotates before recovery is needed. | Very low | Lost SHAs | Tag the branch tip locally before deletion: `git tag archive/triage-punch-list-2026-05-02 0faf6416`. Tag is permanent until manually deleted. |
| Caller's cleanup script left uncommitted changes in the worktree on this branch. | Medium (out of scope) | Worktree dirty after branch delete | Worktree dirty state is orthogonal — `git switch main` will preserve unstaged work or block on conflict; do not infer the branch needs preserving from worktree dirtiness alone. |
| User wants the audit trail of `15d57451` (verbose body explaining the 5 fixes) preserved. | Medium | Authorship credit lost | The merged commit `60d59565` carries the same body verbatim plus PR-merge metadata. No loss. |

## Rollback

1. Pre-deletion: tag `archive/triage-punch-list-2026-05-02` at `0faf6416`. This makes deletion functionally reversible for years, not 90 days.
2. Recovery if branch ever needed back: `git branch fix/triage-punch-list-2026-05-02 archive/triage-punch-list-2026-05-02`.
3. If reflog and tag both lost (catastrophic): the SHAs `0faf6416` and `15d57451` are recorded in this plan and in issue #2608 audit trail — `git fetch origin` won't help (never on origin under that name), but `git fsck --lost-found` would surface them while objects remain in the repo's pack files.

## Out of Scope

- Worktree-cleanup logic the caller mentioned. That is a separate hygiene step.
- Backporting any of the 10 main-side commits the branch is missing — those are forward-only, not branch-disposition-related.
- Closing PRs that referenced the branch (none exist; branch was never PR'd).

## Execution Sequence (when user approves)

1. `git -C digitalmodel fetch origin` — refresh.
2. Re-run the equivalence check from Acceptance Criteria #1. Halt if any file diverges.
3. `git -C digitalmodel ls-remote origin refs/heads/fix/triage-punch-list-2026-05-02` — check remote.
4. `git -C digitalmodel tag archive/triage-punch-list-2026-05-02 0faf6416`.
5. `git -C digitalmodel branch -D fix/triage-punch-list-2026-05-02`.
6. If remote ref existed: `git -C digitalmodel push origin :fix/triage-punch-list-2026-05-02`.
7. Comment on [#2608](https://github.com/vamseeachanta/workspace-hub/issues/2608): cite PR #543, paste blob-hash table from Resource Intel.
8. Close [#2608](https://github.com/vamseeachanta/workspace-hub/issues/2608).
