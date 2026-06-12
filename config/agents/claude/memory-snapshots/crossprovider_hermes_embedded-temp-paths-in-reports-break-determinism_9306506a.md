---
name: crossprovider hermes embedded-temp-paths-in-reports-break-determinism
description: Embedded temp paths in reports break determinism and portability
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [reproducibility, path-portability, report-generation]
---

Report generation includes artifact temp paths (e.g., `/tmp/.../artifacts/...`), making report hash non-deterministic. Reproducible commands require fixed paths or path-agnostic report formats. Hardcoded temp paths in markdown reports are non-portable across machines.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
