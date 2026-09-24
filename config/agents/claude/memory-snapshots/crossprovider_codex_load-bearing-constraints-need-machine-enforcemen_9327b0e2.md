---
name: crossprovider codex load-bearing-constraints-need-machine-enforcemen
description: Load-bearing constraints need machine enforcement, not prose
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement, drift-prevention, process, validation]
---

Constraints that span multiple files (enums, dependencies, formats) should be validated via regex, schema validators, or code checks at commit time. Prose-only constraints are discovered late at review and vulnerable to silent drift. Example: coordination validator only checked phrase presence, not exact enum membership.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
