---
name: crossprovider codex multi-platform-collectors-need-dual-fixture-cove
description: Multi-platform collectors need dual fixture coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-07-23
  tags: [cross-platform-testing, fixture-parity, windows-shell, schema-migration]
---

Shell and PowerShell collectors share schema but diverge in test fixtures. A schema bump updating only the shell fixture leaves the Windows collector path untested. Dual-platform collectors require synchronized fixture updates and acceptance tests covering both paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
