---
name: crossprovider codex gate-validators-must-enforce-semantic-completene
description: Gate validators must enforce semantic completeness, not just field presence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, gates, logic-error]
---

Presence checks alone allow false-positives (e.g., self-references in future-work lists without real follow-up work, or status=unknown treated as OK instead of WARN). Hard gates need explicit policy for borderline states and validation of content shape, not just existence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
