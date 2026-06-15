---
name: crossprovider codex provider-parity-measurement-requires-explicit-ba
description: Provider parity measurement requires explicit baseline reference
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [provider-measurement, parity, machine-equality, reference-grading]
---

Measuring 'provider capability parity' on a machine must reference Claude (or another baseline) on the SAME machine, not measure each provider against absolute status. Example: cannot report Hermes and Codex as PARITY when both lack memory:read; that violates the 'vs Claude' contract. Verdict logic needs to load and compare the reference record for each capability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
