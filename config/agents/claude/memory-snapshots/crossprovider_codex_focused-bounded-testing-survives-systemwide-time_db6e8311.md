---
name: crossprovider codex focused-bounded-testing-survives-systemwide-time
description: Focused bounded testing survives systemwide timeout bounds
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, performance, workspace-hub, fuse]
---

When comprehensive test suites hit FUSE or systemwide 60s timeouts on large clones (workspace-hub ~33K files), don't retry full test runs. Instead: switch to bounded static checks (linter, function length) + focused regression suite covering critical paths. This unblocks verification without requiring full CI rerun.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
