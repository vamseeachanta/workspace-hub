# Archived Skill: `overnight-verify-close-and-blocker-conversion`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/overnight-verify-close-and-blocker-conversion`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/overnight-verify-close-and-blocker-conversion`
Consolidation date: 2026-04-29

---

---
name: overnight-verify-close-and-blocker-conversion
description: Use overnight Claude lanes to clear stale-open GitHub issues by verification-first closure, and convert blocked PR-repair attempts into dedicated blocker issues instead of speculative edits.
triggers:
  - Overnight batch includes several status:plan-approved issues that may already be landed on origin/main
  - Open issues remain stale despite landed commits and prior implementation comments
  - A PR-repair lane discovers repo-wide CI/governance drift outside its owned paths
---

# Overnight verify-close and blocker conversion

## When to use

Use this in workspace-hub-style overnight batches when:
- several approved GitHub issues look suspiciously like they are already done
- issue comments mention landed commits, review artifacts, or approved revision passes
- you want backlog reduction without risky duplicate implementation
- a repair lane for a specific PR may actually be blocked by repo-wide CI drift

## Core idea

Do not default to implementation just because an issue is open.
For stale-open approved issues, assign **verification-first closeout lanes**.
For blocked PR repair, if the true root cause is outside the lane's owned paths, stop and create a dedicated blocker issue the same night.

## Part 1: verification-first closeout lanes

Create one lane per issue.
Each lane should have write ownership only over:
- one result artifact, e.g. `.nightly-results/<date>-issue-<n>.md`
- the GitHub comment/close actions for that issue

### Required verification sequence

1. `git fetch origin --quiet`
2. identify the candidate landing commit from issue comments or recent history
3. prove the commit is on `origin/main`
   - prefer `git merge-base --is-ancestor <commit> origin/main`
   - `git branch -r --contains <commit>` can be a secondary check only
4. verify expected artifacts exist on `origin/main`
   - use `git ls-tree`, direct file reads, or current checkout inspection after sync
5. map acceptance criteria to concrete evidence
   - for design/governance/doc issues, deterministic section/path inspection is often the right validator
   - do not force a runtime test if the deliverable is a document contract or review package
6. if auto-sync / merge-race risk exists, verify **content parity**, not just history containment
   - compare the landed commit's artifact content against `origin/main`
   - example: `git diff <candidate-commit> origin/main -- <artifact-path>` should be empty or have an explicitly explained delta
7. write the evidence report artifact
8. post the closeout comment first
9. close the issue second, in a separate command

### Why comment first

`gh issue close --comment` can be fragile in races or on already-closed issues.
Posting the evidence comment first makes the proof durable even if the close step races or becomes redundant.

### Stronger verification rules learned in practice

Use both of these before closing a stale-open issue:
- **history containment**: `git merge-base --is-ancestor <commit> origin/main`
- **content parity**: `git diff <candidate-commit> origin/main -- <artifact-path>` should be empty unless you can explain the delta

Reason:
- history containment alone does not prove the intended artifact content survived a merge race or later overwrite
- in auto-sync / concurrent-writer repos, the same issue can need both ancestry proof and artifact parity proof before "already done" is defensible

Operational note:
- leave the `status:plan-approved` label alone on a now-closed issue unless there is a separate governance reason to clean it up; that label is evidence of planning state, not an error by itself

### Good fit

This pattern worked well for stale-open issues where:
- revision/implementation commits were already on `origin/main`
- review artifacts and approval markers existed
- the issue simply had never been formally closed

## Part 2: blocked PR-repair lane -> blocker issue conversion

If a lane intended to repair a branch or PR discovers that the actual failure is due to repo-wide CI/governance drift outside the lane's owned paths, do not guess, broaden scope, or patch unrelated files.

### Required diagnosis output

Produce a blocker report containing:
- the failing workflow/check names
- exact missing/referenced files or scripts
- commit/history evidence showing when the breakage was introduced
- why the failure is repo-wide rather than branch-specific
- what could not be verified because of session capability limits

### Then immediately create or attach to a blocker issue

First check whether the blocker class is already tracked.
If an existing open issue already matches the exact blocker class, add fresh evidence there instead of opening a duplicate.
Only create a new blocker issue when no suitable existing tracker exists.

