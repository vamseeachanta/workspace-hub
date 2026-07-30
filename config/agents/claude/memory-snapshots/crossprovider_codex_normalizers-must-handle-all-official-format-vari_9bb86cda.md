---
name: crossprovider codex normalizers-must-handle-all-official-format-vari
description: Normalizers must handle all official format variants
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [data-correctness, testing, documentation]
---

Data normalizers that accept only expected shapes silently drop valid official data (e.g., Texas RRC 8-digit API numbers when code expects 10 digits). Test against official documentation and format specs, not just happy-path assumptions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
