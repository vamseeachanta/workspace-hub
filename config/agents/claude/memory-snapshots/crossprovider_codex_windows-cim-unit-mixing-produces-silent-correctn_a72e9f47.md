---
name: crossprovider codex windows-cim-unit-mixing-produces-silent-correctn
description: Windows CIM unit mixing produces silent correctness bugs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [windows, units, data-integrity]
---

CIM's FreePhysicalMemory reports KB, but TotalPhysicalMemory reports bytes. Mixing units without explicit conversion (e.g., computing RAM in MiB) produces silently-incorrect resource accounting on Windows collectors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
