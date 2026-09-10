# Plan for #3705: repository_sync auto-commits to protected main, stranding unpushable commits

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-08-12
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3705
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-08-12-plan-3705-claude.md | ...-codex.md | ...-agy.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/repository_sync-auto:150-174` — `_auto_sync_one()` core logic. The function commits locally (line 150-151), then pushes (lines 163-174). Push failure due to branch protection (`GH013`) falls through to `status="push-failed"` (line 172). The commit at line 150 is NOT rolled back; the repo is permanently ahead of `origin/main`.

  ```bash
  # line 150-151:
  if git commit -m "chore(sync): auto-sync $date_str" 2>/dev/null; then
      committed=true
  # ...
  # line 163-174:
  elif push_out=$(git push 2>&1); then
      pushed=true
  elif echo "$push_out" | grep -Eiq "archived|read[- ]only"; then
      status="skipped-readonly"
  else
      status="push-failed"   # ← GH013 lands here; commit already committed, never reset
  fi
  ```

- Found: `scripts/repository_sync-auto:169` — `archived|read-only` guard already shows the correct pattern: detect specific rejection strings, handle gracefully. Branch protection needs the same treatment.

- Found: `scripts/repository_sync:394-406` — parallel push logic in the interactive script; same `archived|read-only` guard, same gap for GH013.

- Found: `tests/sync/test_sync_cadence_helper.py` — 67 lines; tests sync cadence timing logic only. No test for push-rejection scenarios.

- Gap: No detection of `GH013` / branch-protection rejections in either sync script.
- Gap: No rollback of a local commit after a protection-gated push failure.
- Gap: No readiness/equality check that surfaces repos with `ahead_main > 0` due to stranded sync commits.

### Standards

Not applicable — harness/sync script, not an engineering calculation.

### LLM Wiki pages consulted

No relevant wiki pages.

### Documents consulted

- Issue #3705 body — confirmed on two repos during 2026-07-29 fleet reconcile: `digitalmodel` (ace-linux-2) had 2 unpushable sync commits dating back 18 days; `deckhand-sandbox` had 1. The push error is `GH013: Repository rule violations found for refs/heads/main`.
- `scripts/repository_sync-auto` full text — `_auto_sync_hub()` (lines 183-218) has a separate commit+push path for the hub repo itself; it does NOT call `_auto_sync_one()` and has a simpler push with no stranded-commit protection.
- `scripts/repository_sync` full text — interactive sync script has the same pattern at lines 394-406 in `push_repo()`.
- Related issue #3702 — STALE-CHECKOUT deadlock; `ahead_main != 0` is one of the three fields that masks all 27 equality dimensions. Stranded sync commits drive `ahead_main` non-zero and feed directly into this deadlock.
- Related issue #3704 — reconcile-ecosystem.sh scans stale refs without fetching; a sibling that is blocked from pushing will also have stale remote refs.
- `tests/sync/test_sync_cadence_helper.py` — read to confirm no existing push-rejection test coverage.

### Gaps identified

- `_auto_sync_one()` does not detect GH013 / protection-gated rejections; does not roll back the stranded commit.
- `_auto_sync_hub()` has the same gap (simpler path; same branch).
- `push_repo()` in `repository_sync` has the same gap (interactive use; lower urgency since human can recover, but should match).
- `reconcile-ecosystem.sh` does not surface repos where `ahead_main > 0` due to stranded sync commits.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-08-12 via `gh issue view`):
- `#3705` — OPEN — bug(sync): repository_sync auto-commits to protected main branches, stranding commits that can never be pushed
- `#3702` — OPEN — (STALE-CHECKOUT deadlock; fed by this bug)

**File existence** (`ls` 2026-08-12):
- EXISTS: `scripts/repository_sync-auto`
- EXISTS: `scripts/repository_sync`
- EXISTS: `tests/sync/test_sync_cadence_helper.py`
- EXISTS: `scripts/readiness/reconcile-ecosystem.sh`
- MISSING (new — this plan creates): `tests/sync/test_auto_sync_protected_branch.py`

