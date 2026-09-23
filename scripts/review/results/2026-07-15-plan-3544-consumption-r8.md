# Adversarial plan review: issue #3544 — consumption R8

- Date: 2026-07-15
- Reviewed commit: `9ac1aebfe76ed1ba28dd7249d9ee0585aa313237`
- Verdict: **MAJOR**

## Findings

1. The verifier rc0/consumption ordering was impossible: the launcher was to
   revalidate after rc0 but before the verifier performed its final consumption
   action.
2. `CONSUMED_RUNNING` and `SPENT` overlapped because no lock distinguished a live
   tombstoned transaction from crashed incomplete output.
3. The plan overclaimed that pre-commit crashes were consumed even though no
   entropy/output preceded the durable commit point.
4. Future tombstone disposition could remove the sole replay barrier.

## Required correction

One long-lived verifier must final-revalidate, durably consume, and only then
return rc0. A retained-parent exclusive lock must remain held across authority
execution and final verification; recovery/cleanup must acquire it nonblocking.
Pre-commit crash must remain UNUSED only if no marker survives, and consumed keys
must remain permanent or migrate atomically into an equally durable checked index.

No files or external state were changed by the reviewer.
