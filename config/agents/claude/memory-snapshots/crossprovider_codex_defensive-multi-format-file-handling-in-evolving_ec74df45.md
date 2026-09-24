---
name: crossprovider codex defensive-multi-format-file-handling-in-evolving
description: Defensive multi-format file handling in evolving systems
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-evolution, file-handling, robustness]
---

When inheriting systems with filename/format evolution (e.g., legacy undated session files alongside new dated variants), defensive handling prevents export/audit breakage. Explicitly test for and handle both formats, or reject unsupported variants with clear error before processing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
