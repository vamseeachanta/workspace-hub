# Retired scanner false-pass regression

The empty-target defect in issue #3854
is superseded by scanner retirement, rather than a repaired resolver. A failed
legacy invocation establishes no scan coverage. The regression tests preserve
that distinction and reject recreation of the removed scanner, including a
dangling symbolic link.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Record retirement-compatible regression coverage to prevent false claims from legacy invocations. |

## Source basis and scope

- Issue #3854
  records the original contract mismatch: the active resolver assigned a variable,
  while its caller captured stdout. An empty target could therefore appear to pass.
- Issue #3871
  describes the same mismatch and requests evidence that the intended input was visited.
- Issue #3936
  directs retirement instead of repairing the scanner's false-PASS behavior.
- Commit `d6f08dd9c` removed `scripts/legal/legal-sanity-scan.sh` and added the
  existing retirement tests. The current checkout contains no resolver to repair.
- [Final-report verification](../standards/FINAL_REPORT_VERIFICATION.md)
  prohibits reinstalling the gate or using old scanner output as evidence.
  Secret checks, source rights and publication controls remain independent.

This is a tooling regression, with no equations, engineering coefficients or
numerical acceptance thresholds. Expected outcomes follow from the retirement
contract and direct fixture construction, rather than the removed implementation.

## Regression coverage

The existing absence guard now checks symbolic links before checking existence.
A dangling link is a directory entry even though its target does not exist;
checking existence alone would incorrectly accept it. Isolated negative fixtures
also recreate a regular file that prints PASS and a directory. Each must be
rejected by the existing retirement guard. The actual checkout exercises its
positive case: no scanner entry remains.

Legacy invocation tests construct a temporary workspace with a hub directory and
an input directory in either a nested or sibling position. The input contains a
synthetic marker. They invoke the actual removed entry point using the registered
fixture name, an empty name, a missing name, and `--all`. Each must fail without
PASS or `Scanning:` output. The marker must remain unchanged. The tests neither
restore the scanner nor claim to inspect the marker for identifier violations.

## Worked example

Inputs, relative to a disposable temporary root:

```text
workspace/
  hub/
  fixture-repo/
    sentinel.txt  (synthetic coverage marker)
```

Method: run the checkout's `scripts/legal/legal-sanity-scan.sh` through Bash from
`workspace/hub`, supplying `--repo=fixture-repo` and setting
`LEGAL_SCAN_REPO_ROOTS` to the disposable workspace. The entry point is absent.
The independent expected answer is a nonzero exit, no PASS, no `Scanning:` output,
and unchanged marker contents. These are asserted by
`test_legacy_invocation_cannot_claim_coverage` in
[the regression tests](../../tests/legal/test_named_scanner_retirement.py).
Moving the fixture beneath `workspace/hub` exercises the nested variant.

Answer: the command cannot establish coverage. Identifier review is **not
performed**. Apply final-report verification to the actual outgoing bundle;
never substitute an empty-target PASS or a failed legacy command for review.

## Reproduce

Run with the repository's Python test dependencies available. Configure the
package cache and temporary test directory outside the checkout as required by
the execution environment.

```bash
uv run --no-project --with pytest --with pyyaml python -m pytest \
  tests/legal/test_named_scanner_retirement.py \
  tests/legal/test_identifier_gate_retirement.py -q -rA -p no:cacheprovider
```

## Limits and follow-up

The original resolver repair and identifier sentinel traversal tests are
superseded by retirement. These tests establish checkout-local retirement
behavior; they do not prove migration of other repositories or installed copies.
Historical plans remain historical evidence. Maintainers determine issue
disposition after review. No scanner, hook or automatic identifier gate is added.
