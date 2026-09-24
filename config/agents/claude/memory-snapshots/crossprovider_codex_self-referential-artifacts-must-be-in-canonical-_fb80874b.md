---
name: crossprovider codex self-referential-artifacts-must-be-in-canonical-
description: Self-referential artifacts must be in canonical scans
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, artifact-safety, leak-detection]
---

High-risk outputs from governance tasks (e.g., policy sweep reports that enumerate findings) must be included in canonical leak/safety scans that gate publication, not only in targeted follow-up tests. Otherwise the scan output itself becomes an unscanned vector.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
