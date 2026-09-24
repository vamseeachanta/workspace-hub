---
name: crossprovider codex evidence-crossing-schemas-need-explicit-fail-clo
description: Evidence-crossing schemas need explicit fail-closed input-to-output mappings
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy-gates, schema-design, data-flow]
---

When sensitive input (e.g., approved reference labels) must map to safe output (e.g., neutral handles), the mapping must be explicit, tested, and prevent leakage or silent narrowing. Session 3 found a contract contradiction: labels were forbidden in output but no mapping rule prevented implementation from leaking or omitting approved set members.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
