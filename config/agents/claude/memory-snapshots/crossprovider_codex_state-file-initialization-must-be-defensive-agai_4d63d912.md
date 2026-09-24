---
name: crossprovider codex state-file-initialization-must-be-defensive-agai
description: State file initialization must be defensive against absence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [state-management, defensive-programming, file-io]
---

When managing persistent state (e.g., YAML config files), parsing logic should handle missing files gracefully by initializing an empty baseline. Avoid having read-on-update logic (like `update_state()`) crash when the file is absent. This prevents first-run failures or recovery loops after accidental deletion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
