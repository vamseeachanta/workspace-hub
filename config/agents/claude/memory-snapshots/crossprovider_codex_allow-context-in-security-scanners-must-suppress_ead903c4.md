---
name: crossprovider codex allow-context-in-security-scanners-must-suppress
description: Allow-context in security scanners must suppress matched content only, not whole lines
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [security-scanner, allow-context, design-principle]
---

When implementing line-level allow-contexts in security scanners, suppress only matched content within valid blocks. Whole-line suppression is a failure mode: a valid allow-context can hide raw paths, emails, confidentiality markers, or secrets elsewhere on the same line. Enforce matched-content allowance; test with mixed-content lines to catch the defect.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
