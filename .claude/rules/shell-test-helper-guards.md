# Shell test helper guards — agent rule (#3876)

**When to apply:** writing or reviewing a shell test harness that has selector modes
(`if [[ "${X_ONLY:-0}" == 1 ]]`, `case "$MODE"`), defines helpers, or makes assertions inside
`$(...)`, pipelines or helper functions. Also applies to any orchestration, in any shell, that
runs a prerequisite (renderer, generator, test) before a later command whose success is
reported.

**Why:** a snapshot helper was defined only inside a selector branch. A targeted run skipped
the definition, `before="$(snapshot ...)"` failed inside a substitution whose status was not
checked, and two empty snapshots compared equal. The harness reported PASS without checking a
single identity (fixed for that harness in PR #3875). A second instance was cross-shell: a
renderer exited 2, a later successful command in the same PowerShell invocation masked it, and
the validation receipt asserted PASS while the generated document carried an
incomplete-evidence diagnostic. A successful final command is not evidence that earlier steps
passed.

**How to apply:**

1. **Define shared helpers unconditionally**, before the first selector branch. Where a helper
   must stay conditional, guard every use outside its block:
   `require_helpers snapshot || { fail snapshot_defined; exit 1; }` (or `declare -F snapshot`).
   `command -v` is not a guard: it accepts an executable of the same name.
2. **Check every load-bearing substitution explicitly.**
   `before="$(snapshot "$p")" || { fail snapshot_before; exit 1; }`. `set -e` does not propagate
   from a substitution inside `local x=$(...)`, a condition, a pipeline element or a function
   called in a `||`/`&&` list, and many harnesses omit `set -e` deliberately. `pipefail` does
   not help once the substitution's status is discarded.
3. **Reject empty records.** Compare snapshots with
   `assert_snapshot_unchanged <label> "$after" "$before"`, which fails when either side is
   blank. `require_nonempty <label> "$record"` covers single records. Equal emptiness is not
   evidence of preservation.
4. **Prove a targeted mode ran its helper** when the helper's output is the evidence:
   `guard_init` in the parent shell, `guard_mark <fn>` inside the helper (it survives `$(...)`),
   `require_executed <fn>` before reporting.
5. **Capture each prerequisite's exit code before the next command.**
   `run_step render <cmd...> || { fail render; exit 1; }` keeps the code in `GUARD_LAST_RC`.
   In PowerShell, test `$LASTEXITCODE` immediately after each native command (or chain with
   `&&`); never let a later `Write-Output` or successful command stand for the pipeline.
   Assert the expected artifact state separately from any exit code.
6. **Retain the failure receipt.** Set `GUARD_RECEIPT` to an append-only log; a corrected run
   adds lines and never overwrites the failed one.

**Tools:** `scripts/lib/shell-test-guards.sh` (runtime guards; tests
`tests/enforcement/test_shell_test_guards.py`) and Level-2
`scripts/enforcement/check-shell-conditional-helpers.py [PATH...]`, which flags calls to a
conditionally-defined helper outside its block without an earlier guard. With no path it
scans every tracked shell test harness (tests
`tests/enforcement/test_check_shell_conditional_helpers.py`).

**Do NOT apply when:** the helper is defined in every branch of an `if ... else ... fi`, or by
`if ! declare -F f; then f() {...}; fi` — the checker already treats both as defined. A
single-mode script with no selector and no substitution-based assertions needs only item 2.

**Enforcement gradient** (per [`patterns.md`](patterns.md)): Level 2 script now. Promote to a
pre-commit hook on staged `*/tests/*.sh` once it has run clean across sibling repositories.

**Related:** [`reproducibility-is-not-correctness.md`](reproducibility-is-not-correctness.md)
(reject an assertion that cannot fail), [#3876](https://github.com/vamseeachanta/workspace-hub/issues/3876),
[#3062](https://github.com/vamseeachanta/workspace-hub/issues/3062), PR #3875.
