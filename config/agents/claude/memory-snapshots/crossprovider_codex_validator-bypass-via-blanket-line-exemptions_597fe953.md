---
name: crossprovider codex validator-bypass-via-blanket-line-exemptions
description: Validator bypass via blanket line exemptions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validator-design, bypass-pattern, security]
---

A regex that exempts 'any line containing keyword' skips all checks on that line, not just the named check. This is a high-risk pattern: a line like `Denied traversal patterns: Path(...).rglob("*")` bypasses both traversal denial and private-leak scanning. Use targeted comment-position exemptions or per-line forensic sentinels instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
