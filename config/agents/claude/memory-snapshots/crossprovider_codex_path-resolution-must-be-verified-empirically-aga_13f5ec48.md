---
name: crossprovider codex path-resolution-must-be-verified-empirically-aga
description: Path resolution must be verified empirically against the real filesystem
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [shell-scripting, path-resolution, verification, defects]
---

Don't assume static path resolution in shell scripts. Grep all invocation sites, test each against the actual filesystem, and flag unresolvable ones separately. Variable-prefixed paths like `$WORKSPACE_ROOT/...` can usually be resolved; others require runtime verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
