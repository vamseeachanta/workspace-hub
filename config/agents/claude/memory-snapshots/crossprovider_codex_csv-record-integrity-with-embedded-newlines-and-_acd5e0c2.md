---
name: crossprovider codex csv-record-integrity-with-embedded-newlines-and-
description: CSV record integrity with embedded newlines and mixed line endings
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-integrity, csv, binary-fidelity, record-parsing]
---

Line-wise splitting and fragment parsing is unsafe for binary-faithful record mutation. Use proper CSV record parsing with byte spans or record boundaries before any mutation; this applies to queue-based workflows and data migrations with quoted fields and mixed CRLF/LF line endings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
