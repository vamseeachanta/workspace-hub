---
name: crossprovider codex generated-artifacts-that-collapse-drop-tracing-i
description: Generated artifacts that collapse/drop tracing info break auditability
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [code-review, governance, traceability]
---

When code scores or renders evidence, dropping opaque identifiers (e.g., `evidence_ref` fields) from the output creates governance gaps—claims become untraceable to their fixture sources. Generated reports must preserve the full tracing chain, not just human-readable labels.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