**Line excerpts** (`sed -n 148,175p scripts/repository_sync-auto`):
```bash
        if git commit -m "chore(sync): auto-sync $date_str" 2>/dev/null; then
            committed=true
        else
            echo "$repo|$staged|false|false|commit-failed" > "$result_file"; return 0
        fi
    fi

    # Update only after local tracked changes are committed; use fast-forward-only.
    if ! _safe_ff_only_pull; then
        echo "$repo|$staged|$committed|false|warn-pull-failed" > "$result_file"; return 0
    fi

    local push_out
    if git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1 \
       && [ -z "$(git log @{u}.. 2>/dev/null)" ]; then
        pushed=false
    elif push_out=$(git push 2>&1); then
        pushed=true
    elif echo "$push_out" | grep -Eiq "archived|read[- ]only"; then
        status="skipped-readonly"
    else
        status="push-failed"
    fi
```

**Gap proof** (`grep -n "GH013\|branch.protection\|protected" scripts/repository_sync-auto`):
- No output → confirms no branch-protection detection exists.

**Reproduction proofs** (per issue body, 2026-07-29):
```
remote: error: GH013: Repository rule violations found for refs/heads/main.
remote: - Changes must be made through a pull request.
remote: - 2 of 2 required status checks are expected.
```
- `digitalmodel` on ace-linux-2: 2 stranded `chore(sync): auto-sync` commits, oldest from 2026-07-11 (18 days silent failure)
- `deckhand-sandbox` on ace-linux-2: 1 stranded commit
- Reproduced at: 2026-07-29 (per issue body)
- Failure mode matches issue claim: YES — commits accumulate permanently; operator cannot distinguish them from intentional local work.

