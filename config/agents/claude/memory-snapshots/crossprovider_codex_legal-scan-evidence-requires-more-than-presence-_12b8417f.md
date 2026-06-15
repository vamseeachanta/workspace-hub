---
name: crossprovider codex legal-scan-evidence-requires-more-than-presence-
description: Legal scan evidence requires more than presence checks
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [security, legal-scan, test-coverage]
---

Requiring 'legal/security scan evidence exists' is insufficient; it allows fake/stale evidence. Need tests for: forged evidence, stale evidence after artifact mutation, wrong scan mode, denied strings present despite claimed pass, scan command/mode/timestamp/scanned-set mismatches. This prevents compliance lane bypass.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
