---
name: crossprovider codex pattern-guards-need-natural-format-variance-cove
description: Pattern Guards Need Natural Format Variance Coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, pattern-matching, security-guardrails]
---

Security guards built with narrow regex patterns (HAR detection of `"log": {"entries"`, private-path detection for `/home` only) fail on real-world format variations (HAR with `version`/`creator` first; `/tmp`, `/var`, relative paths like `browser-evidence/...`). Guards must cover common variations of the target format, not just seeded test cases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
