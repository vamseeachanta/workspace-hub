---
name: crossprovider hermes derived-artifact-governance-risk-in-regenerated-
description: Derived artifact governance risk in regenerated outputs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance, source-of-truth, artifacts, regeneration]
---

When regenerating one artifact from another (e.g., markdown report from JSON data), the source-of-truth precedence must be explicit in governance and validation tests. Without this, changes to the derived artifact diverge silently from the source, breaking synchronization. Establish: which artifact is authoritative on conflict, whether changes to derived-only are acceptable, and tests that verify source and derived match before approval.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
