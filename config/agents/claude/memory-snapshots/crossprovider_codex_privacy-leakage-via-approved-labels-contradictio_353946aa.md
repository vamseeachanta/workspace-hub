---
name: crossprovider codex privacy-leakage-via-approved-labels-contradictio
description: Privacy leakage via 'approved labels' contradiction
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy-boundaries, schema-design, plan-defects]
---

Plans allow 'approved root labels' in output while also banning client/project identifiers in the same output. Verified across #729/#730/#733/#734: raw labels like 'mkt-a', 'client-a', 'client-d' leak through despite denylist. Use opaque root IDs with label mapping kept private/off-repo, or enforce strict redaction on all outputs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
