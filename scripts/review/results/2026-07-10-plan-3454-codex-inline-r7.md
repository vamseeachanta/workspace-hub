# Codex inline r7 — issue #3454 plan

**Reviewed working-tree SHA-256:** `0845c65f9883b7112f6307aa9382b3317c379407679ef24e772713eb9ba3926a`
**Verdict:** MAJOR

Three parallel adversarial reviews found blocking defects:

1. public planning artifacts exposed private repository, issue, path, and commit identities;
2. the driver accepted a pipe/consumed FD and used an invalid Bash option order;
3. a crash left an uncleared directory lock, while nonce-local reconciliation could create a second candidate pair;
4. the receipt commit lacked exact parent, metadata, tree-layout, and self-identity-exclusion rules;
5. the paired private review omitted commit-status severity and did not authenticate provider executable closure.

Working v8 redacts the public/private boundary, binds a sealed driver and kernel lock, reconciles the whole candidate namespace, freezes receipt construction, and tightens paired review evidence. This verdict is not approval; fresh review must target the revised exact pair.
