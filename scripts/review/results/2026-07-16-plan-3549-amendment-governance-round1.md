# Adversarial governance review — #3549 amendment, round 1

**Verdict: MAJOR**

**Reviewed range:** `ff410225583d42d84d4b1e7fb2167621d74d0c5f..8f159199d60d66bb248e8954731fba43ccb7fc8b`

## Blocking findings

1. **The amendment's user-approval pause is not an effective gate.** The plan says
   "Implementation will remain paused until this amendment receives ... explicit
   user approval" at
   `docs/plans/2026-07-16-issue-3549-registry-connection-helpers.md:195-198`, and
   Acceptance Criterion 2 says the user will apply `status:plan-approved` at
   `:346-347`. Live `gh issue view 3549 --json labels` shows that #3549 already
   carries **both** `status:plan-review` and `status:plan-approved`. The mandatory
   status-precedence contract in
   `.claude/skills/coordination/issue-planning-mode/SKILL.md` treats the more
   advanced `status:plan-approved` as authoritative. No
   `.planning/plan-approved/3549.md` marker exists. Therefore the live state still
   authorizes implementation while the amendment text claims it is blocked, and
   the future checkbox can be satisfied by a stale pre-amendment label. The plan
   must specify and verify an approval rollback transaction: remove the old
   `status:plan-approved`, retain the issue at `status:plan-review`, remove or
   supersede any prior local marker, then require a fresh user action and a
   revision-identifying approval marker after this amendment's no-MAJOR review.

2. **The plan presents already-created Slice C artifacts as future work and offers
   no rollback capable of preserving RED-first TDD.** Commit
   `73d449e8c8381b290d2101f1e196fdcab0c969a1` already added
   `src/workspace_hub/workstations/connection_command.py`,
   `tests/workstations/test_connection_cli.py`, and
   `scripts/operations/connection/connect-workstation.py`; commit `ff410225...`
   already made the executable directly runnable. Nevertheless, the amendment
   says the modules "will" own this behavior at plan `:178-188`, the changed-path
   map classifies them as future `Create` rows at `:234-235` and `:249`, and the
   TDD sequence promises that direct executable mode and other cases "will first
   prove RED" at `:202-206`. The current files are 196, 249, and 15 lines and are
   present at the reviewed HEAD. In particular, executable mode cannot honestly
   be introduced test-first after the executable bit has already been committed.
   The amendment must choose one truthful recovery: either roll back Slice C to a
   named pre-Slice-C commit before renewed approval and rerun each RED step, or
   describe the files as pre-existing amendment-baseline artifacts, preserve the
   historical evidence, and limit new RED claims to genuinely unimplemented
   corrections. It may not retroactively describe already-landed implementation
   as future TDD.

3. **The canonical changed-path equality check has no baseline under which it can
   pass.** The map calls itself the "sole implementation changed-path authority"
   and requires the staged set to equal every row at plan `:222-227`; closeout
   again requires changed paths to equal that map at `:387-389`. Relative to the
   implementation base `d9db0d766`, the reviewed branch already modifies the plan,
   README, and HTML report as well as the Slice A-C code. The map includes
   `docs/plans/README.md` (`:260`) but omits the modified canonical plan and HTML
   report. Conversely, comparing future correction work against amendment commit
   `8f159199d` would omit every already-committed Slice A-C `Create`/`Modify` row.
   Thus neither the project merge base nor the amendment baseline can satisfy the
   stated equality. The plan must name the exact comparison commits and define a
   complete, mechanically checkable authority set (including governance artifacts
   or an explicit narrowly-scoped governance exclusion) with action semantics
   relative to that baseline.

4. **The exact acceptance command does not run the amendment's critical test
   file.** The amendment makes `tests/workstations/test_connection_cli.py` the
   authority for abbreviation, `ENOEXEC`, child SIGINT, exception-boundary, and
   executable-mode behavior at plan `:200-220` and `:308-316`. Yet the focused-test
   Acceptance Criterion at `:376-377` runs
   `test_connection_resolver.py` and operation/enforcement tests but omits
   `test_connection_cli.py`. Closeout can therefore satisfy the plan's exact
   focused command without exercising any of the command-boundary corrections
   that triggered this amendment. Add the file to the acceptance command and to
   the CI/changed-path verification contract.

5. **The human-facing HTML still asserts the obsolete pre-implementation
   lifecycle and TDD sequence.** The amendment section in
   `docs/reports/2026-07-16-issue-3549-registry-connection-helpers-plan.html:101-121`
   mentions the split, but its TDD section at `:223-240` still says the resolver,
   overlay, and CLI tests will be written and implemented from scratch. Its
   success contract at `:255` says "Implementation cannot start," while four
   implementation commits (`a116fcdbf`, `f18e5f560`, `73d449e8c`, `ff4102255`)
   precede the amendment. The README correctly says "amendment-draft —
   implementation paused" at `docs/plans/README.md:206`; the HTML instead labels
   the state "amendment review" and communicates a false not-started state. Update
   the HTML to distinguish completed pre-amendment slices, rolled-back or retained
   artifacts, the exact correction RED/GREEN sequence, and the renewed approval
   gate. The README, plan header, and HTML should use one lifecycle term.

## Verified checks without a separate finding

- The 400-line justification is empirically accurate at the reviewed HEAD:
  `connection.py` is 376 lines and `test_connection_resolver.py` is 397 lines.
  `scripts/enforcement/check_python_function_lengths.py` passed those files plus
  the new 196-line command module and 249-line CLI test with the repository's
  400-line-file/50-line-function defaults. The defect is temporal governance, not
  the split's size rationale.
- A tracked-text caller search for all five wrapper basenames found only the two
  executable no-argument Bash calls and two printed PowerShell commands in
  `scripts/workspace:283,314,345,350`. No additional executable caller is omitted.
  References in `config/tabby/*.md` and `docs/modules/cli/*.md` are documentation
  surfaces already present in the changed-path map; the fixed-ID
  `ssh-dev-secondary.sh` references do not require a caller migration.
- Adding `scripts/workspace` is within the issue body's broad authorization to
  change repository scripts and is a necessary compatibility caller migration,
  but it becomes authorized only after the renewed user approval in Finding 1.
- The amendment anticipates scanner self-blocking by requiring runtime-assembled
  synthetic protocol values and narrow same-line sentinels at plan `:285-287` and
  Risk `:440-442`. The final manifest must include both split runtime modules and
  the CLI entry point; whether test artifacts are governed must be stated rather
  than inferred from the word "core."

## Required disposition

Do not resume implementation. Resolve Findings 1-5, produce a fresh revisioned
adversarial review with no MAJOR verdict, reconcile the live issue labels and
approval marker to amendment-review state, and obtain explicit user approval of
that reviewed revision before any correction implementation.
