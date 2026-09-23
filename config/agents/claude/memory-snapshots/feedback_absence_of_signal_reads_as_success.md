---
name: feedback_absence_of_signal_reads_as_success
description: "In CI, a missing signal looks greener than a failing one — audit suppressions, aggregate membership, and dynamic deps, not just red tests"
metadata:
  type: feedback
---

A failing check is a number that looks wrong. A **missing** check is a number that
looks right. Chase the second harder than the first.

Five instances found in one digitalmodel session (2026-07-28/29), each independent:

1. **Shard outside the roll-up** — `tests-capabilities` absent from
   `tests-all.depends_on`, red 15 days unnoticed (dm#1637). It was also the only
   gate of 27 with no `failure_action`, so it carried no verdict even when it ran.
2. **PR with zero Actions runs** — the `pull_request` event never fired; the UI
   showed "1 passing" (an app check). A PR that ran NOTHING looked greener than
   one that failed. Close/reopen did not retrigger; only a new commit SHA did.
3. **Eight workflows red for months** — targeting `tests/domains/<x>/` and
   `src/digitalmodel/modules/`, neither of which exists. Required by nothing, so
   nobody read them (dm#1907).
4. **`collect_ignore` with false comments** — "Deleted service files" (files
   existed), "hypothesis conflict" (refuted by measurement), "data files not in
   git" (generated in memory), "fails with random ordering" (3 seeds, all green).
   **139 hidden tests, 113 passing**, concealing 2 production crashes (dm#1923).
   A second uncommented layer sat beneath it: `pytest.ini` `norecursedirs`.
5. **Dependency addressed by string** — `pd.ExcelWriter(engine="xlsxwriter")`.
   No AST/import scan can see it; removing the dep broke Excel export with every
   shard green.

**How to act on it**
- A suppression's stated reason is a claim. Verify it — comments lie, and a
  plausible one reads as a settled decision nobody re-checks.
- Suite counts hide this: 686 suppressed tests were never in the denominator, so
  re-enabling them moved the visible total by only +4.
- When judging whether code is dead, check WHY it has no CI signal before
  concluding it has no value. I recommended deleting 15,218 LOC whose every
  "untested/un-CI'd" signal was manufactured by one false `collect_ignore` line;
  it had 685 passing tests and two live crashes.
- Import-based contracts are blind to `engine=`/`backend=`/entry points. Pin
  those separately, with the call site cited and an expiry check.

See [[feedback_non_required_checks_hide_regressions]],
[[feedback_required_check_must_not_skip]], [[project_orcaflex_ecosystem_review_2026_07_25]].
