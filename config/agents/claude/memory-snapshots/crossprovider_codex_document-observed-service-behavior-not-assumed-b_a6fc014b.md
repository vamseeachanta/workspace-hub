---
name: crossprovider codex document-observed-service-behavior-not-assumed-b
description: Document observed service behavior, not assumed behavior in infrastructure docs
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [documentation, operations, correctness, infrastructure]
---

Handoff/operational documentation should describe actual implementation behavior (e.g., 'always kills and relaunches x11vnc to ensure fresh auth'), not assumed behavior (e.g., 'starts only if missing'). Validate against current code before publishing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
