---
name: crossprovider hermes uppercase-msys-drive-letters-must-be-normalized-
description: Uppercase MSYS drive letters must be normalized before path matching
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [windows, msys, paths]
---

Windows Git Bash paths like `/D/workspace-hub/` use uppercase drive letters, but prefix matching expects lowercase `/d/`. Normalize via regex before matching and add Windows tests alongside Linux cases.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
