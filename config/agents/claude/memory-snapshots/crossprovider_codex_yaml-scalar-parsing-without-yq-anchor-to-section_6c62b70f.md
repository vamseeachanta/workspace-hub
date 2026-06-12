---
name: crossprovider codex yaml-scalar-parsing-without-yq-anchor-to-section
description: YAML scalar parsing without yq: anchor to section header
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [bash, yaml-parsing, no-external-deps]
---

Find agent block header line with grep -n, then sed the next N lines to extract key:value pairs. More robust than naive grep across whole file. Pattern: sed -n "$(header_line + 1),$(header_line + 5)p" | grep '^[[:space:]]+key:'.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
