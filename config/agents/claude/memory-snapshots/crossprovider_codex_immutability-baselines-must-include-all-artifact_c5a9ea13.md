---
name: crossprovider codex immutability-baselines-must-include-all-artifact
description: Immutability baselines must include all artifacts the process will modify
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [immutability-contracts, process-state, append-only]
---

When defining 'append-only' or immutability guarantees, explicitly include every artifact the process will later mutate (e.g., pack manifests, config files). Excluding 'affected' artifacts from byte-identity proofs creates a loophole: the original can be overwritten after baseline is established, breaking the immutability guarantee.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
