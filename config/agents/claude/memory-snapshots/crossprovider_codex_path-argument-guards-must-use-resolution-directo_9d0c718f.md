---
name: crossprovider codex path-argument-guards-must-use-resolution-directo
description: Path argument guards must use resolution + directory checks, not token denylists
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, mutation-prevention, path-handling]
---

Scripts accepting path arguments can bypass source-boundary assumptions if not guarded. Token denylists prevent strings from appearing in output but do not forbid read_text(), mkdir(), write_text(), or arbitrary path mutations. Enforce via explicit resolution to allowed directory (e.g., resolve input, assert path is under `data/document-index/`, reject otherwise).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
