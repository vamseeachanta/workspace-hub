# Adversarial governance review — #3549 amendment, round 3

**Verdict: MAJOR**

**Reviewed commit:** `d28dc9b7e3957e4e2a18b83921108b710c17f945`

## Blocking findings

1. **The superseding candidate map lost the conditional runbook predicate, so
   exact changed-path equality is no longer executable.** The addendum declares
   itself the superseding authority and says the candidate will include
   `docs/ops/remote-linux-access.md` only “when its predicate fires”
   (`docs/plans/2026-07-16-issue-3549-amendment.md:96-100,127`), but neither the
   addendum, base plan, nor HTML now defines that predicate. The immediately
   previous reviewed revision did define it: modify the runbook only if any of
   `connect-workstation.py`, `machine-local fallback overlay`, or `--dry-run` is
   absent after rebasing, otherwise preserve it and record the three-token
   preflight. Commit `d28dc9b7e` removed that reason column while moving the map
   into the addendum. Base-plan implementation step 8 still refers to “its
   predicate” (`docs/plans/2026-07-16-issue-3549-registry-connection-helpers.md:257-259`)
   without restoring it. A frozen candidate can therefore include or omit the
   runbook without a canonical decision rule, defeating the promised exact map
   check at base-plan acceptance lines 308-311 and addendum lines 167-170.
   Restore the exact predicate and its required evidence in the superseding
   addendum.

2. **The claimed revision-bound two-signal approval gate is prose-only and the
   existing enforcement accepts materially weaker evidence.** The addendum says
   implementation remains blocked unless the owner-applied label and marker
   “match the reviewed revision” (`docs/plans/2026-07-16-issue-3549-amendment.md:151-161`),
   but it specifies no marker schema, validation command, or artifact integrity
   check beyond embedding a commit SHA and three paths. Existing strict commit
   enforcement accepts the named marker solely on file existence
   (`scripts/enforcement/require-plan-approval.sh:58-72`) and the write hook
   accepts any non-recent/non-self-labelled marker without checking issue label,
   reviewed SHA, review verdicts, or artifact blobs
   (`.claude/hooks/plan-approval-gate.sh:34-73,96-100`). Neither enforcement file
   is in the candidate map. Thus a stale or altered marker can authorize writes
   even when the label is absent, its SHA is stale, or a round-3 artifact is
   MAJOR/modified. This also leaves round-2’s required approval identity/date
   absent from marker content. Define an exact marker schema including approver
   identity/date, reviewed SHA, immutable round-3 artifact identities and
   no-MAJOR verdicts; add an executable pre-resume verification that checks the
   live label and marker against the reviewed revision (and authorize any needed
   enforcement change).

3. **The human-facing HTML contradicts the canonical amendment on both TDD state
   and lifecycle gating.** The canonical addendum correctly classifies direct
   executable mode as already green regression coverage
   (`docs/plans/2026-07-16-issue-3549-amendment.md:74-79`), but the HTML still
   requires a *failing* direct-executable test
   (`docs/reports/2026-07-16-issue-3549-registry-connection-helpers-plan.html:237-243`).
   Its success contract then says correction is blocked only until the user
   reapplies `status:plan-approved` (`:257-270`), omitting the required
   revision-bound marker despite the stronger gate at `:128-130`. Finally,
   “Review round 3” at `:93-96` describes the original plan’s Claude/Codex/Gemini
   disagreement immediately after the amendment r1/r2 state without identifying
   it as the original review, making it read as the not-yet-complete amendment
   round 3. The HTML is the declared human-facing plan, so these are operational
   contradictions, not cosmetic lag. Make its TDD sequence, success gate, and
   review chronology exactly match the addendum.

## Verified checks

- Live issue #3549 is OPEN with exactly one lifecycle label,
  `status:plan-review`; it has no `status:plan-approved` label and
  `.planning/plan-approved/3549.md` is absent. The current paused/WIP state is
  truthful. The commit log from the baseline contains preserved Slice A/B/C WIP
  commits and no renewed approval claim.
- `d9db0d7665c66736ae185e462213c92da9a65d82` exists, is the PR #3556 merge
  commit, and is an ancestor of the reviewed commit. Deferred oversized files
  are byte-identical to that exact baseline: `docs/plans/README.md` SHA-256
  `782f5968...a9b4d`, `docs/modules/cli/WORKSPACE_CLI.md` `b500598f...3bd928`,
  and `scripts/workspace` `61d83b3f...3bc7f0`.
- The superseding map explicitly includes the addendum, base plan, HTML,
  revision-bound approval marker, all amendment review artifacts r1-r3, and the
  split command/test modules. All six r1/r2 artifacts are tracked; all nine
  review paths are ignored by `.gitignore:577`, and the addendum limits force-add
  to exact paths rather than a directory or wildcard.
- The direct executable is presently mode `100755` with a Python shebang; the
  addendum correctly treats it as regression rather than a promised RED. Finding
  3 is the remaining HTML contradiction.
- Current and baseline line counts substantiate the named dispositions:
  `registry.yaml` is 405 and will be compacted to at most 400;
  `connection.py`/`test_connection_resolver.py` are 376/397; base plan/addendum/
  HTML are 387/170/298. Every other existing mapped candidate file is at most
  337 lines. The three intentionally deferred byte-identical files are
  541/488/575 lines, and every future created/changed file is subject to the
  addendum's explicit `wc -l <= 400` candidate gate.
- Live issue #3561 is OPEN at `status:needs-plan` and owns the `scripts/workspace`
  split, dead connection paths, explicit machine selection, Windows fallback UX,
  and menu tests. The #3549 deferral is accurately scoped.

## Publication readiness

**NOT READY TO PUBLISH.** No remote ref exists for
`feature/3549-registry-connection-helpers`; the latest live issue comment still
identifies local amendment commit `8f159199d...`, not reviewed commit
`d28dc9b7e...`; and the final round-3 artifact set is not yet committed/pushed.
The known pre-push coverage gate is an external publication blocker, not an
additional content finding. Even if that gate clears, the three MAJOR content
defects above require revision and another focused review before renewed user
approval.

## Required disposition

Keep #3549 at `status:plan-review` with no approval marker. Restore the
conditional-path predicate, make revision-bound approval mechanically
verifiable, and synchronize the HTML lifecycle/TDD contract before requesting
owner approval.
