---
name: crossprovider codex dataset-criteria-must-be-fail-closed-not-happy-p
description: Dataset criteria must be fail-closed, not happy-path absent
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [generators, validation, testing]
---

For extensible generators (e.g., canary extraction scripts), encode dataset selection criteria (required table types, units, evidence threshold, rejection cases) fail-closed in validation and tests. Merely asserting unsafe markers are absent from output misses the adversarial path where a change silently accepts wrong data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
