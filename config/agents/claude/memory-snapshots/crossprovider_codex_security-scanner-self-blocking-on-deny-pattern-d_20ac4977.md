---
name: crossprovider codex security-scanner-self-blocking-on-deny-pattern-d
description: Security scanner self-blocking on deny-pattern documentation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [security, scanning, automation, documentation]
---

When a privacy/security scanner checks for deny-tokens (e.g., /mnt/ace paths), it can fail on its own policy/test documentation if deny-pattern examples aren't marked with a sentinel. Use PUBLIC_SAFETY_DENY_PATTERN_EXAMPLE marker to distinguish documented examples in policy files from real private data, so the scanner excludes marked examples from rejection rules.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
