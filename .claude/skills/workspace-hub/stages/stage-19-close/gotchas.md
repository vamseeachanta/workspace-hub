# Stage 19: Close — Gotchas

## Close Gate Minimum
Before close, require all of:
- `plan gate` passed
- `TDD gate` passed
- `integrated test gate` passed (3-5 pass records)
- `legal gate` passed
- `cross-review gate` passed (iteration count <= 3)
- `user-review html-open gate` passed for each user-review checkpoint
- `user-review publish gate` passed for each user-review checkpoint
- `resource-intelligence gate` passed
- `reclaim gate` evaluated (pass or n/a with reason)
- `future-work gate` passed
- `archive-readiness gate` passed or deferred with follow-up WRK
- `stage evidence gate` passed (stages 1-20 covered)

## No-Bypass Rules
- No close without a per-WRK stage ledger in assets covering stages 1-20.
- No close without gate evidence and `integrated_repo_tests` count in [3,5].

## Edge Cases
- HTML verification required for WRK>=624.
