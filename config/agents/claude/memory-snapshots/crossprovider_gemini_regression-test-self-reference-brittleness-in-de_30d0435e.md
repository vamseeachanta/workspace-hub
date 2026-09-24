---
name: crossprovider gemini regression-test-self-reference-brittleness-in-de
description: Regression test self-reference brittleness in deleted-path scans
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, regression, grep, refactoring, brittleness]
---

Regression tests that grep for deleted or moved file paths will false-positive if the test file itself or plan/documentation contains those strings as references or examples. Mitigation: use per-line sentinels (like `# pragma: allow-deleted-path-reference`) or path-restricted allowlists; avoid blanket per-file exemptions, which are security/correctness backdoors.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