<!-- Verification: 6 distinct sources (issue body + _auto_sync_one lines + _auto_sync_hub path + repository_sync push_repo + test file + issue #3702). Minimum 3 satisfied. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-08-12-issue-3705-sync-protected-branch.md |
| Primary fix | `scripts/repository_sync-auto` |
| Secondary fix | `scripts/repository_sync` |
| Readiness surface | `scripts/readiness/reconcile-ecosystem.sh` |
| New tests | `tests/sync/test_auto_sync_protected_branch.py` |
| Plan review — Claude | scripts/review/results/2026-08-12-plan-3705-claude.md |
| Plan review — Codex | scripts/review/results/2026-08-12-plan-3705-codex.md |
| Plan review — Agy | scripts/review/results/2026-08-12-plan-3705-agy.md |

---

## Deliverable

After this issue is done: `_auto_sync_one()` and `_auto_sync_hub()` in `repository_sync-auto` will detect branch-protection push rejections (GH013), roll back the stranded local commit with `git reset --soft HEAD~1`, and emit a `skipped-protected` status — leaving the repo in clean `ahead_main=0` state rather than permanently stranded. A new TDD test suite verifies the rollback behavior in a hermetic local-repo fixture.

---

## Pseudocode

```
# In _auto_sync_one(), after the push attempt:
elif push_out contains "GH013" OR "required status checks" OR "pull request" (case-insensitive):
    # The branch is protection-gated. Undo the commit so the working copy stays clean.
    if committed == true:
        git reset --soft HEAD~1     # un-commit but keep staged changes
        committed = false
        staged = true               # changes are still staged; honest about state
    status = "skipped-protected"
    # Emit the push output to stderr so operator has evidence
    echo "$push_out" to stderr
else:
    status = "push-failed"          # (unchanged — non-protection failures still fail)

# In _auto_sync_hub(), same detection + reset at the analogous push:
elif push_out contains protection patterns:
    git reset --soft HEAD~1
    echo "workspace-hub: push rejected (branch protection) — commit rolled back" to stderr

# In reconcile-ecosystem.sh scan_repo():
# After checking stash and lock state, add:
    ahead_count=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
    if [[ "$ahead_count" -gt 0 ]]; then
        add NEEDS-APPROVAL "$repo" \
            "local main is $ahead_count commit(s) ahead of origin — may be stranded sync commits" \
            "git log --oneline origin/main..HEAD  # inspect; git reset --soft if they are sync churn"
    fi
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/repository_sync-auto` | Add GH013 detection branch + `git reset --soft HEAD~1` rollback in both `_auto_sync_one()` and `_auto_sync_hub()` |
| Modify | `scripts/repository_sync` | Add same detection in `push_repo()` (interactive use; match behaviour) |
| Modify | `scripts/readiness/reconcile-ecosystem.sh` | Add `ahead_main` staleness check in `scan_repo()` so stranded commits surface in the equality plan |
| Create | `tests/sync/test_auto_sync_protected_branch.py` | TDD suite using hermetic local bare+clone fixtures to verify rollback behaviour |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_auto_sync_detects_gh013_in_push_output` | Static: `_auto_sync_one` shell text contains GH013 or equivalent detection pattern | Script text | Pattern present |
| `test_auto_sync_one_resets_commit_on_protection_failure` | Hermetic: after a push that fails with GH013-like error, the local branch is NOT ahead of its pre-commit state | Bare remote repo configured with a pre-receive hook that rejects with "GH013: Repository rule violations"; dirty working copy | After sync run: `git rev-list --count origin/main..HEAD` == 0; result file contains `skipped-protected` |
| `test_auto_sync_one_does_not_reset_on_other_failures` | Hermetic: a push failure that is NOT protection-related does not roll back the commit | Bare remote with hook that rejects with "internal server error" | After sync run: `git rev-list --count origin/main..HEAD` == 1; result file contains `push-failed` |
| `test_reconcile_ecosystem_surfaces_ahead_main` | Static: reconcile-ecosystem.sh checks `ahead_main` count and adds an action for non-zero | Script text | `rev-list.*origin/main..HEAD` or equivalent present in scan_repo |
| `test_auto_sync_hub_resets_on_protection_failure` | Hermetic: `_auto_sync_hub` path also rolls back commit on GH013 rejection | Same fixture pattern for workspace-hub path | Repo not permanently ahead; stderr contains rollback message |

---

## Acceptance Criteria

- [ ] A repo on a protected branch: after an auto-sync cycle, `git rev-list --count origin/main..HEAD` == 0 (no stranded commits).
- [ ] The result file for that repo contains `skipped-protected`, not `push-failed`.
- [ ] A non-protection push failure (network, server error): the commit is NOT rolled back; `push-failed` status is set.
- [ ] `reconcile-ecosystem.sh` flags repos with `ahead_main > 0` with NEEDS-APPROVAL action.
- [ ] All new tests pass: `bash -c 'cd tests/sync && uv run pytest test_auto_sync_protected_branch.py -v'`
- [ ] `bash -n scripts/repository_sync-auto` exits 0 (syntax check).
- [ ] `bash -n scripts/repository_sync` exits 0 (syntax check).
- [ ] Existing `tests/sync/test_sync_cadence_helper.py` still passes.
- [ ] Existing `tests/readiness/test_reconcile_ecosystem.py` static invariant tests still pass.

---

## Adversarial Review Summary

<!-- To be filled after adversarial review completes. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | — |
| Codex | pending | — |
| Agy | pending | — |

**Overall result:** pending

---

## Risks and Open Questions

- **Risk:** `git reset --soft HEAD~1` requires a clean index after reset. If the commit included a `git add -u` (line ~147 in `_auto_sync_one`), the files will be staged again after reset. The result file will say `staged=true, committed=false` — this is the correct state (changes still pending) and should be documented in the result format comment.
- **Risk:** The pre-receive hook fixture for hermetic tests may not be available on all CI environments. Use a `pre-receive` shell hook in a bare repo (no external service needed) — this is fully offline.
- **Risk:** `_auto_sync_hub()` has a simpler push path (`git push 2>/dev/null`) that swallows stderr. The protection rollback requires capturing stderr: `push_out=$(git push 2>&1)`. This changes the hub path from fire-and-forget to captured — acceptable since hub is always workspace-hub, which is the least likely to have branch protection, but the fix must still handle it correctly.
- **Open:** Should `skipped-protected` be surfaced in the nightly digest differently from `push-failed`? Recommendation: yes — `skipped-protected` is expected/healthy; `push-failed` is a network/auth problem. Digest rendering is out of scope for this issue; file a follow-on.
- **Open:** Backfill — the existing stranded commits on ace-linux-2 need disposition. These are `chore(sync): auto-sync` commits with clean diffs; they can be discarded with `git reset --soft` after confirming the diff is pure sync churn. This is an operational step, not code, and is out of scope for this plan. Operator must handle it manually after the fix lands.
- **Open:** Should this also detect `GH006` (protected branch push not allowed) and `GH007` (branch push review required)? Add all three patterns to be safe: `GH006|GH007|GH013|required status checks|pull request` (case-insensitive). Implementation decision; widen the pattern in the fix.

---

## Complexity: T2

**T2** — three files modified (repository_sync-auto, repository_sync, reconcile-ecosystem.sh), one new test file created, hermetic fixture setup required for the tests.
