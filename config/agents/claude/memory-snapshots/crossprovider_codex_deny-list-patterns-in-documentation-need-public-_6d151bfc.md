---
name: crossprovider codex deny-list-patterns-in-documentation-need-public-
description: Deny-list patterns in documentation need public-safety markers
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [documentation, security, patterns, privacy]
---

Policy and test documentation can reference concrete deny-list examples (e.g., 'reject /mnt/ace/...' or 'block SECRET_KEY=...') only under a PUBLIC_SAFETY_DENY_PATTERN_EXAMPLE marker. Without the marker, privacy scanners correctly reject the documentation file itself, creating a false blocker.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
