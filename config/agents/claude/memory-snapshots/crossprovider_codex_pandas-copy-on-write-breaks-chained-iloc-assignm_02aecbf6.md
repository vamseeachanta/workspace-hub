---
name: crossprovider codex pandas-copy-on-write-breaks-chained-iloc-assignm
description: Pandas copy-on-write breaks chained .iloc assignment
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [pandas, runtime-defect, environment]
---

Under COW behavior, chained assignments like `df.loc[mask, col].iloc[i] = value` do not propagate; use explicit `df.iloc[i, col] = value` or reassign the whole series. Legacy code using chained assignment returns zero totals.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
