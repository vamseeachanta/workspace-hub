# Guards must discriminate — agent rule

**When to apply:** whenever you write, review, or trust a check — a test, an enforcement script, a CI gate, a linter, a budget, a coverage report. Before believing any of them, establish that the check can *fail*.

**Why:** the single most common defect class in this repo is not a broken check. It is a check that is correct, passing, and measuring nothing. It cannot be found by reading the code, because the code is usually right — only by breaking the thing it guards and confirming something goes red.

Measured on 2026-08-01/02, one session, nine distinct instances:

| the check | what it claimed | what it discriminated |
|---|---|---|
| `client_infrastructure: []` in the PII deny-list | "no client identifiers" | nothing — an empty rule list and a satisfied one produce the same green tick |
| `check-harness-file-size.sh` | "harness files ≤ 20 lines" | four literal filenames; the 20 KB file that auto-loads has a fifth name |
| `check_r5` context budget | "≤ 16 KB of context" | 4 KB of a 24 KB load; the biggest file was never a candidate |
| `chain.py` `executed` stage | "cards that completed" | cards that *ran* — `done` means completion, not success, and `is_success` was never called |
| a title-leak test's 12-char window | "no title fragment leaks" | nothing below 12 characters — and client codes are short |
| a refused-claim test asserting `warnings` truthy | "the commit was not undone" | the weather — an unrelated warning was already present |
| a `--no-heartbeat` test counting beats | "no beater was started" | nothing — a short payload produces zero beats either way |
| `check-client-pii.py <directory>` | "these files are clean" | zero files; a directory argument scans nothing and exits 0 |
| `test_attempts_are_bounded` | "exhaustion runs nothing" | survived a behaviour change by luck — it asserted `runner.seen == []` but not `calls == []` |

Six were written *by the same people who knew about the other three*, in the same session. This is not carelessness; the failure mode is genuinely invisible from the inside.

**How to apply:**

1. **Break it and watch it fail.** Before trusting any guard, mutate the behaviour it protects and confirm a named test goes red. If nothing fails, the guard is decorative. This is the whole rule; everything below is a shortcut to the common cases.
2. **Assert the property, never the name.** `assert "title" not in card` passes when the field is renamed to `summary`. Scan the serialised output for the *value*, not the key. A test that greps for wording pins the string, not the behaviour.
3. **An empty scan is not a pass.** Enumerating zero files, summing zero candidates, iterating an empty list — all read identically to success. Fail loudly on a zero-item scan, or state the population in the output so a human can see it was one.
4. **Absence must not read as success.** Distinguish "never measured" from "measured, found nothing". `chain.py` is the reference implementation: it reports `not measured here` rather than `0` so an unbuilt join cannot read as "nothing shipped".
5. **A guard anchored to a filename is not a guard.** Anchor to the mechanism that *creates* the thing — the generator's own output list, the installer's own paths — so a rename cannot silently drop coverage. A completeness check anchored to a filename pattern is not a completeness check.
6. **A declared exemption flag is a backdoor.** A hand-editable `counts_toward_budget: false` lets anyone shrink the number while the check stays green, and records the exemption as deliberate. Derive membership; never declare it. Where an exemption is genuinely unavoidable, use a per-line sentinel with a reason (prior art: `scripts/enforcement/check-no-abs-paths.sh:111`), never a per-file blanket exempt.
7. **A test that parses the thing it validates tests the parser.** Asserting that `install-soul-runtime.sh` declares target X proves the parser reads the script; it proves nothing about the live symlink. Keep parser unit tests, but do not let them stand in for wiring tests.
8. **A mutation that hangs is a failed mutation.** It names no property and burns the CI budget. Bound your fakes so the guard fails cleanly.
9. **Add a negative control.** One test that asserts the checker *does* fire on a deliberately-bad input. It is the only assertion in a file of `assert not ...` that catches the scanner itself going blind.

**Do NOT apply when:** nothing. There is no check cheap enough to be exempt — the cheapest checks are the ones most likely to be vacuous.

**Enforcement gradient** (per [`patterns.md`](patterns.md)): Level 0 prose today. The natural Level 2 is a mutation-testing pass over `scripts/enforcement/` and `tests/`, run periodically rather than per-commit, reporting guards whose removal breaks nothing. Until that exists, the discipline is manual and belongs in every review.

**Related:** [`patterns.md`](patterns.md). Memory: `feedback_tests_that_pin_a_name_not_a_property`, `feedback_absence_of_signal_reads_as_success`, `feedback_required_check_must_not_skip`, `feedback_non_required_checks_hide_regressions`, `feedback_check_the_dimension_you_were_not_burned_by`. Issues: [#3762](https://github.com/vamseeachanta/workspace-hub/issues/3762) (both harness guards), [#3768](https://github.com/vamseeachanta/workspace-hub/issues/3768), [#3773](https://github.com/vamseeachanta/workspace-hub/issues/3773) R5, [#3775](https://github.com/vamseeachanta/workspace-hub/issues/3775) (the gate that never saw a bot push), [#3744](https://github.com/vamseeachanta/workspace-hub/issues/3744) (the prior instance this rule failed to prevent).
