---
name: crossprovider codex generated-artifact-parity-tests-catch-silent-sch
description: Generated artifact parity tests catch silent schema divergence
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [testing, schema-validation, generated-artifacts]
---

Tests that verify generated JSONL/JSON/HTML exactly match checked-in baselines before and after implementation catch schema mutations and count mismatches that structural tests alone miss. This pattern is effective for closed-world generators (e.g., client-private-routing-queue.py) where outputs must remain stable across reruns.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
