---
name: crossprovider codex json-generator-script-as-canonical-source-for-ge
description: JSON + generator script as canonical source for generated artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-integrity, artifact-generation]
---

When markdown reports or other text artifacts are generated from JSON data via a script, treat the JSON source file and generator script as canonical, not the markdown. Manual edits to markdown diverge from JSON; regeneration through the script preserves data integrity and prevents report drift.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
