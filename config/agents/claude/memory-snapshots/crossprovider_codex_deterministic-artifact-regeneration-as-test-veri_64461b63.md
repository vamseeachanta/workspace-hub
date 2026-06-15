---
name: crossprovider codex deterministic-artifact-regeneration-as-test-veri
description: Deterministic artifact regeneration as test verification
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [testing, generators, reproducibility]
---

For generators that produce stable outputs (JSON/HTML reports from fixed input sets), verify correctness by regenerating the artifact and byte-comparing against the committed version. This catches non-determinism and verifies the generator is correctly driven by its inputs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
