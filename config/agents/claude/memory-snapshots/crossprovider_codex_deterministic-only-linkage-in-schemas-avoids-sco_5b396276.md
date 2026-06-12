---
name: crossprovider codex deterministic-only-linkage-in-schemas-avoids-sco
description: Deterministic-only linkage in schemas avoids scope bleed
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [schema, design, scope, data-model]
---

Keep linkage rules narrow and exact-match-only (e.g. operator + project_name equality). Reject fuzzy matching, aliases, and normalization in the linkage contract itself; these belong to separate issues and can cause unbounded scope creep.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
