---
name: crossprovider codex codex-statusline-is-config-only-not-scriptable-l
description: Codex statusline is config-only, not scriptable like Claude
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [codex, statusline, configuration, tool-limitation]
---

Codex uses native `tui.status_line` config with predefined item IDs; no support for custom command hooks like Claude's `statusLine.command`. Exact format cloning (C:32%|O:35%·3.3d) is impossible. Viable approach: reorder/suppress native quota items via config only; no code/script changes extend it.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
