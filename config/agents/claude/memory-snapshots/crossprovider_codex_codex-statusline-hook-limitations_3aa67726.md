---
name: crossprovider codex codex-statusline-hook-limitations
description: Codex statusline hook limitations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling, cross-provider, architecture, codex]
---

Codex does not support Claude-style custom command hooks for status formatting; native `/statusline` uses predefined footer items via `tui.status_line` config key. Exact Claude-format clone (C:32%|O:35%...) is not currently possible via stock Codex; viable path is managed config change to make native footer compact and quota-first.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
