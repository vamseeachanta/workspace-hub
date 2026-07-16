# Adversarial governance review — #3549 amendment, round 2

**Verdict: MAJOR**

**Reviewed commit:** `7b658ce2c3a2809b92d5f7478245108d3bb52d5d`

## Blocking findings

1. **Renewed approval still has no revision-bound local proof, and the sole
   changed-path authority prevents adding it.** Round-1 Finding 1 required a
   fresh user action **and** a revision-identifying approval marker after the
   amendment obtains a no-MAJOR review. The revision now truthfully says the
   live issue has no marker and that only the user may restore
   `status:plan-approved` at
   `docs/plans/2026-07-16-issue-3549-registry-connection-helpers.md:228-231`,
   but Acceptance Criterion 2 at `:371-372` requires only the label. The
   `Canonical Implementation Changed-Path Map` declares itself the sole
   authority at `:233-240` yet contains no `Create` row for
   `.planning/plan-approved/3549.md`. Consequently the post-review workflow
   must either omit the repository's canonical local approval proof or create
   an unauthorized path that makes the candidate equality check fail. The HTML
   repeats only the label/user gate at
   `docs/reports/2026-07-16-issue-3549-registry-connection-helpers-plan.html:84-92,231-248,251-264`.
   Require the owner-authorized transition to create a marker bound to the exact
   reviewed amendment revision (and approval identity/date), add that path to
   the changed-path authority, and verify both label and marker before any
   correction resumes.

2. **The amendment still retroactively labels an already-green executable
   behavior as a future RED-first correction.** The amendment says new tests
   “will first prove RED” for “direct executable mode” at plan `:200-207`, and
   again groups direct-executable tests into the correction sequence at
   `:219-226`. At the reviewed commit,
   `scripts/operations/connection/connect-workstation.py` already has a Python
   shebang, is stored as Git mode `100755`, and direct invocation from a
   non-repository working directory returns success. The existing test at
   `tests/workstations/test_connection_cli.py:234-249` uses `sys.executable`,
   but removing that interpreter prefix does not expose an unimplemented
   behavior: the executable bit was already committed in
   `ff410225583d42d84d4b1e7fb2167621d74d0c5f`. This repeats the temporal defect
   in round-1 Finding 2. Direct execution may be retained as characterization/
   regression evidence, while the genuinely absent corrections (`--fall`,
   general pre-child `OSError`, child `-SIGINT`, overlay-I/O classification,
   and literal-source enforcement) may receive new RED tests. It may not be
   counted as a new failing review-driven test or evidence of post-amendment
   TDD.

## Checks performed without another finding

- Live `gh issue view 3549` shows only `status:plan-review`, not
  `status:plan-approved`; `.planning/plan-approved/3549.md` is absent. The
  rollback and current-state claims in plan `:228-231`, Review Summary
  `:443-446`, README `:206`, and HTML `:84-92` match live state.
- `d9db0d7665c66736ae185e462213c92da9a65d82` exists and is the merge commit for
  PR #3556, the approved-plan merge. `git diff --name-status d9db0d... HEAD`
  confirms the present WIP action semantics: registry/resolver/plan/README/HTML
  are modifications, the two connection modules/CLI/two focused tests are
  creations, and all three round-1 amendment artifacts are creations.
- The changed-path map explicitly includes the canonical plan, README, HTML,
  all three round-1 artifacts, and all three expected round-2 artifacts at plan
  `:272-280`. The conditional runbook predicate is currently true because all
  three named tokens are absent, so its conditional row is not a silent
  exclusion.
- The focused acceptance command at plan `:400-401` now includes
  `tests/workstations/test_connection_cli.py`. The current focused CLI file was
  also executed and reports 15 passing nodes; this is baseline evidence only,
  not acceptance of the future corrections.
- HTML lifecycle content now distinguishes preserved WIP from future
  corrections at HTML `:104-127,231-248`, and its body reports round-1 MAJOR,
  paused implementation, rolled-back label, and absent marker. Aside from the
  missing renewed-marker contract in Finding 1, it is lifecycle-consistent with
  the Markdown plan and README.
- `git check-ignore -v --no-index` confirms each of the six exact amendment
  artifact paths is ignored by `.gitignore:577`. Plan `:282-285` limits
  force-add to those individual paths and forbids directory-wide/wildcard
  force-add.
- Live issue #3561 is OPEN at `status:needs-plan` and explicitly owns repair and
  splitting of the dead `scripts/workspace` connection-menu dispatch. The plan,
  README, and HTML all defer that caller without claiming it remains compatible.
- A tracked-text search for the five wrapper basenames found the executable or
  printed calls in `scripts/workspace:283,314,345,350`, which are covered by
  #3561. The remaining operational call sites use the fixed-ID
  `ssh-dev-secondary.sh` in `docs/ops/ace-linux-2-handoff-runbook.md`; that
  wrapper retains its fixed machine ID under plan `:125`, so no current caller
  migration is omitted. Other hits are historical plans/audits or documentation
  surfaces already listed in the changed-path map.

## Required disposition

Keep #3549 at `status:plan-review` with no approval marker and do not resume
correction implementation. Add the revision-bound approval-marker transaction
to the plan/map/HTML acceptance contract and reclassify direct-executable mode
as preserved green regression evidence rather than a future RED. Then rerun the
amendment review before requesting renewed user approval.
