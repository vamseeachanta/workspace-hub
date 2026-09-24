---
name: crossprovider codex reusing-script-logic-inherits-all-scope-assumpti
description: Reusing script logic inherits all scope assumptions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-reuse, scope-drift, discovery]
---

Copying parse/discovery logic from existing scripts (e.g., generate-index.py, generate-fixtures.sh) inherits their directory scope and coverage assumptions. Before reuse, explicitly verify the source covers all cases the new plan requires (e.g., done/ and archived/ directories, not just pending/archive/).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
