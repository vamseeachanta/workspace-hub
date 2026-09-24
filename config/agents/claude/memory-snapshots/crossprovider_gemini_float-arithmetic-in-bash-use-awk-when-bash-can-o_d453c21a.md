---
name: crossprovider gemini float-arithmetic-in-bash-use-awk-when-bash-can-o
description: Float arithmetic in bash: use awk when bash can only do integers
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [bash, arithmetic, awk]
---

Bash arithmetic expansion does not support floats. Use `awk 'BEGIN { print (p >= 80) ? "yes" : "no" }'` for comparisons like percentage thresholds. Common when parsing JSON quota values (week_pct).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
