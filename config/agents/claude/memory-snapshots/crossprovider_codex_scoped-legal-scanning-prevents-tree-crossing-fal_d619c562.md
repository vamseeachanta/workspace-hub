---
name: crossprovider codex scoped-legal-scanning-prevents-tree-crossing-fal
description: Scoped legal scanning prevents tree-crossing false positives
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [compliance, legal-scanning, scope]
---

Large legal scanners report failures from sibling/parent repos when run without path targeting. Use scan targeting options (file list, scope flag) to avoid misattribution; a clean scoped scan does not mean the entire monorepo is clean.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
