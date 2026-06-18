---
name: crossprovider codex codex-statusline-api-limitation-native-items-onl
description: Codex statusline API limitation — native items only
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [codex, statusline, api-constraint, config-only]
---

Codex CLI uses `tui.status_line` with predefined item IDs (model, context, rate-limit, git, token, session), not custom command hooks like Claude's `statusLine.command`. Exact Claude parity (`C:32%|O:35%·3.3d|G:100%·6.6d`) is not achievable; solution is config-only (reorder native items, update sync tests).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
