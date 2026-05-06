# Branch & Worktree Cleanup Stream — 2026-05-05

**Scope:** ecosystem-wide cleanup of accumulated worktrees, stale branches, and abandoned WIP across the 24 repos under `workspace-hub`.

**Outcome:** minimal branch surface (4 surviving branches, all with defined forward paths) and durable artifacts for recovery + future-session reuse.

## Final Branch Surface

Every branch listed has a clear next-action. No "unknown WIP" remains in the ecosystem.

| Repo | Branch | Commits | Forward path |
|---|---|---:|---|
| workspace-hub | `chore/llm-wiki-spinout-cleanup` | 1 | PR vamseeachanta/workspace-hub#2649 OPEN — review/merge to complete the spinout |
| digitalmodel | `feat/2346-prospect-pipeline-canonical-adapter` | 1 | PR vamseeachanta/digitalmodel#586 OPEN — opened today, 1,760 lines GTM prospect pipeline |
| digitalmodel | `feat/2458-multibody-orcawave-benchmark` | 1 | PR vamseeachanta/digitalmodel#585 OPEN — opened today, multibody benchmark fixture |
| worldenergydata | `docs/handoff-2026-05-03-lt-epic-closed` | 18 | active multi-issue WIP, pushed to origin, will be split into per-feature PRs later |

## Stream Totals

| Action | Count |
|---|---:|
| Worktrees removed | 14 |
| Local branches deleted | 39 |
| Remote stale refs deleted | 4 |
| Recovery tags placed (`archive/closed-*`) | 19 |
| PRs opened | 2 (digitalmodel#585, #586) |
| PRs closed with explanation | 1 (worldenergydata#340) |
| Issue comments posted | 4 (workspace-hub#2458, #2346; worldenergydata#340; digitalmodel#504) |
| Security incidents resolved | 1 (Telegram bot token leak — see below) |
| New feedback memories logged | 1 (`feedback_credential_issuer_copy_paste_leak.md`) |

## Security Incident (resolved)

`aceengineer-admin` branch `codex/burn-20260427-issue-2493` commit `bfe00da chore(admin): note telegram bot token in private admin doc` contained a live Telegram Bot token (`8288748751:...`) pasted verbatim from BotFather output into `admin/software.md`.

**Resolution:**
1. Token revoked via BotFather `/revoke` (user, out-of-band)
2. Branch deleted local + origin (no archive tag — would have re-anchored the leak commit as reachable)
3. Local pack purged: `git reflog expire --expire=now --expire-unreachable=now --all && git gc --prune=now --aggressive`
4. Verified: `git cat-file -e bfe00da` returns "Not a valid object name" — physically removed from local storage
5. Repo is private, so blast radius is limited to anyone with read access to the repo via leaked credentials. Token is revoked so historical exposure is academic.

**Memory captured:** `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_credential_issuer_copy_paste_leak.md` (indexed in `MEMORY.md:72`). Future sessions will recognize the pattern and apply the same resolution recipe.

## Ecosystem Patterns Surfaced

These show up across multiple branches, worth keeping in mind:

1. **Stacked-feature-branch + same-day batch ship**: 2026-04-16 worldenergydata batch (#286 → #299 → #298 → #290 → #293) — 5 PRs merged within 41 minutes, leaving 5 stacked-on-top branches all orphaned by squash-merges. Consider building one PR per branch off main rather than stacking when shipping in batches.

2. **`git cherry` false-positives on squash-merged content**: patch-id check can't equate squash-merge results to original split commits. Branches whose work landed via squash will look like "+ unique commits" forever. Always also check if a merged PR exists for the issue and whether expected output files are on main before treating "+ unique" as real WIP.

3. **`grep -vE '^\*'` filter bug in branch-survey one-liners**: drops the currently-checked-out branch from results, silently hiding it from triage. Surfaced 3 missed branches in this stream (worldenergydata, assethold, aceengineer-admin). Prefer `git for-each-ref refs/heads --format='%(refname:short)'` for comprehensive surveys.

4. **Auto-sync as silent pusher**: auto-sync pushes local-ahead commits during contention resolution AND keeps active branches synced to origin. Several of the deleted branches had origin refs we hadn't explicitly created. Useful to know — local backup is more reliable than expected.

5. **Auto-merge `--delete-branch` is healthy housekeeping**: 4 branches self-resolved during this session because `gh pr merge --delete-branch` cleaned them up after PRs merged. The branches that *don't* get cleaned up (like the assethold codex/burn-2459 case) are the ones where the auto-merge config didn't pass that flag — worth reviewing the org-wide setting.

6. **Codex/burn-* naming was scratch convention**: when promoting a codex/burn branch to a real PR, cherry-pick onto a fresh `feat/<issue>-<short-name>` branch. Avoids force-push, gives a clean small diff (vs the stale-base 100+ file noise), and properly names the branch for review.

7. **Closed-issue + unique-content branch heuristic** caught 12 stale branches. False positive rate: ~2 of 12 needed nuance (worldenergydata `nightly/2451` was superseded-not-merged, requiring PR-close-with-explanation; aceengineer-admin `codex/burn-2493` had 1 post-closure unique commit that turned out to be the security leak). Worth applying as default triage but always verify before delete.

## Recovery Tags Available

19 archive tags placed across repos for branches that were deleted:

```
digitalmodel:
  archive/closed-2455-issue-2457-canonical-spec-proof
  archive/closed-2580-fix-2574-quality-gates-infra

worldenergydata:
  archive/closed-2433-codex-nextwave-20260427-issue-2433
  archive/closed-2451-nightly-2451-worldenergydata
  archive/closed-288-feat-288-query-api-pr
  archive/closed-290-feat-290-ms-cli
  archive/closed-293-docs-293-notebooks
  archive/closed-298-feat-298-mnt-ace-catalog
  archive/closed-300-chore-300-scripts-consolidate

aceengineer-website:
  archive/closed-2357-codex-burn-20260427-issue-2357
  archive/closed-2463-codex-burn-20260427-issue-2463

assetutilities:
  archive/closed-2461-codex-burn-20260427-issue-2461

assethold:
  archive/closed-2459-codex-burn-20260427-issue-2459
```

Tags are local-only (not pushed to origin). Recovery: `git checkout archive/<tag>` or `git branch <new-name> archive/<tag>`. Tags don't expire — they're durable across sessions until explicitly deleted.

**Deliberately not tagged:** `aceengineer-admin codex/burn-20260427-issue-2493` — security purge required removing the leak commit's reachability, so no archive tag was created.

## Follow-ups for Next Session

- [ ] Review and merge the 2 digitalmodel PRs opened today (#585, #586)
- [ ] Decide on workspace-hub#2649 (llm-wiki spinout cleanup) — review or further iteration
- [ ] Update `digitalmodel` issue #504 label from `status:working` to `status:done` (PR #538 delivered the work; comment posted requesting closure)
- [ ] Optional: split the 18-commit `worldenergydata docs/handoff-2026-05-03-lt-epic-closed` branch into per-category PRs (plan-review docs, GTM economics features, fix #384, capability drift checks, production decline notebook). Categorization tabulated in branch 8 review notes from this session
- [ ] Optional: contact GitHub Support to purge unreachable orphan commits across the repos where branch deletions happened (cosmetic; revoked tokens make this academic)
