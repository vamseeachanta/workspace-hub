---
name: crossprovider codex pipe-delimited-row-strings-are-fragile-for-exten
description: Pipe-delimited row strings are fragile for extension in bash
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, data-structure, brittleness]
---

Extending pipe-delimited strings with new fields (e.g., `id|priority|...|note|not_before`) causes silent corruption when field values contain the delimiter. Codex identified this in whats-next.sh: any future note with `|` would shift columns silently. Use associative arrays or separate parallel data structures instead to avoid brittle re-parsing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
