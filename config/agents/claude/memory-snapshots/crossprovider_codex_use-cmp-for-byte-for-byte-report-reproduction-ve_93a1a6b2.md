---
name: crossprovider codex use-cmp-for-byte-for-byte-report-reproduction-ve
description: Use cmp for byte-for-byte report reproduction verification
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [reproducibility, testing-rigor, determinism-verification]
---

When validating that a script produces deterministic output matching a committed report, capture the generated output to temp and use `cmp <generated> <committed>` rather than visual diff or string comparison. This proves exact reproduction without relying on eyeballed similarities.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
