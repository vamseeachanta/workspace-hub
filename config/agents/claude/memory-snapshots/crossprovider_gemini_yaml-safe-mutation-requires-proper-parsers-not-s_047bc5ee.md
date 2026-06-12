---
name: crossprovider gemini yaml-safe-mutation-requires-proper-parsers-not-s
description: YAML-safe mutation requires proper parsers, not sed
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [yaml-safety, parallel-agents, frontmatter-mutation]
---

Never use raw sed to mutate YAML frontmatter. Use yq or Python inline YAML parsing instead. Parallel agents race-corrupt sed-based mutations; proper parsers handle edge cases (missing frontmatter, malformed YAML, pre-existing keys) safely. Critical for multi-agent batch updates to WRK files.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
