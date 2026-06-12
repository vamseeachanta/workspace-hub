---
name: crossprovider hermes autofeed-safety-verify-output-artifacts-not-proc
description: Autofeed safety: verify output artifacts, not process liveness alone
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [monitoring, autofeed, queue-safety, observability]
---

When monitoring autofeed/dispatch lanes, check for actual output artifacts (result files, log mtimes, markers written) rather than relying on process count or zero-byte logs. Logs can remain unchanged while subprocess hangs; process tables don't confirm useful work. Compare artifact sizes/mtimes across snapshots to verify throughput.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
