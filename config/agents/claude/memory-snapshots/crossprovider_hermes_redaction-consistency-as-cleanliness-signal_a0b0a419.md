---
name: crossprovider hermes redaction-consistency-as-cleanliness-signal
description: Redaction consistency as cleanliness signal
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [secret-scanning, redaction, audit-control, cleanliness-verification]
---

When secret scans consistently produce the same hash (`d3eba50e73fe816282cc31de9e199fdb9c5247df1ed1c0a6efe5a3ff5f183b5e` for 'clean' state) across multiple monitoring cycles, this is verification that post-redaction artifacts are stable and uncontaminated. Use the clean-state hash as a control signal; deviation triggers audit. Applies to GitHub API responses, logs, and CLI output that may contain tokens/keys.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
