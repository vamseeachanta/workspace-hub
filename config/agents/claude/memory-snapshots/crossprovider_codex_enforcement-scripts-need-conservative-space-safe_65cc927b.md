---
name: crossprovider codex enforcement-scripts-need-conservative-space-safe
description: Enforcement scripts need conservative, space-safe specification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement, scripts, safety]
---

Scripts that police code (linters, validators) must use exhaustive file-selection patterns that are shell-safe (no word-splitting), conservative regex (prefer false negatives to false positives), and explicit exemption mechanisms. Underspecified enforcement silently misses violations or misparses filenames with whitespace.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
