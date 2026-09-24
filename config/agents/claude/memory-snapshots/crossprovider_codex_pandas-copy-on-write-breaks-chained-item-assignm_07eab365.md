---
name: crossprovider codex pandas-copy-on-write-breaks-chained-item-assignm
description: Pandas copy-on-write breaks chained item assignment; use explicit indexing instead
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pandas, data-processing, defect-pattern]
---

When pandas has copy-on-write enabled, chained assignments like `df["col"].iloc[i] = value` do not update the frame. Use explicit indexing patterns (e.g., `.loc[]` with proper copy control, or `.at[]`) to ensure mutations are applied.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
