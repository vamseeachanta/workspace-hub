---
name: crossprovider codex click-dual-boolean-flags-need-explicit-default-n
description: Click dual-boolean flags need explicit default=None for schema precedence
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [click, cli-design, precedence]
---

#611 adds `--export-xlsx/--no-export-xlsx` deferring to spec defaults when flag omitted, but Click dual-bool flags without `default=None` collapse absence to a boolean, silently overriding schema precedence. TDD must test absent flag behavior.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
