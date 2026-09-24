---
name: crossprovider gemini yaml-scalar-extraction-without-yq-grep-header-bo
description: YAML scalar extraction without yq: grep header + bounded read
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [yaml, bash, parsing, no-deps]
---

Find agent block header with `grep -n "^${agent}:"`, then read 5 lines after to grep for key. Example: `sed -n "$((line+1)),$((line+5))p" file | grep "  key:"`. Avoids yq dependency; works for flat key-value pairs under agent sections.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
