# Task 2 report: Phase-A ledger key ID

Implemented the smallest Task 2 contract:

- `new_ledger` now rejects key IDs unless they are `phase-a-` plus a lowercase canonical UUIDv4.
- Codec ledger parsing applies the same validation and enforces the UTF-8 byte bound of 64 bytes.
- The generation-ledger JSON Schema now carries the matching prefix/UUIDv4 pattern and byte-length bound.
- Existing CLI and audit fixtures using the pre-contract synthetic key ID were updated to the canonical Phase-A test ID.

Verification:

- `pytest -q scripts/legal/tests/test_rule_authority_codec.py -k 'key_id'` — 10 passed, 12 deselected.
- `pytest -q scripts/legal/tests/test_rule_authority_codec.py` — 22 passed.
- `pytest -q scripts/legal/tests/test_rule_authority_cli.py -x` — 3 passed, then an existing filesystem-preflight fixture failed with `command=authority verdict=filesystem rc=4`; the failure is unrelated to key-ID parsing and is reproducible in the unchanged authority fixture path.
- `pytest -q scripts/legal/tests/test_rule_authority_audit.py -x` — audit cases reached execution; the shared runner emitted partial progress without a final summary, so this suite remains a verification follow-up rather than being claimed green.

Scope exclusions: no approval parsing, FD broker, launcher, protection, workflow, CLI, or external activation work.
