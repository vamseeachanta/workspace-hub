---
name: crossprovider codex scanner-path-validation-in-planning
description: Scanner path validation in planning
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [planning, validation, scanners]
---

When verifying plans that reference external scanners, validate that planned commands match actual scanner constraints (e.g., paths must be repo-local, not absolute/temp-file paths). Planned commands using incompatible path formats (like `--scan-public-path <temp-file>`) surface incomplete contract understanding early.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
