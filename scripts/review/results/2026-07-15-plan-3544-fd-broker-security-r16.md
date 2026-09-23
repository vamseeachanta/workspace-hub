# Adversarial plan review: issue #3544 — FD broker security R16

- Date: 2026-07-15
- Reviewed commit: `46fe41621bd2c36c0b1173b2384090fb89efe108`
- Verdict: **MAJOR**

## Finding

The frozen Bash preflight used bare `trap` and relied on `builtin` to prove that
`builtin` was not shadowed. Executed fixtures showed that functions named
`trap`, `builtin`, `type`, and `exec` could forge every answer, pass the
preflight, and intercept the final call. The plan therefore could not claim that
an in-shell check established the integrity of the shell that evaluated it.

The correction must either use a separate authenticated direct-exec entry or
make a pristine already-running Bash an explicit out-of-band trust prerequisite
without a self-attestation claim.

No files or external state were changed by the reviewer.
