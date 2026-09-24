---
name: crossprovider gemini yaml-mutation-in-bash-requires-proper-parsers-no
description: YAML mutation in bash requires proper parsers, not sed
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [bash, yaml, robustness, anti-pattern]
---

Raw sed for YAML frontmatter mutation is fragile and breaks on missing frontmatter, malformed YAML, or existing keys. Use yq or Python inline scripts for safe YAML reading/writing with edge-case handling.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
