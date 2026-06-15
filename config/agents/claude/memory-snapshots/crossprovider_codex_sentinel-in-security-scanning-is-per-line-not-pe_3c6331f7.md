---
name: crossprovider codex sentinel-in-security-scanning-is-per-line-not-pe
description: Sentinel in security scanning is per-line, not per-file
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [security-scanning, legal-gate, issue-259]
---

A deny-pattern scanner that exempts an entire file/pattern if any matching line contains a sentinel example (e.g., PUBLIC_SAFETY_DENY_PATTERN_EXAMPLE) creates a bypass: a file with both an example and a real leak passes. Issue #259: fix requires per-instance sentinels or syntax-aware markers, not line-level wildcards.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
