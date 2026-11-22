# Hash-pinned attestation tests

A source pin checks provenance. A refreshed-pin mutation checks whether the
attestation rejects changed behaviour. Both checks are required: rejection at a
stale hash alone does not establish semantic rejection.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Add separate provenance and semantic controls to prevent vacuous mutation coverage. |

Table 1. Guidance revisions.

## Test pattern

Use `tests/enforcement/pin_helpers.py::assert_semantic_rejection` with a pytest
temporary directory, monkeypatch, original source bytes, mutation function, pin
table, evaluator and expected semantic reason. The original pin must match and
the original evaluation must return `accepted`. The helper copies and mutates
the source, reads it back, patches only the in-memory pin table and evaluates
an isolated record map. Source paths must resolve inside the temporary directory.
The pin is restored even when evaluation raises.

The wrapper reason API returns `missing-pin`, `missing-source` or `stale-pin`
for provenance failures, and `unreachable` or `source-shape` for semantic
failures. `accepted` denotes agreement with the source contract. An unknown
attestation returns `None`; the existing boolean API retains that distinction.
The helper accepts only an explicit semantic reason, so a false boolean,
provenance rejection or always-accepting evaluator cannot satisfy the test.
An always-rejecting evaluator fails the baseline positive control.

Retain separate missing-pin and stale-pin tests. Never refresh committed pins
from a failing test automatically. Changed source requires inspection of the
reachable source contract, followed by source, pin and contract tests in the
same change. Hash agreement does not authorize execution or establish general
shell-program correctness.

## Worked example

`tests/enforcement/fixtures/pinned-preview.sh` is the complete source:

```sh
#!/bin/sh
set -eu
mode=preview
target=local
if [ "$mode" = apply ]; then
  printf '%s\n' "$target"
fi
printf '%s\n' "$mode"
# no external effects
exit 0
```

The hand-counted ten lines are read as bytes; the script is never executed.
The independent semantic rule permits a literal `mode=preview` assignment.
Changing that line to `mode=apply` violates the rule. Independent `sha256sum`
readback of the exact fixture and that substitution produced:

| Source | SHA-256 |
| --- | --- |
| Original | `605183fcd3b4f413a2c91c3849caec5bf0faa0cffed79dec632d29ba02fdc19b` |
| Mutated | `646156d0b7abbcece69a10f424fade9d0c1322ab8e4eae56e9775555aa36a2c9` |

Table 2. Exact source-byte digests; algorithm: FIPS 180-4 (2015), section 6.2.

With the original pin, mutated bytes produce `stale-pin`. With the recomputed
pin temporarily installed, those same bytes produce `source-shape`. The test
`test_worked_example` checks both results and the restored pin. Its semantic
oracle is the literal assignment specified above, independent of production
attestation implementation.

## Inventory and closed schemas

The machine-readable [audit](../reports/hash-pinned-attestation-audit.json)
records each test, module, original coverage and current verdict. AST discovery
enumerates enforcement test functions that reference known attestation APIs or
pin tables and their local callers. A new discovered test without an audit row,
an obsolete row or a duplicate fails `test_attestation_inventory.py`. New
attestation APIs and pin-table names must also be registered in the discovery
entrypoints. This is a bounded static inventory, not arbitrary Python call
resolution; dynamic imports and cross-module helper indirection require review.
Unpinned structural and baseline-digest controls remain explicit in the audit.

| Workflow test | Previous assertion | Closed contract |
| --- | --- | --- |
| `test_main_push_scheduler_workflow_is_fail_closed` | Exact push keys and branch; no whole-event equality or conditional-job check | Entire `on` mapping equals push to main; job and steps have no conditions. |
| `test_enforcement_workflow_is_active_and_failure_propagating` | Presence of pull request event | Entire event mapping equals the existing main-branch pull request activity list; job and steps have no conditions. |

Table 3. Workflow-policy inventory in `test_scheduler_mutation_delivery.py`.

The repository search for `paths`, `paths-ignore`, `branches-ignore` and event
assertions identified these scheduler contracts. Other `paths` assertions in
skills-audit and secret-scanner configuration tests describe finding locations
or scanner exclusions, rather than workflow triggers, and are outside this
event contract. The existing main-push test already used an exact inner map;
its remaining gap was the surrounding event and condition schema.

Use whole-map equality when the contract is closed: every extra event key or
filter can change coverage. Use an explicit allowed schema for extensible
contracts, with independent assertions for required fields. A token denylist
cannot establish an exhaustive event contract. Mutations cover `paths`,
`paths-ignore`, `branches-ignore`, `tags`, `tags-ignore`, activity `types`, branch
changes, additional/missing triggers, and job/step `if` expressions. An unsupported
filter on an event is also rejected; not every event accepts every spelling.
Existing pull request activity restrictions remain deliberate contract fields.

## Sources and limits

- [GitHub Actions workflow syntax](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions),
  accessed 2026-10-22: event branch, tag, path and activity filters; job and step
  conditions. Filters restrict matching runs and conditions can skip execution.
- [FIPS 180-4, Secure Hash Standard (2015)](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf),
  accessed 2026-10-22, section 6.2: SHA-256 algorithm, used as
  `pin = SHA256(source_bytes)` for both original and mutated bytes.

No engineering constants or acceptance limits are introduced. Fixture digests
identify synthetic bytes, not engineering inputs. The helper cannot prove the
semantic strength of the evaluator; the mutation and expected reason still
require review. Working-source snapshots used by unit tests do not replace
the production guard's index transport or final staged-tree validation.
