# Adversarial plan review: issue #3544 — FD broker security R12

- Date: 2026-07-15
- Reviewed commit: `fedce54c1c85b7a75d29d9627f1c39b4af9184aa`
- Verdict: **MAJOR**

## Findings

1. Inherited `BASH_ENV` and dynamic-loader variables could execute before the
   broker because the outer Bash/Python environment was not cleared.
2. CPython runtime randomness contradicted an overbroad “no entropy” claim.
3. Verified module FDs were not bound to later Python imports.
4. Pseudocode still assigned retained no-follow opens to Bash.

No files or external state were changed by the reviewer.
