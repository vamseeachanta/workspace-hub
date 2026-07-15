# Task 3 RED report — canonical genesis approval parser

Issue: [#3544](https://github.com/vamseeachanta/workspace-hub/issues/3544)

Added `scripts/legal/tests/test_rule_authority_genesis_approval.py` with a
canonical typed record helper and focused contract tests for acceptance,
canonical bytes, exact nested key sets, schema/type mutations, malformed
identity and host facts, missing fields, duplicate keys, BOM/CRLF, and the
16,384-byte bound (11 test functions plus parameterized cases).
The tests target the future `parse_canonical_approval(bytes)` boundary and do
not add parser, schema, or production code.

RED evidence (2026-07-15):

```text
$ pytest -q scripts/legal/tests/test_rule_authority_genesis_approval.py
ERROR collecting ...
ModuleNotFoundError: No module named 'verify_rule_authority_genesis_approval'
```

This is the intended RED state: the production verifier module has not yet
been created.
