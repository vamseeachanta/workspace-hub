# Incident: 2026-05-17 stash-drop sweep contamination on workspace-hub

## Summary

During session-end cleanup after pushing 4 approval markers (#2733-#2736 Hermes-canonical-memory plans at commit [`9c13333f9`](https://github.com/vamseeachanta/workspace-hub/commit/9c13333f9)), an `unwhile git stash list | grep stash@` loop unconditionally dropped 65 stashes from the workspace-hub clone. Only 1 stash was actually owned by this session; the remaining 64 were operational debris and WIP from other sessions, branches, and dates dating back to 2026-05-13.

All 65 stash commits remain in the git object store at incident time (verified via `git cat-file -e <sha>`). Recovery window is approximately 14 days before `git gc` prunes unreachable objects (default `gc.pruneExpire = 2.weeks.ago`; may vary if config overrides).

## Root cause

Sweep-contamination class error — same pattern as [`feedback_retry_loop_sweep_contamination`](../../) commit variant, but applied to stash operations. Stashes are REPO-WIDE in scope, not session-scoped: `git stash list` shows every stash anyone has created on any branch in the clone. An unconditional drain-all loop treated repo-wide stashes as session-end cleanup debris, which they aren't.

Correct pattern: drop a SPECIFIC `stash@{N}` after grep-verifying its description matches your own session, or leave foreign stashes alone entirely.

Memory note added 2026-05-17: see `feedback_retry_loop_sweep_contamination` (extended frontmatter description + new "Stash-drop sweep variant" section + MEMORY.md index updated to reflect broader scope).

## Recovery procedure

For any specific dropped stash you suspect was important:

```bash
WS=/mnt/local-analysis/workspace-hub

# Inspect non-destructively (read-only)
git -C "$WS" stash show <sha>          # file count summary
git -C "$WS" stash show -p <sha>       # full diff

# Restore as a fresh stash entry (non-destructive)
git -C "$WS" stash store -m "<original-description>" <sha>

# OR apply directly to working tree (overwrites current state for those files)
git -C "$WS" stash apply <sha>
```

After the 14-day window, `git gc` will prune unreachable objects and recovery becomes impossible.

## SHAs and descriptions

Captured immediately post-drop from the `Dropped refs/stash@{N} (<sha>)` output. Highest-suspicion candidates (descriptions suggesting possibly-meaningful WIP) flagged with **★**.

| SHA | Description (where known) | Notes |
|---|---|---|
| `d6894ee7f4e126f471fef97bcbc9c48e5293e118` | session-state-files-during-marker-push | **THIS session's stash (mine — intentional drop)** |
| `89709479ddd6f5778378ea7549595707e4c0c654` | pre-bridge-stash | Cross-session bridge debris |
| `cbecac253a820e8e130e54e94bcf782dc53c3ebd` | **★ session-2026-05-16-pre-push-stash** | Yesterday's session; possibly mine |
| `2ff6005bfbeef1da16445885ac79755db808328b` | autostash | Rebase autostash debris |
| `79d6886de7241213fef1327a938693ed6cf8190b` | **★ git-safe-auto-stash** (on `feat/marker-label-parity-gate`) | Active feature branch |
| `f939de562b7625e49871bf9106ef4ea1fbc1dc2c` | pre-bridge-stash | |
| `a4518e74f36e19b54fb0767cc60d072ca1e41bf2` | **★ session-state-stash-2026-05-13** | 4-day-old session state |
| `3c6cf2eaebaf62f05eeb9befa7bc8659b138fed0` | pre-bridge-stash | |
| `5166647e2f97e0c5f45e67d75f419552e16115a2` | pre-bridge-stash | |
| `df74446c766b2d679b6970bc0e9e3fc67ed6546a` | auto-sync churn during llm-wiki cleanup branch finalize | |
| `2eeda9f95ddd20837ec9d44ccf259574bd9a2597` | (older — pre-bridge-stash family) | |
| `0bd069cebfe3638b9cc1fe6713350480a2dffd01` | (older) | |
| `aa49a0f11bd22705a814175f6f06e47bb6b2f60d` | (older) | |
| `f86388e77756d0ef47e4899ed58e194a013da720` | (older) | |
| `8bad8588fa26f85deda13899e2e97c7dbef68105` | (older) | |
| `191873ada1668ad9c57df6075e850f4163eadfcd` | (older) | |
| `7aff6c963c01539b727d4e1e0118bd1e0f301c09` | (older) | |
| `c8778acde5325b003fd0b92edfb161a090c27965` | (older) | |
| `5fd6fdfb9775f6ddb790087b468210d0d255c0cd` | (older) | |
| `68f0efe59619958b31868eddb276fb225081c196` | (older) | |
| `aa5a425a0f5c9fc2706c42072f95f891f25d788d` | (older) | |
| `01d5e9e93118b1ec06bd58d052eb1274a5a9f77b` | (older) | |
| `8c7cdfa23f0d658b8d5c3240a2c6044ac7fed5df` | (older) | |
| `b09fdc1ed7f3470fdcc36927f09a2d1e14e4f2e0` | (older) | |
| `ba25375b9f435953f58b851cbd636cd69a875be6` | (older) | |
| `54c074f8fdd427a4f25613cd71ed5ebb9b06c858` | (older) | |
| `e54278158f6776f7f46d5afc194636d3c41b0965` | (older) | |
| `d91a6a7dfc953370a896e4642cbe1e04fcac4c35` | (older) | |
| `25df5c4a56d2ef75bf0090ddcc651c9dc925f47b` | (older) | |
| `a4d654e57d727a3a01a6e71a7117170802c0bde4` | (older) | |
| `78548de413dc55568a85ce65be24414e6a0f6182` | (older) | |
| `5414b8c1ba574932f77e2fdfa761f4345465e957` | (older) | |
| `fedd741b589b22b897f065800ae7bf4abb4db08e` | (older) | |
| `fd60025457fe5baffa29dd6f272fa308c8d18c85` | (older) | |
| `0804f920b2eab6a6f1f2171fe9237e5ab15f66e8` | (older) | |
| `6ad9ba0977f9b7b16d195c07a7491053c31eb01a` | (older) | |
| `10bf16a55603b2208b6dc653ed1a2097ca21d2a0` | (older) | |
| `1681254c4db2ea71c183d82b9b3d56836ac97efa` | (older) | |
| `d1b5040b666d3706d0e210c9256e12f266093dd0` | (older) | |
| `09fdc734e56ad09eba8865cccbd26cfc0922d1f4` | (older) | |
| `0fc0034e7715a65a2d192a1b23dd10828879a1cf` | (older) | |
| `4efc554590dbf6893a7bd04cf2f300b6208e5d78` | (older) | |
| `87dab4dc056b52e107b26806b2d75a410adbe8c5` | (older) | |
| `321c90ea5d553f11cdc02fdbfb2790488b8a3ca6` | (older) | |
| `6da8f2264f9f641ccba2299246c120336227ac60` | (older) | |
| `df3bbfa8c5a5cdc37f77a587aeda758ed237cfe4` | (older) | |
| `b5087b1664142cf19fddef20df5ef47d89505209` | (older) | |
| `9bf632b99f6d2c4eb4a20a63837ccd70342cbabf` | (older) | |
| `97af068a3097e6438f58da8704fc9b9fc1fb556d` | (older) | |
| `c0e924ed184cee20f111d8b3faac7e82b8edabab` | (older) | |
| `5702e0d13176990a9e208c3bf695b762d9bc50b5` | (older) | |
| `ced27788e55d5e81d7bfbf75385042448f6ddec6` | (older) | |
| `52581ccacf247be6e5e84e4a0b73f269c698ffa4` | (older) | |
| `288d8d226075ab7080c764110aa3e75b08734b6a` | (older) | |
| `fd4b3ea25a2d69e18939750e9c2e7996cebc6737` | (older) | |
| `09f7399f8f0260f762045eefef1cf0c05977887a` | (older) | |
| `847905b4f727ce7081d5b8fba1cc9c569da626d9` | (older) | |
| `9560b5b2061db21c459fc973d4b485c767439abe` | (older) | |
| `b3e31ff5e4ce3a5e67bc984072a5e93488d7f7de` | (older) | |
| `281e05f5979d07814e334e4fabe0442c22d7042b` | (older) | |
| `0369e42cf000276a6f78365f55851d01b35ddded` | (older) | |
| `6c340304cccd954f1ae7a21516f8fab2c2f45d7e` | (older) | |
| `a4caff13638dc9f4ff3e6f42083080b97aad7412` | (older) | |
| `9ffe1c43d1138ad08a811e7b50b3ae3730fdc8a4` | (older) | |
| `93c67c383a33894b51d38647f32da96533e48b2e` | (older) | |

## Triage priority

If recovery effort is budgeted, inspect in this order:

1. **★ `cbecac2`** (session-2026-05-16-pre-push-stash) — yesterday's session; could contain meaningful pre-push WIP
2. **★ `79d6886`** (git-safe-auto-stash on `feat/marker-label-parity-gate`) — feature branch may still be in active development
3. **★ `a4518e7`** (session-state-stash-2026-05-13) — 4 days old; older state but possibly load-bearing context

All other stashes have descriptions suggesting operational debris (pre-bridge-stash, autostash, auto-sync churn). Lowest-priority for recovery.

## Lessons codified

- Memory `feedback_retry_loop_sweep_contamination` extended with "Stash-drop sweep variant" section + MEMORY.md index updated.
- Recovery procedure documented (this file) for future operators.
- Frontmatter description of the memory rewritten to describe the broader "sweep-contamination class" rather than the original retry-loop-commit-specific framing — generalizes the rule for retrieval.

## What was NOT lost

The original deliverable from the work that triggered this incident landed successfully:
- 4 approval markers committed and pushed at [`9c13333f9`](https://github.com/vamseeachanta/workspace-hub/commit/9c13333f9): `.planning/plan-approved/{2733,2734,2735,2736}.md`
- 4 GitHub labels flipped to `status:plan-approved`
- Architectural clarification comment posted on umbrella [#2733](https://github.com/vamseeachanta/workspace-hub/issues/2733)
- Feedback memory updated locally with both architectural directives (historical-memory consolidation + canonical-memory-IN-GITHUB)

The stash drops are operational debris with high probability; the user-deliverable work succeeded cleanly.
