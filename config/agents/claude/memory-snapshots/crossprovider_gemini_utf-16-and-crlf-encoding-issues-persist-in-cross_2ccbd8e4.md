---
name: crossprovider gemini utf-16-and-crlf-encoding-issues-persist-in-cross
description: UTF-16 and CRLF encoding issues persist in cross-platform work queues and YAML
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [encoding, cross-platform, data-integrity, yaml-parsing]
---

Mixed Windows+Linux environments produce UTF-16 files (Windows Notepad default) or CRLF line endings that silently break `generate-index.py` and other Python parsers on Linux. No Python fallback or partial-line skipping will catch encoding errors—they must be caught at commit time. Encoding guard hooks are load-bearing for ecosystem stability.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
