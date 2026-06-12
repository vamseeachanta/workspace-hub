---
name: crossprovider codex yaml-multi-line-fields-fail-when-parsed-with-bas
description: YAML multi-line fields fail when parsed with bash regex
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [data-integrity, bash-limits, yaml]
---

Regex-based field extraction in shell scripts (e.g., `get_value "blocked_by"`) cannot handle YAML lists: `blocked_by: [WRK-1, WRK-2]` or multi-line YAML syntax becomes empty or truncated. Causes data corruption (blocking state misreported). Use proper YAML parser in Python inline block or accept field flattening (single-value scalar fields only).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
