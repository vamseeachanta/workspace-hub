# Task 4 report — canonical genesis approval parser

Implemented `scripts/legal/verify_rule_authority_genesis_approval.py` with a
stdlib-only `parse_canonical_approval(data: bytes)` boundary. It enforces the
16,384-byte canonical JSON contract, duplicate-key rejection, exact key sets,
typed host/account/mount facts, UUIDv4, OID/SHA-256/path/fingerprint formats,
and fixed `ValueError` failures without echoing input values.

Verification:

- `pytest -q scripts/legal/tests/test_rule_authority_codec.py scripts/legal/tests/test_rule_authority_cli.py` — **30 passed**.
- `pytest -q scripts/legal/tests/test_rule_authority_genesis_approval.py` — **58 passed**. The RED fixtures now retain the generated record for comparison and correctly assert that the one-byte-over mutation is 16,385 bytes.

No launcher, FD broker, approval-consumption, or external-activation files were
changed.
