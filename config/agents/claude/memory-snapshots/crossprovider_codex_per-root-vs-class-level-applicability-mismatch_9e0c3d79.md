---
name: crossprovider codex per-root-vs-class-level-applicability-mismatch
description: Per-root vs class-level applicability mismatch
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, plan-fidelity, output-projection]
---

Plans claiming 'per-root applicability decisions' but implementations only tracking class-level state (no opaque_root_id in output) create false correctness. Downstream cannot determine which concrete root is eligible. Outputs must include opaque root ID or the plan claim is falsified.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
