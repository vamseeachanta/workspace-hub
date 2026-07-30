---
name: crossprovider codex csv-dialect-detection-must-handle-quoted-delimit
description: CSV dialect detection must handle quoted delimiters, not count characters only
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [csv-parsing, edge-case, silent-failure]
---

Simple character-counting dialect detection (e.g., most common is the delimiter) fails silently when headers contain quoted delimiters—a comma quoted inside a semicolon-delimited file will be counted as a semicolon delimiter but misparse the header. Use `csv.Sniffer` or multi-candidate dialect parsing with quote handling and validation against field counts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
