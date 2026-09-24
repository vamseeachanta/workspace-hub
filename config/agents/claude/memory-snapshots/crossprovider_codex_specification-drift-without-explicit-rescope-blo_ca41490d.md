---
name: crossprovider codex specification-drift-without-explicit-rescope-blo
description: Specification drift without explicit rescope blocks gate approval
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [specification, scope-management, gates]
---

WRK-1053 v1→v2: implementation shifted from category-based coverage audit to script-reference audit without updating acceptance criteria. If implementation diverges from spec, create explicit rescope entry (e.g., 'AC3 deferred to WRK-1054') and surface it to user approval before gate passes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
