---
name: crossprovider gemini yaml-key-lookup-without-yq-needs-section-header-
description: YAML key lookup without yq needs section-header anchoring to avoid false positives
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [bash, yaml, parsing-pattern]
---

When parsing YAML with grep/sed alone, anchor to the section header (e.g., grep -n '^agent:' first, then read next N lines). Naive grepping for 'cli_min:' matches unrelated keys in other sections. Header-anchoring prevents shadowing and cross-section pollution.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
