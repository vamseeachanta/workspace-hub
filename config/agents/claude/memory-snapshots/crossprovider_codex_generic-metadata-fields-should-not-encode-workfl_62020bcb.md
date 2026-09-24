---
name: crossprovider codex generic-metadata-fields-should-not-encode-workfl
description: Generic metadata fields should not encode workflow state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, overloading, state-management]
---

Using `note:` as a signal for parked/stalled work (present = parked, absent = active) will cause false positives when that field is used for its intended generic purpose. Codex flagged this in WRK-1125: the queue schema already uses `note` for informational context in pending items, so overloading it as a state flag is unstable. Use explicit fields like `state_hint`, `parked_reason`, or dedicated frontmatter keys.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
