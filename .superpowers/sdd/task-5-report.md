# Task 5 RED report — retained-FD genesis launcher

## Scope

Added only contract tests in `scripts/legal/tests/test_rule_authority_genesis_launcher.py`.
No launcher, broker, verifier, authority, or activation code was added.

## Verification

Command:

```text
pytest -q scripts/legal/tests/test_rule_authority_genesis_launcher.py
```

Result: **21 failed**, as expected. Every test fails at the required launcher
boundary because `scripts/legal/launch_rule_authority_genesis.sh` does not yet
exist. This is intentional RED evidence for the next implementation slice.

The suite now exercises the public entry through subprocess fixtures (in
addition to source-independent contract checks): owner/Actions acceptance and
rejection, hostile environment clearing, exact argv forwarding, PATH/Python
sentinels, unrelated-FD closure, no-follow symlink rejection, and sealed
memfd identity readback. The frozen public argument names and order are pinned
(`--tool-repo`, `--tool-sha`, `--out-parent`, `--transaction-id`,
`--approval-record`, `--approval-sha256`, `--python-realpath`, and
`--python-sha256`). A valid temporary approval/contract/manifest/verifier
fixture captures child argv, environment, and inherited descriptors; the
launcher is required to reach it under a pristine environment. The tests pin
owner-only public entry, `builtin exec -c`, retained
`O_NOFOLLOW` descriptors, independent outer-bootstrap identity, isolated
stdlib-only `-I -S -B -c` broker, no path reopening/entropy/authority import,
sealed memfd requirements, exact internal argument ordering, and no mutable
broker file.
