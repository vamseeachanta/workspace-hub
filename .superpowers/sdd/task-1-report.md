# Task 1 RED Report — Phase-A Ledger Key ID

## Scope

Added focused tests in `scripts/legal/tests/test_rule_authority_codec.py` for the
Phase-A ledger `key_id` contract. The tests cover acceptance of the canonical
`phase-a-<lowercase UUIDv4>` form and rejection of uppercase UUIDs, non-UUID
suffixes, missing prefix, extra characters, non-string values, and non-ASCII
overlong values. No production code, schema, CLI, or unrelated tests were
modified.

## RED Evidence

Command:

```text
pytest -q scripts/legal/tests/test_rule_authority_codec.py -k 'phase_a_key_id'
```

Result: `7 failed, 1 passed, 12 deselected`.

All seven invalid-input cases failed because `authority.new_ledger()` did not
raise `codec.AuthorityError`; the canonical valid-input test passed.

## Commit

The test-only changes are committed separately with a conventional commit.

## Concerns

The production implementation must validate both the exact Phase-A prefix/UUID
shape and the UTF-8 byte bound before constructing or authenticating a ledger.
