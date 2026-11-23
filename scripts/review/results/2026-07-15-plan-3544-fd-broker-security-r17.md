# Adversarial plan review: issue #3544 — FD broker security R17

- Date: 2026-07-15
- Reviewed commit: `2096f2f6516e5adaf4bf2b063532ab10624ad1af`
- Verdict: **MAJOR**

## Findings

The frozen command began with `builtin exec -c`, so it erased `GITHUB_ACTIONS`
and `LEGAL_RULE_OWNER_GENESIS` before the first Python process could enforce the
stated Actions and owner gates. The trusted parent Bash must check those values
immediately before clearing its environment, or the gates must be removed from
the runtime claim.

Two negative tests also overclaimed what the boundary can prove: the memfd
carries a declared approved digest rather than a runtime measurement of Python's
executed `-c` bytes, and deliberate same-UID reconstruction of the retained FD
state remains outside the threat model.

No files or external state were changed by the reviewer.
