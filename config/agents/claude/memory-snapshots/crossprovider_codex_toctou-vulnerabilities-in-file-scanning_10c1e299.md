---
name: crossprovider codex toctou-vulnerabilities-in-file-scanning
description: TOCTOU vulnerabilities in file scanning
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, toctou, race-condition, file-operations]
---

Stat-by-pathname followed by independent open-by-pathname has a race where directory entries change between operations. Always use descriptor-relative operations (fstatat, openat) and verify identity match via fstat after opening; don't trust earlier stat alone.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
