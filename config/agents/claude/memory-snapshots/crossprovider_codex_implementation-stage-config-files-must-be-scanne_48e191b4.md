---
name: crossprovider codex implementation-stage-config-files-must-be-scanne
description: Implementation-stage config files must be scanned like source code
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [scanning, lifecycle]
---

If a `.example.json` or config template is marked as an implementation artifact, include it in leak and validation scans alongside source files. Skipping only generated/test artifacts leaves implementation-stage files under-validated.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
