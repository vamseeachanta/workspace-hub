---
name: crossprovider codex safety-contract-testing-requires-allowlist-verif
description: Safety contract testing requires allowlist verification, not string scanning
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, safety-contracts, mutation-detection, allowlists]
---

Scanning shell source for mutation strings like `git push` won't catch Python `argv` lists, subprocess calls, or indirect mutations. Read-only contracts must be verified by tracking execution paths against known-safe allowlists, not pattern-matching source text. String-based tests provide false confidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
