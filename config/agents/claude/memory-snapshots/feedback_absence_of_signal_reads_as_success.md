---
name: feedback_absence_of_signal_reads_as_success
description: "In CI, a missing signal looks greener than a failing one — audit suppressions, aggregate membership, and dynamic deps, not just red tests"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 19c1569d-4a9e-4d87-bd34-50c2605be4d1
  modified: 2026-08-02T11:22:56.928Z
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

## 2026-08-02: three self-inflicted instances in one session

The pattern is not only in CI. Three times in one session a **failed operation presented as a successful one**, each through a different mechanism:

1. **Hung push.** `git push` on a new branch stalled 44 min in the pre-push hook — zero bytes of output, no timeout, no error. A hung push is byte-for-byte indistinguishable from a finished one. Only `git ls-remote` distinguishes them. See [[feedback_prepush_no_verify_allowed_on_feature_branch]].
2. **`| tail` ate a non-zero exit.** Ran `bash review-fanout.sh ... 2>&1 | tail -30`; the script correctly `exit 2`-ed on a filename-convention rejection, but **a pipeline reports the LAST command's status**, so the harness recorded exit 0. I nearly filed a bug against the script for "exiting 0 on rejection." The script was right; the invocation was wrong.
3. **0-byte artifact = still running, not empty result.** Review artifacts existed on disk with size 0 while the providers were mid-flight. File existence is not completion.

**How to act on it**
- **`cmd | tail` / `| head` discards the real exit code** — and I reach for those constantly to keep output small. Use `set -o pipefail`, check `${PIPESTATUS[0]}`, or don't pipe when the status matters. This composes with instance 1: piping a push through `tail` hides *both* the hang and the failure.
- Verify against the **authoritative external state**, never the local command's report: `git ls-remote` over push output, `gh pr list --state merged` over a diff read ([[feedback_branch_landed_ask_the_forge_not_an_llm]]).
- A **0-byte output file means in-flight or dead, never clean.** Size 0 is not a result.
- Diagnose a hung command through its **children**, not itself: `pgrep -P <pid> -a` names what it is actually stuck in.

See [[feedback_non_required_checks_hide_regressions]],
[[feedback_required_check_must_not_skip]], [[project_orcaflex_ecosystem_review_2026_07_25]].
