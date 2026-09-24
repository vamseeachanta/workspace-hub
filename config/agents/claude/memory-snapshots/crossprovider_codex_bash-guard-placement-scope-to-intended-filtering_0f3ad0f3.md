---
name: crossprovider codex bash-guard-placement-scope-to-intended-filtering
description: Bash guard placement: scope to intended filtering layer, not all downstream logic
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash-patterns, control-flow, logic-bugs]
---

An early `return` guard in a bash function that intended to filter one output section (e.g., ready-to-start buckets) can inadvertently suppress items from all downstream sections if placed before section-routing logic. Guards must fire after early returns for items that should always appear (e.g., WORKING, EXT_BLOCKED), scoped to their specific target section only. Discovered in WRK-1100: periodic-item filter at line 86 suppressed items from WORKING and --all output before those sections were reached.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
