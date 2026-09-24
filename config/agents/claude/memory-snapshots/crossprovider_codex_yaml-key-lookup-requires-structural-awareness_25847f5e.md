---
name: crossprovider codex yaml-key-lookup-requires-structural-awareness
description: YAML key lookup requires structural awareness
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [yaml, grep, tooling-quirk]
---

Grep patterns can miss indented keys under parent maps in YAML (e.g., `workflows:` map in Deckhand routing). Use structural parsing or expanded context when searching YAML; exact-line grep is not reliable for nested structures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