Examples from live use:
- create a new blocker issue when a PR-repair lane discovers a previously untracked repo-wide CI/workflow drift
- attach fresh evidence to an existing blocker issue when a local-ready implementation lane is blocked by a known pre-push / worktree / hook-coupling problem already under active tracking

This keeps overnight batches from creating duplicate blocker tickets while still preserving the new evidence.

### Also update the blocked issue

Post a comment on the originally targeted issue explaining:
- the blocker issue number
- that the branch was not changed because the failure is upstream/repo-wide
- the next correct sequence:
  1. fix blocker issue
  2. rerun/rebase blocked PR
  3. reassess remaining branch-specific failures

## Post-reboot / context-compaction merge-close lane

Use the same blocker-conversion discipline when a reboot, token reset, or context compaction leaves partially-repaired PRs in flight.

Required sequence before more edits:
1. Rebuild live state from GitHub, not the old transcript:
   - `gh pr view <n> --json headRefOid,mergeStateStatus,mergeable,statusCheckRollup`
   - save/inspect latest run IDs and exact failing check names.
2. Inspect full failed job logs when `--log-failed` only shows wrapper/post-job noise:
   - `gh run view <run> --log > /tmp/ci-logs/<repo>-<run>-full.log`
   - then grep/read around the real failing test, not only setup/cache cleanup errors.
3. Classify each remaining failure before patching:
   - branch-specific regression that belongs to this PR
   - stale/broad CI collection lane that should be bounded
   - conflicting test expectations or repo-wide data/fixture drift that should become a blocker issue/comment instead of speculative edits.
4. For matrix jobs, fix one class and re-push once; then wait for the new head run. Do not keep patching against stale run IDs after the PR head changes.
5. If two tests require opposite production behavior, stop treating it as a simple CI fix. Choose the behavior that matches real execution semantics, update the stale test if clearly wrong, or create/update a blocker issue documenting the conflict.
6. For inherited PRs with data-dependent CI failures, separate code-path bugs from missing checkout artifacts before broadening scope.
   - Verify repository root/path constants first; a bad `PROJECT_ROOT`/relative path can mask the real missing-data condition.
   - Search for the required fixture/source files in the checkout and record whether they are absent or merely mislocated.
   - If the test genuinely requires optional external/source data that is absent from normal CI checkouts, add a narrow `pytest.skip(...)` guard around fixture construction (including `FileNotFoundError` raised after initial path checks) instead of fabricating data or rewriting production logic.
   - Rerun the exact failing target after the skip change; do not assume the first missing file is the only missing source artifact.
7. When an inherited PR has legacy tests seeding older persistence models while current code writes canonical models, do not collapse duplicate detection to one side blindly. Preserve canonical duplicate checks and, if compatibility is required, add a narrow legacy fallback keyed by a durable external identifier, with targeted tests proving both paths.
8. Do not merge while `mergeStateStatus` is `UNSTABLE` unless the only non-green checks are explicitly non-blocking and documented by policy.

Useful merge-close output should include:
- PR URL, head SHA, latest run ID, and current check conclusions
- pushed commit hashes and local validation commands
- unresolved failures grouped by class
- whether issues were closed, updated with evidence, or left open because CI remained red

## Practical batch pattern

A high-yield overnight mix is:
- 2-3 verify-close lanes for stale-open approved issues
- 1 bounded branch-repair lane
- 1 true implementation lane

This gives you:
- backlog reduction from issue closure
- dependency clarification from blocker conversion
- one or more genuine code-execution lanes still making forward progress

## Pitfalls

- Do not treat commit containment alone as proof of completion when merge-race workflows exist.
- Do not keep a blocked PR-repair lane running after proving the root cause is repo-wide.
- Do not silently absorb a CI workflow fix into a feature-branch repair lane unless that workflow path is explicitly owned.
- Do not close a stale-open issue without explicit acceptance-criteria mapping and at least one concrete proof artifact.

## Reusable outcome

This pattern turned one overnight batch into:
- multiple stale-open issue closures with proof-rich comments
- one blocked PR lane converted into a newly tracked CI blocker issue
- clearer priority focus on the remaining true implementation lane
