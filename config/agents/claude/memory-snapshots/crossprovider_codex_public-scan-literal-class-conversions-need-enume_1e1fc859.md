---
name: crossprovider codex public-scan-literal-class-conversions-need-enume
description: Public-scan literal-class conversions need enumerated scope
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [public-scan, negative-fixtures, security-scanning]
---

Plans requiring scanner/test fixture conversions must explicitly list denied-literal classes (e.g., private paths, confidential snippets, traversal patterns) and conversion rules as acceptance criteria, not just assert safety.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
