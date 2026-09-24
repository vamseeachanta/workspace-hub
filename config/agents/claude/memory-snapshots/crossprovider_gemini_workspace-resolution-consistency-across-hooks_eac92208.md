---
name: crossprovider gemini workspace-resolution-consistency-across-hooks
description: Workspace resolution consistency across hooks
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [hooks, workspace-resolution, portability]
---

Different hook scripts use different approaches to resolve `WORKSPACE_HUB` (git rev-parse, manual traversal, env var fallback). Prefer consistent pattern: `WORKSPACE_HUB="${WORKSPACE_HUB:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"` or `git rev-parse --show-toplevel`. Standardizing prevents path errors when scripts run in unexpected contexts.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
