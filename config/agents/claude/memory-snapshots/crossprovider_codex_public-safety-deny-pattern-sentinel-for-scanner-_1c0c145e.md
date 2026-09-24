---
name: crossprovider codex public-safety-deny-pattern-sentinel-for-scanner-
description: Public safety deny-pattern sentinel for scanner allowlists
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy-scanning, deny-lists, tooling-pattern]
---

Use `PUBLIC_SAFETY_DENY_PATTERN_EXAMPLE` line-level sentinels to mark allow-listed deny-patterns in privacy/legal scanners, preventing false-positives on documentation examples. Avoids need for broad file-level exclusions that become security backdoors, and keeps enforcement rules tight.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
