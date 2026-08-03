# Adversarial plan review: issue #3544 — consumption R9

- Date: 2026-07-15
- Reviewed commit: `fc96082c582a924f2132ea641a6ffaa36eb944ed`
- Verdict: **MAJOR**

## Findings

The four R8 consumption findings were resolved. A new MAJOR remained: the
approved interpreter was rehashed by pathname before consumption but was not
retained across the later authority exec, allowing different interpreter bytes
to run after approval was spent. Activation COMPLETE proof also failed to state
that it acquires the same parent lock.

## Required correction

The launcher must open one verified interpreter FD and execute both verifier and
authority through that same `/proc/self/fd` identity. Activation classification
and local proof must acquire and hold the retained-parent lock nonblocking.

No files or external state were changed by the reviewer.
