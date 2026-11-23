# Adversarial plan review — #3424 privacy/transaction r8

Provider: Codex parallel reviewer

Verdict: MAJOR

## Findings

1. Push used the mutable local branch ref as its source; auto-sync could advance it after verification and publish an unscanned commit before the post-fetch check noticed.
2. The lock ownership token contained only issue and PID, so PID reuse could make a stale pre-existing lock look transaction-owned and eligible for deletion.

## Required disposition

- Push the immutable candidate object with an exact remote-head lease and verify both local and remote refs afterward.
- Add a cryptographically unpredictable per-attempt nonce to the ownership token and test PID-reused stale-lock behavior.

All earlier lock/trap/scanner/CAS issues were resolved in this round.

No files were edited by the reviewer.
