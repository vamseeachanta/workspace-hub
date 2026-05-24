# Approved Issue SSoT Verification Interruption Pattern

Use when an approved issue is interrupted during verification/closeout after implementation changes exist.

## Durable lesson

If a live verifier fails on an operator-facing argument or output contract, treat that as an unfinished implementation blocker, not a cosmetic command typo.

Examples from sibling-repo SSoT work:
- A checker accepted registry machine keys but not hostnames/aliases; live usage with `--machine ace-linux-1` failed even though registry key `dev-primary` existed. Add a RED test for registry key + hostname + alias resolution before fixing.
- A repair verifier was invoked with `--json` before confirming the parser supported it. Preserve the exact failing command and parser error in the interruption handoff, then resume by either adding the missing contract under TDD or correcting the verification command to the documented CLI.

## Resume order

1. Re-check issue approval/state and `git status --short`.
2. Re-run the narrow failing verifier command first.
3. If the verifier CLI contract is wrong, add/adjust a focused RED test before implementation.
4. Re-run the targeted suite and live checker.
5. Only then proceed to adversarial review, commit/push, evidence comment, and closeout.
