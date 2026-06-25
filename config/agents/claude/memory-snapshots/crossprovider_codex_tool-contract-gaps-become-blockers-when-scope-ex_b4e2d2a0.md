---
name: crossprovider codex tool-contract-gaps-become-blockers-when-scope-ex
description: Tool contract gaps become blockers when scope expands
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [tool-design, scope-mismatch, contract-debt]
---

When reusing an existing tool for a slightly-broader use case, verify its contract supports that scope before committing to the design. DNV classifier needed legal-sanity-scan's `--paths` mode (path-scoped scanning) but it only had full/diff-only modes; contract expansion became a prerequisite. Check tool boundaries early.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
