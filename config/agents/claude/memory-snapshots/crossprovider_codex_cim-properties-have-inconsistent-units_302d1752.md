---
name: crossprovider codex cim-properties-have-inconsistent-units
description: CIM properties have inconsistent units
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [windows, cim, units, correctness]
---

Windows CIM: FreePhysicalMemory is KB, TotalPhysicalMemory is bytes. Must coerce both to same unit (MiB) before arithmetic or comparisons; do not assume units match.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
