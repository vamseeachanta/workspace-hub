---
name: crossprovider codex api-backward-compatibility-preserve-positional-s
description: API backward compatibility: preserve positional slots, keyword-only after *
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [api-design, backward-compatibility]
---

When changing an API used with positional arguments, preserve existing positional parameter slots exactly (order and meaning). Add new parameters only after a bare `*`, making them keyword-only. Use sensible defaults (e.g., `load_datum='net_pump_load'`) to maintain existing callers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
