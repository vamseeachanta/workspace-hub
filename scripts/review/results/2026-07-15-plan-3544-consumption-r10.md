# Adversarial plan review: issue #3544 — consumption R10

- Date: 2026-07-15
- Reviewed commit: `dbce469323ce4e2904e66fd618ac7a41b2e10283`
- Verdict: **MAJOR**

## Finding

The bootstrap's separate probe proved only that some open file description held
the parent lock, not that the inherited candidate FD owned it. An unlocked
candidate could pass while another process held the lock.

## Required correction

The lock proof must require first probe failure, successful lock reassertion on
the inherited candidate, and second probe failure. The verifier should directly
exec authority after consumption so normal lock continuity is structural, and
tests must inject an unlocked candidate while another process owns the lock.

No files or external state were changed by the reviewer.
