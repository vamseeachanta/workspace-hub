# Plan-lite: literal repair roots

## Summary

The work will document and verify the bounded test scope for literal target
roots in generated skills repair advice. The implementation reference is
`tests/readiness/test_reconcile_ecosystem.py`.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| 1 | 2026-10-27 | Record the explicit scope, fixture approach and acceptance criteria missing from the description. |

## Proposed scope

The tests will cover semicolons, command substitution and square brackets in
repair roots, each with and without native skills. Production behavior and
other command emitters will remain outside this change.

## Disposable-fixture approach

Each case will create an isolated repository and execute its generated advice
from a foreign working directory. Literal indexed bytes will supply the
expected adapter content. Foreign sentinels, native content and glob-matching
sibling directories will provide independent preservation checks. Injection
payloads will target only a sentinel inside the temporary test directory.

## Acceptance criteria

- All six parameterized cases will pass alongside the existing tests.
- Selected adapters will contain the literal expected indexed bytes.
- Foreign and native sentinels will retain their identity and content.
- Glob-matching siblings will remain unchanged.
- No injection sentinel will appear.
- The calling shell and Python working directories will remain unchanged.
- Existing stale-advice, missing-root and failed-runner refusals will pass.

Verification will run the complete test file with pytest, without its cache
provider and with a separate scratch basetemp. Publication checks will cover
whitespace, secrets, identifiers, ignored paths and LFS attributes. Hosted
failures will be attributed only after inspecting their logs and comparing the
relevant code and test configuration with the base branch.
