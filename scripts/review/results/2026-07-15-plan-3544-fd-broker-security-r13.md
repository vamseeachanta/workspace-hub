# Adversarial plan review: issue #3544 — FD broker security R13

- Date: 2026-07-15
- Reviewed commit: `cba0351816fdac3b41e5fe7f2507b7324f4964d4`
- Verdict: **MAJOR**

## Findings

1. Dynamically linked `/usr/bin/env` could process hostile loader variables before
   clearing them.
2. Sealed archive/manifest FDs were omitted from verifier-to-authority inheritance.
3. CPython runtime-randomness wording covered only the first startup.
4. Memfd creation omitted `MFD_ALLOW_SEALING` and exact seal readback.

No files or external state were changed by the reviewer.
