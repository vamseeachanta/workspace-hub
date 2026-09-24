---
name: crossprovider codex script-detection-via-grep-alone-misses-valid-inv
description: Script detection via grep alone misses valid invocation patterns
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [script-detection, validation, grep-hazards]
---

Grepping for only `bash scripts/` or `uv run` misses legitimate patterns like frontmatter `scripts:` entries and other reference styles already in the corpus. Detection logic must enumerate corpus-wide patterns or use schema-aware parsing, not grep heuristics alone.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
