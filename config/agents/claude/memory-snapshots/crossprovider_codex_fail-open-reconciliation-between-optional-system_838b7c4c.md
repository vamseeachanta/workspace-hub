---
name: crossprovider codex fail-open-reconciliation-between-optional-system
description: Fail-open reconciliation between optional system integrations
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [integration-api, validation-design, test-gaps]
---

When system A optionally integrates with system B (e.g., #66 fixtures reconciling with future #63 output contract), the integration validator should fail-closed: reject incompatible combinations explicitly. Only checking field name + prefix while ignoring token grammar or private-policy mismatch leaves bypass vectors. Tests must cover the integrated case, not just provisional mode.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
