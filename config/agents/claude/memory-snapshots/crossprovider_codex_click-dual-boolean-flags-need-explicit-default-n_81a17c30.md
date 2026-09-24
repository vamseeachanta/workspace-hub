---
name: crossprovider codex click-dual-boolean-flags-need-explicit-default-n
description: Click dual-boolean flags need explicit default=None for config deferral
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [click-library, cli-patterns, parameter-precedence]
---

Dual-boolean flags like `--export-xlsx/--no-export-xlsx` must set `default=None` to distinguish "flag absent" from "flag false". Without it, Click collapses absence to a boolean and silently overrides config precedence chains. Test all three states: absent, true, false.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
