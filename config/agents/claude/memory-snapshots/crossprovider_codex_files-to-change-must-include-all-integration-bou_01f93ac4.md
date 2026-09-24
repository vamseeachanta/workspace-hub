---
name: crossprovider codex files-to-change-must-include-all-integration-bou
description: Files-to-Change must include all integration boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, file-inventory, integration-points]
---

Plans often omit the files where integrations actually happen (e.g., where a runner calls a preparer, or where results are extracted from output). Grep for actual call sites, not just the "main" modules mentioned in the narrative. Missing integration-point files cause implementation gaps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
