---
name: crossprovider codex cli-filtering-options-must-have-visible-rendered
description: CLI filtering options must have visible rendered effect
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [cli, compatibility]
---

Options like --state, --online-only, --verbose must change actual output, not silently filter intermediate data then render unchanged. Option invisibility violates surface compatibility.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
