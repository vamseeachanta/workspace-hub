---
name: crossprovider hermes preserve-checksummed-evidence-artifacts-during-c
description: Preserve checksummed evidence artifacts during cleanup
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cleanup, evidence, preservation]
---

When cleaning up workspace folders, preserve evidence-bearing directories (e.g., `preserved-*` with `.sha256` files) even if they consume disk space. These enable root-cause analysis and recovery if needed; separate approval from general cleanup.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
