# Golden provenance and behavioral evidence

A comparator declaration distinguishes a regression record from independent
evidence. The Level 2 checker validates that declaration. Passing it does not
establish that the comparator was executed, that its source is independent, or
that an engineering result meets its criterion.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial | 2026-10-22 | Define the standalone declaration check and behavioral probes required by issue #3844. |

## Committed-tree check

Run from the repository root:

```sh
uv run --no-project python scripts/enforcement/check-golden-provenance.py
uv run --no-project python scripts/enforcement/check-golden-provenance.py --ref origin/main
```

The script reads only the selected Git tree, pinned before enumeration. It does
not inspect uncommitted edits, untracked records, ignored files or sibling
repositories. `--repo` selects another authorized local repository. Inherited
Git binding variables are removed for these read-only subprocesses.

Every directory with an exact path component `golden`, `goldens`, `baseline` or
`baselines` requires its own immediate `provenance.json`. A record at a parent
cannot cover a nested directory with another matching name. Nonstandard names
are outside automatic discovery and require a separate inventory. Directory
names are a discovery convention, not proof of engineering content: a source
package called `baseline` is reported too. A submodule inside a matching directory
still triggers the requirement; the submodule's contents are not traversed.

The minimum record has a JSON object `comparator` containing the exact string
`class` from the taxonomy below. Additional run metadata is permitted and should
record the producing revision, tool version, arguments, parallel configuration
and input digest where applicable. This slice does not validate those fields.

| Comparator class | Declaration check | Meaning |
|---|---|---|
| `closed-form` | Pass | Published analytical solution |
| `measured` | Pass | Physical experiment |
| `cross-solver` | Pass | Independent correlated implementation |
| `conservation` | Pass | Invariant the result must satisfy |
| `archived-run` | Warning | Prior output of the same code; regression evidence only |
| `none` | Warning | No correctness comparator |
| Missing or unrecognized | Error | Required declaration is absent or unusable |

Malformed JSON, duplicate keys, non-finite constants and non-object comparator
records fail. A symlink or submodule cannot supply the provenance record. A
record must be a regular committed blob; metadata values are never echoed in
diagnostics. Formatting-only fixtures can declare `none` and retain a warning
rather than invent a correctness comparator.

Exit status is success when there are no errors; warnings alone do not fail.
Declaration errors fail. Failure to read the Git tree or a required blob has a
distinct operational-error status. These are command conventions, not numerical
engineering acceptance limits. No hook or mandatory CI gate is installed by this
slice; existing directories are reported without backfilling or exemptions.

## Worked declaration example

Inputs: a committed `tests/golden/answer.txt` and the following
`tests/golden/provenance.json`:

```json
{
  "comparator": {
    "class": "conservation",
    "description": "An independently derived count invariant"
  }
}
```

Method: identify the `golden` directory, locate its immediate regular JSON record,
parse `comparator.class`, and compare it with the class table. `conservation` is
recognized and is outside the warning set. The answer is no declaration errors
and no warnings. The command succeeds. This example supplies no engineering
result or physical acceptance limit; it demonstrates the declaration contract.

Negative controls use the same inputs: remove the record and the answer is a
missing-record error; replace the class with `archived-run` or `none` and the
answer is a warning. The tests derive their expected results from this hand
trace and the policy table, independently of the implementation.

## Structural reads require behavioral checks

Issue #3844 identifies the failure as **a structural read reported as a
behavioral fact**. One recorded example confirmed an `IntEnum` member existed,
then described its consuming whitelist as sound without evaluating the
comparison. The whitelist compared numeric string representations to member
names, so it matched nothing. The member existed; that did not establish the
relationship consuming it.

Before publishing a behavioral claim, execute the check at the boundary the
claim concerns. Record the command, environment, exit status and observed result.
If execution is unavailable, label the claim **NOT_EVALUATED** and state the
missing dependency or evidence. Reading structure alone cannot upgrade it.

| Claim | Small executed disproof to attempt |
|---|---|
| A module cannot import | `python -c 'import importlib; print(importlib.import_module("package.module").__file__)'` |
| A path does not resolve | `python -c 'from pathlib import Path; p=Path("relative/path"); print(p.exists(), p.resolve(strict=True))'` |
| A test never collects | `python -m pytest --collect-only -q tests/test_target.py` |
| A comparison accepts the intended state | `python -c 'from enum import IntEnum; S=IntEnum("S", "READY"); print(str(S.READY) in {"READY"}, S.READY in {S.READY})'` |
| An imported function is reached | Execute the real entry point with a spy on the alleged callee and assert whether it was called. |

Substitute the real module, path, test and comparison in an authorized disposable
environment. Importing code can have side effects: do not probe licensed or
unauthorized dependencies. A collection result establishes collection only;
a path check establishes that filesystem path only. Import aliases must be
checked by importing, not inferred from a missing directory. Trace reachability
through the actual entry point; the presence of an import is insufficient.

The comparison probe is a synthetic counterexample. Member equality succeeds
while string-to-name membership fails. It illustrates the mechanism without
importing any engineering software. Correctness of a real whitelist still
requires executing its actual comparison against accepted and rejected states.

Before trusting a parameter sweep, assert invariants that must remain fixed
across that sweep. A changing applied input can resemble convergence; repeatable
outputs and plausible trends do not independently establish correctness.

## Sources and verification scope

- `.claude/rules/reproducibility-is-not-correctness.md` (2026), comparator table
  and application guidance: taxonomy and separation of regression from correctness.
- Issue #3844 (2026), proposed scope, acceptance criteria and instances of
  structural-read failures: declaration enforcement and behavioral probes.
- Linked issues #3838, #3839 and #3843, and the linked example-deck issue:
  historical context only. No historical engineering number is reused here.
- `tests/enforcement/test_check_golden_provenance.py`: policy truth-table cases,
  malformed-record controls, immutable-tree reads and executable synthetic
  comparison. No engineering equations, coefficients or acceptance limits are
  introduced; equations and numerical sourcing are therefore not applicable.

Existing golden directories are not migrated. Declared comparator validity,
source rights, execution receipts and the truth of arbitrary behavioral claims
remain subject to review. The structural-read checklist is prose guidance; the
Level 2 check applies to comparator declarations only.
